#!/usr/bin/env python3
"""Generate a fixed landing page for another post from an original xg.pasch.fan share_item HTML.

Usage: python3 make_page.py original-ep3833.html > ep3833.html

Reads og:title / og:url / og:image and target_id/view_key from the original page and substitutes
them into index.html (which holds the target_id=3846 example values).
"""
import html
import json
import re
import sys
from pathlib import Path

SUFFIX = " / XG OFFICIAL FANCLUB「ALPHAZ」"
HERE = Path(__file__).resolve().parent

# Example values baked into index.html
EX = {
    "title": "MAYA｜World tour finished!!🥺❤️",
    "url": "https://xg.pasch.fan/share_item?type=post&id=d05c68c0-d7a8-4434-8c00-211021e1534f&lang=en",
    "image": "https://d2v1fabzb8kzzn.cloudfront.net/post/20261121/ddb726d22ac748fc825d253f44f382be.jpg",
    "target_id": "3846",
    "view_key": "BD",
}


def meta(src, prop):
    m = re.search(r'<meta\s+(?:property|name)="%s"\s+content="([^"]*)"' % re.escape(prop), src)
    return html.unescape(m.group(1)) if m else None


def main():
    src = Path(sys.argv[1]).read_text(encoding="utf-8")
    title = meta(src, "og:title") or ""
    if title.endswith(SUFFIX):
        title = title[: -len(SUFFIX)]
    link = re.search(r"xg-twitter-login://view\?view_key=(\w+)&(?:amp;)?target_id=(\d+)", src)
    new = {
        "title": title,
        "url": meta(src, "og:url"),
        "image": meta(src, "og:image"),
        "view_key": link.group(1),
        "target_id": link.group(2),
    }

    out = (HERE / "index.html").read_text(encoding="utf-8")
    # Order matters: JSON block first (raw JSON strings), then HTML-escaped occurrences.
    out = re.sub(
        r'(<script type="application/json" id="post-data">).*?(</script>)',
        lambda m: m.group(1) + "\n" + json.dumps(
            {k: new[k] for k in ("title", "image", "view_key", "target_id")},
            ensure_ascii=False, indent=2).replace("</", "<\\/") + "\n" + m.group(2),
        out, count=1, flags=re.S,
    )
    for k in ("url", "image", "title"):
        out = out.replace(EX[k], html.escape(new[k], quote=True))
    out = out.replace("view_key=BD&amp;target_id=3846",
                      "view_key=%s&amp;target_id=%s" % (new["view_key"], new["target_id"]))
    sys.stdout.write(out)


if __name__ == "__main__":
    main()
