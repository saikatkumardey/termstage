"""CSS keyframe-based animated SVG generation for termstage."""

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


def _truncate(text: str, max_chars: int) -> str:
    """Truncate text with ellipsis if it exceeds max_chars."""
    if len(text) > max_chars:
        return text[: max_chars - 1] + "…"
    return text


def _max_chars(width: int) -> int:
    """Compute max characters per line that fit within the SVG width."""
    char_width = FONT_SIZE * 0.61
    return int((width - 2 * PADDING) / char_width)


# Characters per second for typing animation
CHARS_PER_SEC = 30
# Seconds for output fade-in
FADE_DURATION = 0.4
# Seconds pause after each step before next starts
STEP_PAUSE = 0.3
# Seconds to hold completed animation before looping
LOOP_PAUSE = 2.0


def _escape(text: str) -> str:
    return html.escape(text, quote=True)


def _count_lines(steps: list[dict]) -> int:
    total = 0
    for i, step in enumerate(steps):
        if "comment" in step:
            total += 1
        elif "cmd" in step:
            total += 1
            output = step.get("output", "")
            if output:
                total += len(output.rstrip("\n").split("\n"))
        if i < len(steps) - 1:
            total += 1
    return total


def _render_title_bar(width: int, title: str, theme: dict) -> str:
    dots_y = TITLE_BAR_HEIGHT // 2
    dots_html = ""
    if theme.get("dots", True):
        dot_colors = ["#ff5f57", "#febc2e", "#28c840"]
        dot_x_start = 16
        dot_spacing = 20
        for i, color in enumerate(dot_colors):
            cx = dot_x_start + i * dot_spacing
            dots_html += f'<circle cx="{cx}" cy="{dots_y}" r="6" fill="{color}" />\n    '

    title_x = width // 2
    title_svg = (
        f'<text x="{title_x}" y="{dots_y + 5}" '
        f'font-family={FONT_FAMILY!r} font-size="13" '
        f'fill="{theme["text"]}" opacity="0.7" '
        f'text-anchor="middle" dominant-baseline="middle">'
        f"{_escape(title)}</text>"
    )

    return f"""    <!-- Title bar -->
    <rect x="0" y="0" width="{width}" height="{TITLE_BAR_HEIGHT}"
          rx="8" ry="8" fill="{theme['title_bar']}" />
    <rect x="0" y="{TITLE_BAR_HEIGHT - 8}" width="{width}" height="8"
          fill="{theme['title_bar']}" />
    {dots_html}{title_svg}"""


# ---------------------------------------------------------------------------
# Looping keyframe generators
# All animations are infinite loops of duration `loop_dur` seconds.
# The typing/fade effect is encoded as percentage keyframes; the steps()
# timing function is set per-keyframe so it only applies to the typing phase.
# ---------------------------------------------------------------------------

def _pct(t: float, loop_dur: float) -> str:
    return f"{t / loop_dur * 100:.3f}%"


def _make_keyframes(
    anim_id: str, n_chars: int, start_s: float, duration_s: float, loop_dur: float
) -> str:
    """Typewriter clip-path animation, looping."""
    sp = _pct(start_s, loop_dur)
    ep = _pct(start_s + duration_s, loop_dur)
    steps_fn = f"steps({max(n_chars, 1)}, end)"

    return (
        f"  @keyframes type-{anim_id} {{\n"
        f"    0%    {{ clip-path: inset(0 100% 0 0); }}\n"
        f"    {sp}  {{ clip-path: inset(0 100% 0 0); animation-timing-function: {steps_fn}; }}\n"
        f"    {ep}  {{ clip-path: inset(0 -20px 0 0); }}\n"
        f"    99.9% {{ clip-path: inset(0 -20px 0 0); }}\n"
        f"    100%  {{ clip-path: inset(0 100% 0 0); }}\n"
        f"  }}\n"
        f"  .type-{anim_id} {{\n"
        f"    clip-path: inset(0 100% 0 0);\n"
        f"    animation: type-{anim_id} {loop_dur:.3f}s linear 0s infinite;\n"
        f"  }}\n"
    )


def _make_fade_keyframes(anim_id: str, start_s: float, loop_dur: float) -> str:
    """Fade-in animation, looping."""
    sp = _pct(start_s, loop_dur)
    ep = _pct(start_s + FADE_DURATION, loop_dur)

    return (
        f"  @keyframes fade-{anim_id} {{\n"
        f"    0%    {{ opacity: 0; }}\n"
        f"    {sp}  {{ opacity: 0; }}\n"
        f"    {ep}  {{ opacity: 1; }}\n"
        f"    99.9% {{ opacity: 1; }}\n"
        f"    100%  {{ opacity: 0; }}\n"
        f"  }}\n"
        f"  .fade-{anim_id} {{\n"
        f"    opacity: 0;\n"
        f"    animation: fade-{anim_id} {loop_dur:.3f}s linear 0s infinite;\n"
        f"  }}\n"
    )


def _make_cursor_keyframes(
    anim_id: str, start_s: float, end_s: float, loop_dur: float
) -> str:
    """Blinking cursor: visible during typing, hidden otherwise."""
    sp = _pct(start_s, loop_dur)
    ep = _pct(end_s, loop_dur)
    # tiny nudge so two keyframes at same pct don't collapse
    sp_plus = f"{(start_s + 0.001) / loop_dur * 100:.4f}%"

    return (
        f"  @keyframes cursor-{anim_id} {{\n"
        f"    0%, {sp} {{ opacity: 0; }}\n"
        f"    {sp_plus} {{ opacity: 1; animation-timing-function: steps(1, end); }}\n"
        f"    {ep}      {{ opacity: 0; }}\n"
        f"    100%       {{ opacity: 0; }}\n"
        f"  }}\n"
        f"  .cursor-{anim_id} {{\n"
        f"    opacity: 0;\n"
        f"    animation: cursor-{anim_id} {loop_dur:.3f}s linear 0s infinite;\n"
        f"  }}\n"
    )


def render_animated_svg(config: dict[str, Any]) -> str:
    """
    Render an animated SVG terminal window from config dict.
    Uses CSS @keyframes for typewriter + fade-in effects. No JS.
    Animations loop indefinitely with a pause between iterations.
    """
    title = config.get("title", "termstage demo")
    theme_name = config.get("theme", "dark")
    prompt = config.get("prompt", "$ ")
    width = int(config.get("width", 700))
    steps = config.get("steps", [])

    theme = THEMES.get(theme_name, THEMES["dark"])
    max_chars = _max_chars(width)
    char_width = FONT_SIZE * 0.61

    # ------------------------------------------------------------------
    # Pass 1: compute timing for every step
    # ------------------------------------------------------------------
    timed: list[dict] = []  # enriched step records
    time_cursor = 0.5  # slight initial pause
    anim_counter = 0

    for i, step in enumerate(steps):
        if "comment" in step:
            text = _truncate(step["comment"], max_chars)
            aid = f"c{anim_counter}"
            anim_counter += 1
            n = len(text)
            dur = n / CHARS_PER_SEC
            timed.append(
                dict(kind="comment", aid=aid, text=text, start=time_cursor, dur=dur)
            )
            time_cursor += dur + STEP_PAUSE

        elif "cmd" in step:
            cmd = _truncate(step["cmd"], max_chars - len(prompt))
            full_line = prompt + cmd
            aid = f"cmd{anim_counter}"
            anim_counter += 1
            n = len(full_line)
            dur = n / CHARS_PER_SEC
            cursor_x = PADDING + n * char_width

            output_record = None
            if step.get("output", ""):
                oid = f"out{anim_counter}"
                anim_counter += 1
                output_lines = step["output"].rstrip("\n").split("\n")
                output_record = dict(
                    oid=oid,
                    lines=[_truncate(ln, max_chars) for ln in output_lines],
                    start=time_cursor + dur,
                )
                time_cursor += dur + FADE_DURATION
            else:
                time_cursor += dur

            timed.append(
                dict(
                    kind="cmd",
                    aid=aid,
                    cmd=cmd,
                    prompt=prompt,
                    full_line=full_line,
                    n=n,
                    dur=dur,
                    start=time_cursor - dur - (FADE_DURATION if output_record else 0),
                    cursor_x=cursor_x,
                    output=output_record,
                )
            )

        if i < len(steps) - 1:
            time_cursor += STEP_PAUSE

    loop_dur = time_cursor + LOOP_PAUSE

    # ------------------------------------------------------------------
    # Pass 2: generate keyframes + SVG elements
    # ------------------------------------------------------------------
    n_lines = _count_lines(steps)
    body_height = PADDING + n_lines * LINE_HEIGHT + PADDING
    total_height = TITLE_BAR_HEIGHT + body_height

    keyframes_parts: list[str] = []
    elements: list[str] = []

    y = TITLE_BAR_HEIGHT + PADDING + LINE_HEIGHT

    for record in timed:
        if record["kind"] == "comment":
            aid = record["aid"]
            keyframes_parts.append(
                _make_keyframes(aid, len(record["text"]), record["start"], record["dur"], loop_dur)
            )
            elements.append(
                f'    <text x="{PADDING}" y="{y}" '
                f'font-family={FONT_FAMILY!r} font-size="{FONT_SIZE}" '
                f'fill="{COMMENT_COLOR}" xml:space="preserve" class="type-{aid}">'
                f"{_escape(record['text'])}</text>"
            )
            y += LINE_HEIGHT

        elif record["kind"] == "cmd":
            aid = record["aid"]
            start_s = record["start"]
            end_s = start_s + record["dur"]

            keyframes_parts.append(
                _make_keyframes(aid, record["n"], start_s, record["dur"], loop_dur)
            )
            keyframes_parts.append(
                _make_cursor_keyframes(aid, start_s, end_s, loop_dur)
            )

            elements.append(
                f'    <text x="{PADDING}" y="{y}" '
                f'font-family={FONT_FAMILY!r} font-size="{FONT_SIZE}" '
                f'xml:space="preserve" class="type-{aid}">'
                f'<tspan fill="{theme["prompt"]}">{_escape(record["prompt"])}</tspan>'
                f'<tspan fill="{theme["text"]}">{_escape(record["cmd"])}</tspan>'
                f"</text>"
            )
            elements.append(
                f'    <rect x="{record["cursor_x"]:.1f}" y="{y - FONT_SIZE}" '
                f'width="{char_width:.1f}" height="{FONT_SIZE + 2}" '
                f'fill="{theme["text"]}" opacity="0.7" class="cursor-{aid}" />'
            )
            y += LINE_HEIGHT

            if record["output"]:
                oid = record["output"]["oid"]
                keyframes_parts.append(
                    _make_fade_keyframes(oid, record["output"]["start"], loop_dur)
                )
                for line in record["output"]["lines"]:
                    elements.append(
                        f'    <text x="{PADDING}" y="{y}" '
                        f'font-family={FONT_FAMILY!r} font-size="{FONT_SIZE}" '
                        f'fill="{OUTPUT_COLOR}" xml:space="preserve" class="fade-{oid}">'
                        f"{_escape(line)}</text>"
                    )
                    y += LINE_HEIGHT

        # blank gap between steps
        y += LINE_HEIGHT

    # remove trailing blank line gap
    y -= LINE_HEIGHT

    title_bar_svg = _render_title_bar(width, title, theme)
    keyframes_css = "\n".join(keyframes_parts)
    elements_joined = "\n".join(elements)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}" height="{total_height}"
     viewBox="0 0 {width} {total_height}">
  <style>
{keyframes_css}
  </style>
  <!-- Window frame -->
  <rect x="0" y="0" width="{width}" height="{total_height}"
        rx="8" ry="8" fill="{theme['bg']}" />
{title_bar_svg}
  <!-- Terminal body -->
  <clipPath id="body-clip">
    <rect x="0" y="{TITLE_BAR_HEIGHT}" width="{width}" height="{body_height}" />
  </clipPath>
  <g clip-path="url(#body-clip)">
{elements_joined}
  </g>
</svg>
"""
    return svg
