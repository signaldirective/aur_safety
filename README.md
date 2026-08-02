# aur_safety

[![aur_safety demo](https://img.youtube.com/vi/E0i1_9jwNZA/0.jpg)](https://youtu.be/E0i1_9jwNZA)

**aur_safety** is a drop-in wrapper for `yay`, `pacaur`, and `paru` that annotates search results and blocks dangerous installs by cross-referencing known-compromised AUR packages.

It checks every package against multiple curated blocklists sourced from the June 2026 `atomic-lockfile`/`js-digest` supply-chain attack, the 2025 CHAOS RAT campaign, the Russian spam injection campaign, the July 2026 ELF dropper / AUR package takeover wave, and associated malicious npm dependencies.

## Features

- **`aur_safety find <search>`** — runs `<helper> -Ss` and marks known-bad packages with a red `(unsafe)` tag
- **`aur_safety install <package>`** — runs `<helper> -S` but warns and prompts for confirmation before installing any package on the blocklist (default answer is no)
- **`aur_safety update-lists`** — checks all package lists against the latest versions on GitHub and downloads any updates
- **`aur_safety config`** — view or change your AUR helper (yay, pacaur, or paru)

## aur_safety_api — self-updating version

`aur_safety_api` is an experimental variant that keeps its blocklists up to date automatically, so end users never have to run `update-lists`:

- Each list file carries a `# version: N` header; the repo's tiny `lists.json` manifest records every list's current revision + sha256.
- On every `find`/`install` (at most once per 6h — override with `AUR_SAFETY_UPDATE_TTL`, in seconds), `aur_safety_api` downloads `lists.json`, compares revisions against the local headers, and silently updates any stale lists. If GitHub is unreachable it falls back to the local lists and continues.
- The lists themselves are maintained by a collector service (`tools/update_lists.py`, scheduled via the provided systemd timer) that polls the aur-audit API for confirmed-malicious packages, merges them into the blocklists, bumps the versions, and pushes to GitHub.

Install it alongside the classic version (it does not overwrite `aur_safety`):

```bash
./install_api.sh            # installs aur_safety_api
./install-service.sh        # optional: run the list collector every 6h
```

The collector requires an SSH deploy key at `~/.ssh/aur_safety_deploy` with push access to this repo (or edit `GIT_SSH_COMMAND` in the generated unit). Run it once manually to sanity-check:

```bash
python3 tools/update_lists.py --dry-run
```

## Install

```bash
git clone https://github.com/signaldirective/aur_safety.git
cd aur_safety
./install.sh
```

This copies the blocklists to `~/.config/aur_safety/` and installs the `aur_safety` command to `~/.local/bin/`. Make sure `~/.local/bin/` is in your `PATH`.

On first run, `aur_safety` will ask which AUR helper you use (`yay`, `pacaur`, or `paru`). You can change it later with `aur_safety config <helper>`.

## Package Lists

| File | Source |
|---|---|
| `package_list.txt` | June 2026 AUR supply-chain attack (~1935 packages, consolidated from mailing list, IRC, and community reports) |
| `chaos_rat_packages.txt` | 2025 CHAOS RAT trojan campaign |
| `malicious_npm_packages.txt` | Malicious npm packages used as payload droppers (`atomic-lockfile`, `js-digest`, etc.) |
| `malicious_russian_spam_packages.txt` | Russian spam injection campaign (~80 packages) |
| `malicious_elf_dropper_packages.txt` | July 2026 ELF dropper / package takeover wave (~87 packages, sourced from the aur-audit blacklist and AUR mailing list reports) |

Lists are updated as new threats are reported. Pull requests welcome.

## License

MIT

---

If you find this useful, consider buying me a coffee:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/signaldirective)
