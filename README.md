# aur_safety

[![aur_safety demo](https://img.youtube.com/vi/15DIgdqSpFM/maxresdefault.jpg)](https://youtu.be/15DIgdqSpFM)

**aur_safety** is a drop-in wrapper for `yay`, `pacaur`, and `paru` that annotates search results and blocks dangerous installs by cross-referencing known-compromised AUR packages.

It checks every package against multiple curated blocklists sourced from the June 2026 `atomic-lockfile`/`js-digest` supply-chain attack, the 2025 CHAOS RAT campaign, the Russian spam injection campaign, and associated malicious npm dependencies.

## Features

- **`aur_safety find <search>`** — runs `<helper> -Ss` and annotates each result with a green `(safe)` or red `(unsafe)` tag
- **`aur_safety install <package>`** — runs `<helper> -S` but warns and prompts for confirmation before installing any package on the blocklist (default answer is no)
- **`aur_safety update-lists`** — checks all package lists against the latest versions on GitHub and downloads any updates
- **`aur_safety config`** — view or change your AUR helper (yay, pacaur, or paru)

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

Lists are updated as new threats are reported. Pull requests welcome.

## License

MIT

---

If you find this useful, consider buying me a coffee:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/signaldirective)
