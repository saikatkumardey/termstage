"""Pure Python SVG generation for termsvg (static rendering)."""

from __future__ import annotations

import html
from typing import Any

from .themes import (
    COMMENT_COLOR,
    FONT_FAMILY,
    FONT_SIZE,
    LINE_HEIGHT,
    OUTPUT_COLOR,
    PADDING,
    THEMES,
    TITLE_BAR_HEIGHT,
)


def _escape(text: str) -> str:
    """HTML-escape text for safe SVG embedding."""
    return html.escape(text, quote=True)


def _count_lines(steps: list[dict]) -> int:
    """Count total rendered lines across all steps."""
    total = 0
    for i, step in enumerate(steps):
        if "comment" in step:
            total += 1
        elif "cmd" in step:
            total += 1  # prompt + cmd line
            output = step.get("output", "")
            if output:
                total += len(output.rstrip("\n").split("\n"))
        # blank line gap between steps (not after last)
        if i < len(steps) - 1:
            total += 1
    return total


def _render_title_bar(width: int, title: str, theme: dict) -> str:
    """Render the macOS-style title bar."""
    bar_y = 0
    dots_y = TITLE_BAR_HEIGHT // 2

    dots_html = ""
    if theme.get("dots", True):
        dot_colors = ["#ff5f57", "#febc2e", "#28c840"]
        dot_x_start = 16
        dot_spacing = 20
        for i, color in enumerate(dot_colors):
            cx = dot_x_start + i * dot_spacing
            dots_html += (
                f'<circle cx="{cx}" cy="{dots_y}" r="6" fill="{color}" />\n    '
            )

    title_x = width // 2
    title_svg = (
        f'<text x="{title_x}" y="{dots_y + 5}" '
        f'font-family={FONT_FAMILY!r} font-size="13" '
        f'fill="{theme["text"]}" opacity="0.7" '
        f'text-anchor="middle" dominant-baseline="middle">'
        f"{_escape(title)}</text>"
    )

    return f"""    <!-- Title bar -->
    <rect x="0" y="{bar_y}" width="{width}" height="{TITLE_BAR_HEIGHT}"
          rx="8" ry="8" fill="{theme['title_bar']}" />
    <!-- Fake bottom corners for title bar -->
    <rect x="0" y="{TITLE_BAR_HEIGHT - 8}" width="{width}" height="8"
          fill="{theme['title_bar']}" />
    {dots_html}{title_svg}"""


def render_svg(config: dict[str, Any]) -> str:
    """
    Render a static SVG terminal window from config dict.

    config keys:
      title, theme, prompt, width, steps
    """
    title = config.get("title", "termsvg demo")
    theme_name = config.get("theme", "dark")
    prompt = config.get("prompt", "$ ")
    width = int(config.get("width", 700))
    steps = config.get("steps", [])

    theme = THEMES.get(theme_name, THEMES["dark"])

    # Calculate height
    n_lines = _count_lines(steps)
    body_height = PADDING + n_lines * LINE_HEIGHT + PADDING
    total_height = TITLE_BAR_HEIGHT + body_height

    lines_svg = []
    y = TITLE_BAR_HEIGHT + PADDING + LINE_HEIGHT  # baseline y of first line

    for i, step in enumerate(steps):
        if "comment" in step:
            comment_text = step["comment"]
            lines_svg.append(
                f'    <text x="{PADDING}" y="{y}" '
                f'font-family={FONT_FAMILY!r} font-size="{FONT_SIZE}" '
                f'fill="{COMMENT_COLOR}" xml:space="preserve">'
                f"{_escape(comment_text)}</text>"
            )
            y += LINE_HEIGHT

        elif "cmd" in step:
            cmd = step["cmd"]
            output = step.get("output", "")

            # Render prompt + command on same line using tspan
            lines_svg.append(
                f'    <text x="{PADDING}" y="{y}" '
                f'font-family={FONT_FAMILY!r} font-size="{FONT_SIZE}" '
                f'xml:space="preserve">'
                f'<tspan fill="{theme["prompt"]}">{_escape(prompt)}</tspan>'
                f'<tspan fill="{theme["text"]}">{_escape(cmd)}</tspan>'
                f"</text>"
            )
            y += LINE_HEIGHT

            if output:
                for line in output.rstrip("\n").split("\n"):
                    lines_svg.append(
                        f'    <text x="{PADDING}" y="{y}" '
                        f'font-family={FONT_FAMILY!r} font-size="{FONT_SIZE}" '
                        f'fill="{OUTPUT_COLOR}" xml:space="preserve">'
                        f"{_escape(line)}</text>"
                    )
                    y += LINE_HEIGHT

        # blank gap between steps
        if i < len(steps) - 1:
            y += LINE_HEIGHT

    title_bar_svg = _render_title_bar(width, title, theme)
    lines_joined = "\n".join(lines_svg)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}" height="{total_height}"
     viewBox="0 0 {width} {total_height}">
  <!-- Window frame -->
  <rect x="0" y="0" width="{width}" height="{total_height}"
        rx="8" ry="8" fill="{theme['bg']}" />
{title_bar_svg}
  <!-- Terminal body -->
  <clipPath id="body-clip">
    <rect x="0" y="{TITLE_BAR_HEIGHT}" width="{width}" height="{body_height}"
          rx="0" ry="0" />
  </clipPath>
  <g clip-path="url(#body-clip)">
{lines_joined}
  </g>
</svg>
"""
    return svg
