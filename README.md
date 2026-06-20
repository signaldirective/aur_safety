# aur_safety

**aur_safety** is a drop-in wrapper for `yay` that annotates search results and blocks dangerous installs by cross-referencing known-compromised AUR packages.

It checks every package against multiple curated blocklists sourced from the June 2026 `atomic-lockfile`/`js-digest` supply-chain attack, the 2025 CHAOS RAT campaign, the Russian spam injection campaign, and associated malicious npm dependencies.

## Features

- **`aur_safety find <search>`** — runs `yay -Ss` and annotates each result with a green `(safe)` or red `(unsafe)` tag
- **`aur_safety install <package>`** — runs `yay -S` but warns and prompts for confirmation before installing any package on the blocklist (default answer is no)

## Install

```bash
git clone https://github.com/your-username/aur_safety.git
cd aur_safety
./install.sh
```

This copies the blocklists to `~/.config/aur_safety/` and installs the `aur_safety` command to `~/.local/bin/`. Make sure `~/.local/bin/` is in your `PATH`.

## Package Lists

| File | Source |
|---|---|
| `package_list.txt` | June 2026 AUR supply-chain attack (~1935 packages, consolidated from mailing list, IRC, and community reports) |
| `chaos_rat_packages.txt` | 2025 CHAOS RAT trojan campaign |
| `malicious_npm_packages.txt` | Malicious npm packages used as payload droppers (`atomic-lockfile`, `js-digest`, etc.) |
| `malicious_russian_spam_packages.txt` | Russian spam injection campaign (~80 packages) |

Lists are updated as new threats are reported. Pull requests welcome.

## License

MIT

---

If you find this useful, consider buying me a coffee:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/signaldirective)
