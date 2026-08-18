"""Renderer for the local documentation index."""

from __future__ import annotations

from html import escape
from importlib.resources import files


class IndexRenderer:
    def __init__(self) -> None:
        self.template = files("local_docs").joinpath("templates/index.html").read_text(
            encoding="utf-8"
        )

    def render(self, sites: list[str], port: int) -> str:
        rows = []
        for site in sorted(sites):
            safe_site = escape(site)
            url = f"http://{safe_site}:{port}"
            rows.append(
                "<tr>"
                f"<td><strong>{safe_site}</strong></td>"
                '<td><span class="status-badge">Активен</span></td>'
                f'<td><a href="{escape(url, quote=True)}" target="_blank" '
                'class="site-link">Открыть сайт</a></td>'
                "</tr>"
            )
        return self.template.replace("<!-- SITES_ROWS_PLACEHOLDER -->", "\n".join(rows))
