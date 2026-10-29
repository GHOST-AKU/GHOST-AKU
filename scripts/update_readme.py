#!/usr/bin/env python3
"""Refresh only the GitHub-native Markdown telemetry region.

Uses public GitHub API data, without third-party badges or images.
Does not touch the README unless displayed statistics actually change.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

USER = "GHOST-AKU"
README = Path(__file__).resolve().parents[1] / "README.md"
START = "<!-- AUTO_STATS:START -->"
END = "<!-- AUTO_STATS:END -->"


def github_api(path: str) -> object:
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GHOST-AKU-markdown-profile",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request("https://api.github.com" + path, headers=headers)
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)


def public_repositories() -> list[dict]:
    repositories: list[dict] = []
    for page in range(1, 21):
        batch = github_api(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise RuntimeError("Unexpected GitHub API response")
        repositories.extend(repo for repo in batch if isinstance(repo, dict) and not repo.get("private", False))
        if len(batch) < 100:
            break
    if not repositories:
        raise RuntimeError("No public repositories returned; preserving existing README")
    return repositories


def telemetry_table(repositories: list[dict]) -> str:
    # The profile repo is included in the total, but excluded from latest push
    # so that periodic automation does not continually report its own commits.
    candidates = [r for r in repositories if r.get("name", "").lower() != USER.lower()]
    if not candidates:
        latest_cell = "—"
    else:
        latest = max(candidates, key=lambda r: r.get("pushed_at") or "")
        name = str(latest.get("name") or "unknown")
        date = str(latest.get("pushed_at") or "")[:10] or "unknown"
        url = "https://github.com/" + urllib.parse.quote(USER, safe="") + "/" + urllib.parse.quote(name, safe="")
        # Repository names cannot contain spaces, pipes, or backticks on GitHub.
        latest_cell = f"[`{name}`]({url}) · `{date}`"

    stars = sum(int(repo.get("stargazers_count") or 0) for repo in repositories)
    return (
        "| PUBLIC REPOS | STARS RECEIVED | LATEST PUBLIC PUSH |\n"
        "| :---: | :---: | :--- |\n"
        f"| **{len(repositories)}** | **{stars}** | {latest_cell} |"
    )


def replace_region(original: str, content: str) -> str:
    pattern = re.compile(re.escape(START) + r"\n.*?\n" + re.escape(END), re.DOTALL)
    if len(pattern.findall(original)) != 1:
        raise RuntimeError("README telemetry markers missing or duplicated")
    return pattern.sub(lambda _: START + "\n" + content + "\n" + END, original)


def main() -> int:
    try:
        repos = public_repositories()
        before = README.read_text(encoding="utf-8")
        after = replace_region(before, telemetry_table(repos))
    except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
        print(f"Telemetry update failed, README preserved: {exc}")
        return 1

    if after == before:
        print("No meaningful telemetry change; README left untouched")
        return 0
    README.write_text(after, encoding="utf-8")
    print("Updated README telemetry (public information only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
