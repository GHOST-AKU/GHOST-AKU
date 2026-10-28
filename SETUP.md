# GHOST-AKU Pixel Profile — Installation & customization

## 30-second installation

1. On GitHub create a **public** repository named `GHOST-AKU` in your `GHOST-AKU` account. This special repo's root `README.md` appears on your GitHub profile. If it already exists, add/merge these files instead.
2. Upload all files from this pack, **preserving the folder structure and dot directories**. Do not upload the ZIP as one file.
3. Go to the repo's **Actions** tab and run `Refresh pixel telemetry` with **Run workflow** once. The job tries again every 6 hours (UTC).
4. If Actions does not push: in repository **Settings → Actions → General → Workflow permissions**, confirm write permission is allowed, and check branch protection/rulesets. The workflow explicitly requests `contents: write` but rules can still prevent the push.

## How it moves

- `assets/hero.gif`: original hand-made animated pixel city, moon, character, drone, blinking neon, quest progress. It loops without JavaScript.
- `assets/worlds.gif`: three rotating project selections.
- `assets/continue.gif`: looping footer prompt.
- `assets/live-status.svg`: original bitmap-font SVG showing **public repo count**, summed stars received by public owned repositories, and **latest public repository push** (not total contributions and not necessarily the latest individual commit).
- `.github/workflows/live-status.yml`: attempts to update the SVG every six hours and commits only if there is a diff. GitHub can delay scheduled workflows; README image caches can also lag.

No third-party statistics website, remote image host, or user-supplied personal access token is needed. The workflow uses the repository's automatic `GITHUB_TOKEN`.

## Customizing

- Modify text, links and ordering in `README.md`.
- Modify pixel art and animation timing in `scripts/generate_assets.py`, then run `python -m pip install Pillow` and `python scripts/generate_assets.py` (Pillow >=10 recommended). The generator expects DejaVu Sans Mono on Linux, but uses fallback fonts if absent. The generated GIF assets are included so regeneration is optional.
- Change `USER = 'GHOST-AKU'` in `scripts/update_status.py` only if adapting the pack to another account.
- To remove automated updates, delete the `.github/workflows/live-status.yml` file and keep the fallback `live-status.svg`, or remove that panel entirely.
- Run `python scripts/update_status.py --offline` to rebuild a placeholder **without** querying GitHub. This overwrites the last live status; do not run it after a successful sync unless resetting deliberately.
- Original GIFs are self-contained; no JavaScript, external image downloads, or external font links.

## Compatibility

GitHub profile README files must be in a **public username-matching repository**. GitHub supports GIFs and image references in Markdown; it does not support running arbitrary JavaScript inside README. GIFs are designed to loop, but animations may be paused in reduced-motion or client-specific experiences. An SVG gets redrawn by Actions, not updated every second in the viewer's browser.

## Files

```text
GHOST-AKU/
├── README.md
├── SETUP.md
├── assets/
│   ├── hero.gif
│   ├── worlds.gif
│   ├── continue.gif
│   └── live-status.svg
├── scripts/
│   ├── generate_assets.py
│   └── update_status.py
└── .github/
    └── workflows/
        └── live-status.yml
```
