#!/usr/bin/env python3
"""Fetch, fingerprint, and archive official documentation for expert profiles."""

from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


MAX_BYTES = 512 * 1024
MAX_EXCERPT_CHARS = 6_000
URL_PATTERN = re.compile(r"https://[^\s)>]+")


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.capture = False
        self.parts: list[str] = []
        self.title = ""
        self.current_tag = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.current_tag = tag
        self.capture = tag in {"title", "h1", "h2", "h3", "p", "li"}

    def handle_endtag(self, tag: str) -> None:
        if tag == self.current_tag:
            self.capture = False
            self.current_tag = ""

    def handle_data(self, data: str) -> None:
        if not self.capture:
            return
        cleaned = " ".join(html.unescape(data).split())
        if not cleaned:
            return
        if self.current_tag == "title" and not self.title:
            self.title = cleaned
        self.parts.append(cleaned)


def profile_root() -> Path:
    script = Path(__file__).resolve()
    # /opt/data/profiles/<profile>/scripts/official-source-watch.py
    return script.parent.parent


def skill_sources(root: Path) -> Path:
    candidates = list((root / "skills" / "custom").glob("*/references/official-sources.md"))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected one expert source manifest, found {len(candidates)}")
    return candidates[0]


def fetch(url: str) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.5",
            "User-Agent": "sarl-agent-ai-official-source-watch/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = response.read(MAX_BYTES)
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type", "")
            modified = response.headers.get("Last-Modified", "")
            etag = response.headers.get("ETag", "")
        decoded = payload.decode("utf-8", errors="replace")
        extractor = TextExtractor()
        if "html" in content_type.lower() or "<html" in decoded[:1000].lower():
            extractor.feed(decoded)
            excerpt = "\n".join(extractor.parts)[:MAX_EXCERPT_CHARS]
            title = extractor.title
        else:
            excerpt = decoded[:MAX_EXCERPT_CHARS]
            title = ""
        return {
            "ok": True,
            "url": url,
            "final_url": final_url,
            "title": title,
            "content_type": content_type,
            "last_modified": modified,
            "etag": etag,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes_sampled": len(payload),
            "excerpt": excerpt,
        }
    except (OSError, urllib.error.URLError, ValueError) as error:
        return {
            "ok": False,
            "url": url,
            "error": f"{type(error).__name__}: {error}",
        }


def main() -> int:
    root = profile_root()
    profile = root.name
    manifest = skill_sources(root)
    urls = list(dict.fromkeys(URL_PATTERN.findall(manifest.read_text(encoding="utf-8"))))
    if not urls:
        raise RuntimeError(f"No HTTPS sources found in {manifest}")

    knowledge = root / "knowledge"
    reports = knowledge / "official-research"
    reports.mkdir(parents=True, exist_ok=True)
    state_path = knowledge / "source-state.json"
    previous = {}
    if state_path.is_file():
        try:
            previous = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            previous = {}

    checked_at = datetime.now(timezone.utc)
    results = [fetch(url) for url in urls]
    changed = []
    failed = []
    for result in results:
        url = str(result["url"])
        if not result.get("ok"):
            failed.append(url)
            continue
        old_hash = previous.get(url, {}).get("sha256")
        result["changed"] = old_hash is not None and old_hash != result.get("sha256")
        result["first_seen"] = old_hash is None
        if result["changed"]:
            changed.append(url)

    state = {
        str(result["url"]): {
            "sha256": result.get("sha256"),
            "checked_at": checked_at.isoformat(),
            "title": result.get("title"),
            "final_url": result.get("final_url"),
        }
        for result in results
        if result.get("ok")
    }
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        f"# Veille officielle — {profile}",
        "",
        f"- Vérification UTC: {checked_at.isoformat()}",
        f"- Manifest: `{manifest}`",
        f"- Sources: {len(results)}",
        f"- Changements détectés: {len(changed)}",
        f"- Échecs: {len(failed)}",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"## {result.get('title') or result['url']}",
                "",
                f"- URL: {result['url']}",
                f"- URL finale: {result.get('final_url', '')}",
                f"- Statut: {'OK' if result.get('ok') else 'ECHEC'}",
                f"- SHA-256 échantillon: {result.get('sha256', '')}",
                f"- Modifié: {result.get('last_modified', '')}",
                f"- ETag: {result.get('etag', '')}",
                f"- Changement: {result.get('changed', False)}",
                f"- Première observation: {result.get('first_seen', False)}",
            ]
        )
        if result.get("error"):
            lines.append(f"- Erreur: {result['error']}")
        excerpt = str(result.get("excerpt") or "").strip()
        if excerpt:
            lines.extend(["", "### Extrait indexé", "", excerpt])
        lines.append("")

    stamp = checked_at.strftime("%Y-%m-%dT%H%M%SZ")
    report_path = reports / f"{stamp}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    status_lines = [
        f"# État des sources officielles — {profile}",
        "",
        f"Dernière vérification: {checked_at.isoformat()}",
        f"Rapport: `{report_path}`",
        "",
        "| Source | Statut | Changement | Titre |",
        "|---|---|---|---|",
    ]
    for result in results:
        status_lines.append(
            "| {url} | {status} | {changed} | {title} |".format(
                url=result["url"],
                status="OK" if result.get("ok") else "ECHEC",
                changed=result.get("changed", False),
                title=str(result.get("title") or "").replace("|", "/"),
            )
        )
    (knowledge / "SOURCE_STATUS.md").write_text(
        "\n".join(status_lines) + "\n",
        encoding="utf-8",
    )

    print(f"OFFICIAL_SOURCE_WATCH profile={profile}")
    print(f"sources={len(results)} changed={len(changed)} failed={len(failed)}")
    print(f"report={report_path}")
    if changed:
        print("changes:")
        for url in changed:
            print(f"- {url}")
    if failed:
        print("failed:")
        for url in failed:
            print(f"- {url}")
        print("VERDICT=SUPERVISION_REQUISE")
    else:
        print("VERDICT=OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"OFFICIAL_SOURCE_WATCH_ERROR={type(error).__name__}: {error}")
        print("VERDICT=SUPERVISION_REQUISE")
        raise SystemExit(0)
