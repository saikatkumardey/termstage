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

# Characters per second for typing animation
CHARS_PER_SEC = 30
# Seconds for output fade-in
FADE_DURATION = 0.4
# Seconds pause after each step before next starts
STEP_PAUSE = 0.3


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


def _make_keyframes(anim_id: str, n_chars: int, start_s: float, duration_s: float) -> str:
    """Generate @keyframes for a typewriter clip-path width expansion."""
    # We use a clipPath trick: text is clipped by a rect whose width grows.
    # Each character is ~ch wide; we animate max-width via clip-path.
    # Actually we'll use the 'steps()' timing function with clip-path width.
    # The animation: from width=0 to width=full_width over duration_s
    # with steps(n_chars, end) for discrete character reveals.
    steps_fn = f"steps({max(n_chars, 1)}, end)"
    delay_s = start_s

    return (
        f"  @keyframes type-{anim_id} {{\n"
        f"    from {{ clip-path: inset(0 100% 0 0); }}\n"
        f"    to   {{ clip-path: inset(0 0% 0 0); }}\n"
        f"  }}\n"
        f"  .type-{anim_id} {{\n"
        f"    clip-path: inset(0 100% 0 0);\n"
        f"    animation: type-{anim_id} {duration_s:.3f}s {steps_fn} {delay_s:.3f}s forwards;\n"
        f"  }}\n"
    )


def _make_fade_keyframes(anim_id: str, start_s: float) -> str:
    return (
        f"  @keyframes fade-{anim_id} {{\n"
        f"    from {{ opacity: 0; }}\n"
        f"    to   {{ opacity: 1; }}\n"
        f"  }}\n"
        f"  .fade-{anim_id} {{\n"
        f"    opacity: 0;\n"
        f"    animation: fade-{anim_id} {FADE_DURATION:.2f}s ease {start_s:.3f}s forwards;\n"
        f"  }}\n"
    )


def _make_cursor_keyframes(anim_id: str, start_s: float, end_s: float) -> str:
    """Cursor blinks during typing, then disappears."""
    return (
        f"  @keyframes blink-{anim_id} {{\n"
        f"    0%, 49% {{ opacity: 1; }}\n"
        f"    50%, 100% {{ opacity: 0; }}\n"
        f"  }}\n"
        f"  .cursor-{anim_id} {{\n"
        f"    opacity: 0;\n"
        f"    animation:\n"
        f"      blink-{anim_id} 0.6s step-end {start_s:.3f}s {int((end_s - start_s) / 0.6) + 1},\n"
        f"      fade-{anim_id}-out 0.01s linear {end_s:.3f}s forwards;\n"
        f"  }}\n"
        f"  @keyframes fade-{anim_id}-out {{\n"
        f"    to {{ opacity: 0; }}\n"
        f"  }}\n"
    )


def render_animated_svg(config: dict[str, Any]) -> str:
    """
    Render an animated SVG terminal window from config dict.
    Uses CSS @keyframes for typewriter + fade-in effects. No JS.
    """
    title = config.get("title", "termstage demo")
    theme_name = config.get("theme", "dark")
    prompt = config.get("prompt", "$ ")
    width = int(config.get("width", 700))
    steps = config.get("steps", [])

    theme = THEMES.get(theme_name, THEMES["dark"])

    n_lines = _count_lines(steps)
    body_height = PADDING + n_lines * LINE_HEIGHT + PADDING
    total_height = TITLE_BAR_HEIGHT + body_height

    keyframes_parts: list[str] = []
    elements: list[str] = []

    y = TITLE_BAR_HEIGHT + PADDING + LINE_HEIGHT
    time_cursor = 0.5  # slight initial pause

    anim_counter = 0

    for i, step in enumerate(steps):
        if "comment" in step:
            comment_text = step["comment"]
            aid = f"c{anim_counter}"
            anim_counter += 1
            n_chars = len(comment_text)
            duration = n_chars / CHARS_PER_SEC

            keyframes_parts.append(_make_keyframes(aid, n_chars, time_cursor, duration))
            time_cursor += duration

            elements.append(
                f'    <text x="{PADDING}" y="{y}" '
                f'font-family={FONT_FAMILY!r} font-size="{FONT_SIZE}" '
                f'fill="{COMMENT_COLOR}" xml:space="preserve" class="type-{aid}">'
                f"{_escape(comment_text)}</text>"
            )
            y += LINE_HEIGHT
            time_cursor += STEP_PAUSE

        elif "cmd" in step:
            cmd = step["cmd"]
            output = step.get("output", "")

            full_line = prompt + cmd
            aid = f"cmd{anim_counter}"
            anim_counter += 1
            n_chars = len(full_line)
            duration = n_chars / CHARS_PER_SEC

            # Cursor appears at start of typing, disappears at end
            cursor_end = time_cursor + duration
            keyframes_parts.append(_make_keyframes(aid, n_chars, time_cursor, duration))
            keyframes_parts.append(
                _make_cursor_keyframes(aid, time_cursor, cursor_end)
            )

            # Cursor x position: after the text. Approximate at font-size * 0.6 per char
            char_width = FONT_SIZE * 0.61
            cursor_x = PADDING + n_chars * char_width

            elements.append(
                f'    <text x="{PADDING}" y="{y}" '
                f'font-family={FONT_FAMILY!r} font-size="{FONT_SIZE}" '
                f'xml:space="preserve" class="type-{aid}">'
                f'<tspan fill="{theme["prompt"]}">{_escape(prompt)}</tspan>'
                f'<tspan fill="{theme["text"]}">{_escape(cmd)}</tspan>'
                f"</text>"
            )
            # Cursor rect (blinking block)
            elements.append(
                f'    <rect x="{cursor_x:.1f}" y="{y - FONT_SIZE}" '
                f'width="{char_width:.1f}" height="{FONT_SIZE + 2}" '
                f'fill="{theme["text"]}" opacity="0.7" class="cursor-{aid}" />'
            )

            time_cursor = cursor_end
            y += LINE_HEIGHT

            if output:
                output_lines = output.rstrip("\n").split("\n")
                # Fade in all output lines together
                oid = f"out{anim_counter}"
                anim_counter += 1
                keyframes_parts.append(_make_fade_keyframes(oid, time_cursor))
                time_cursor += FADE_DURATION

                for line in output_lines:
                    elements.append(
                        f'    <text x="{PADDING}" y="{y}" '
                        f'font-family={FONT_FAMILY!r} font-size="{FONT_SIZE}" '
                        f'fill="{OUTPUT_COLOR}" xml:space="preserve" class="fade-{oid}">'
                        f"{_escape(line)}</text>"
                    )
                    y += LINE_HEIGHT

        # blank gap between steps
        if i < len(steps) - 1:
            y += LINE_HEIGHT
            time_cursor += STEP_PAUSE

    title_bar_svg = _render_title_bar(width, title, theme)
    keyframes_css = "\n".join(keyframes_parts)
    elements_joined = "\n".join(elements)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
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
