#!/usr/bin/env python3
"""aur_safety malicious-package list collector.

Polls machine-readable sources, merges confirmed ("black") package names into
the campaign lists, bumps the per-file `# version: N` header, regenerates
`lists.json`, and pushes the result to GitHub so that aur_safety_api clients
self-update.

Run it periodically (see systemd/aur-safety-lists.timer). It is safe to run
unattended: sources are unioned into the existing lists (nothing is ever
removed), and git operations use `pull --rebase` before pushing.

Exit codes:
  0 - success (or nothing to do)
  1 - one or more sources could not be fetched (partial update may still push)
  2 - git operation failed
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BRANCH = "main"
GIT_SSH_URL = os.environ.get(
    "AUR_SAFETY_PUSH_URL", "git@github.com:signaldirective/aur_safety.git"
)

LIST_FILES = [
    "package_list.txt",
    "chaos_rat_packages.txt",
    "malicious_npm_packages.txt",
    "malicious_russian_spam_packages.txt",
    "malicious_elf_dropper_packages.txt",
]

VERSION_RE = re.compile(r"^#\s*version:\s*(\d+)$")

SOURCES = [
    {
        "name": "aur-audit blacklist",
        "url": "https://aur-audit.wtako.net/packages?filter=black&limit=500",
        "target": "malicious_elf_dropper_packages.txt",
        "paginate": True,
    },
]


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def fetch_source_names(src):
    names = set()
    url = src["url"]
    while True:
        data = fetch_json(url)
        for pkg in data.get("packages", []):
            name = pkg.get("packageName")
            if name:
                names.add(name)
        nxt = data.get("nextCursor")
        if src.get("paginate") and nxt:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}before={nxt}"
            time.sleep(0.3)
        else:
            break
    return names


def load_list(path):
    header = []
    entries = set()
    version = 0
    try:
        lines = path.read_text().splitlines()
    except FileNotFoundError:
        lines = []
    for line in lines:
        m = VERSION_RE.match(line)
        if m:
            version = int(m.group(1))
            header.append(line)
        elif line.startswith("#"):
            header.append(line)
        elif line.strip():
            entries.add(line.strip())
    return header, entries, version


def save_list(path, header, entries, version):
    out = []
    version_written = False
    for line in header:
        if VERSION_RE.match(line):
            out.append(f"# version: {version}")
            version_written = True
        else:
            out.append(line)
    if not version_written:
        out.append(f"# version: {version}")
    out.extend(sorted(entries))
    path.write_text("\n".join(out) + "\n")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read_version(path):
    for line in path.read_text().splitlines():
        m = VERSION_RE.match(line)
        if m:
            return int(m.group(1))
    return 0


def regenerate_manifest():
    files = {}
    for fname in LIST_FILES:
        p = REPO_ROOT / fname
        files[fname] = {
            "revision": read_version(p),
            "sha256": sha256_bytes(p.read_bytes()),
        }
    return {
        "version": max(e["revision"] for e in files.values()),
        "updated": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "files": files,
    }


def git(args, check=True):
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=check
    )


def push_changes(changed_files, manifest):
    tracked = [*changed_files, "lists.json"]

    # Stash only our modified files so pull --rebase can run on a clean tree.
    stash = git(
        ["stash", "push", "-m", "aur-safety-lists", "--", *tracked], check=False
    )
    if stash.returncode != 0 and "No local changes" not in (stash.stderr or ""):
        print(f"  git stash failed:\n{stash.stderr}", file=sys.stderr)

    pull = git(["pull", "--rebase", "origin", BRANCH], check=False)
    if pull.returncode != 0:
        print(f"  git pull --rebase failed:\n{pull.stderr}", file=sys.stderr)

    pop = git(["stash", "pop"], check=False)
    if pop.returncode != 0:
        print(f"  git stash pop failed (resolve manually):\n{pop.stderr}", file=sys.stderr)
        return False

    git(["add", *tracked])
    n = len(changed_files)
    git(["commit", "-m", f"lists: update {n} list(s) (revision {manifest['version']})"])

    push = subprocess.run(
        ["git", "push", GIT_SSH_URL, BRANCH],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if push.returncode != 0:
        print(f"  git push failed:\n{push.stderr}", file=sys.stderr)
        return False
    print(f"  Pushed to {GIT_SSH_URL}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="Fetch sources and show what would change without writing or pushing"
    )
    parser.add_argument(
        "--no-push", action="store_true", help="Write and commit changes locally but do not push"
    )
    parser.add_argument(
        "--skip-git", action="store_true", help="Update lists and manifest on disk only (no git at all)"
    )
    args = parser.parse_args()

    changed = []
    had_source_error = False

    for src in SOURCES:
        try:
            names = fetch_source_names(src)
        except Exception as e:  # network / json errors
            print(f"  ERROR: failed to fetch {src['name']}: {e}", file=sys.stderr)
            had_source_error = True
            continue

        target = REPO_ROOT / src["target"]
        header, entries, version = load_list(target)
        new_names = set(names) - entries

        if not new_names:
            print(f"  {src['target']}: up to date ({len(entries)} packages)")
            continue

        new_version = version + 1
        entries |= set(names)
        if not args.dry_run:
            save_list(target, header, entries, new_version)
        print(
            f"  {src['target']}: +{len(new_names)} new -> revision {new_version} "
            f"({len(entries)} total)"
        )
        changed.append(src["target"])

    if not changed:
        print("No changes.")
        return 1 if had_source_error else 0

    if args.dry_run:
        print(f"DRY-RUN: would update {len(changed)} list(s) and push to GitHub.")
        return 1 if had_source_error else 0

    manifest = regenerate_manifest()
    if not args.skip_git:
        if not args.dry_run:
            (REPO_ROOT / "lists.json").write_text(
                json.dumps(manifest, indent=2) + "\n"
            )

    if args.skip_git:
        print("Lists updated on disk (lists.json regenerated).")
        return 0
    if args.no_push:
        print(f"Lists committed locally ({len(changed)} changed), not pushed.")
        return 0

    ok = push_changes(changed, manifest)
    return 2 if not ok else (1 if had_source_error else 0)


if __name__ == "__main__":
    sys.exit(main())
