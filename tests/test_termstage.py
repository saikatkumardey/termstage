"""Tests for termstage SVG rendering."""

from __future__ import annotations

import pytest

from termstage.renderer import render_svg
from termstage.animator import render_animated_svg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _basic_config(**overrides):
    cfg = {
        "title": "test demo",
        "theme": "dark",
        "prompt": "$ ",
        "width": 700,
        "steps": [
            {"cmd": "echo hello", "output": "hello"},
        ],
    }
    cfg.update(overrides)
    return cfg


# ---------------------------------------------------------------------------
# render_svg — basic structure
# ---------------------------------------------------------------------------

class TestRenderSvgBasic:
    def test_contains_svg_tag(self):
        svg = render_svg(_basic_config())
        assert "<svg" in svg

    def test_correct_width(self):
        svg = render_svg(_basic_config(width=700))
        assert 'width="700"' in svg

    def test_title_in_output(self):
        svg = render_svg(_basic_config(title="My Cool CLI"))
        assert "My Cool CLI" in svg

    def test_utf8_declaration(self):
        svg = render_svg(_basic_config())
        assert 'encoding="UTF-8"' in svg


# ---------------------------------------------------------------------------
# render_animated_svg — basic structure
# ---------------------------------------------------------------------------

class TestRenderAnimatedSvgBasic:
    def test_contains_svg_tag(self):
        svg = render_animated_svg(_basic_config())
        assert "<svg" in svg

    def test_contains_keyframes(self):
        svg = render_animated_svg(_basic_config())
        assert "@keyframes" in svg

    def test_correct_width(self):
        svg = render_animated_svg(_basic_config(width=700))
        assert 'width="700"' in svg

    def test_title_in_output(self):
        svg = render_animated_svg(_basic_config(title="Animated Demo"))
        assert "Animated Demo" in svg

    def test_utf8_declaration(self):
        svg = render_animated_svg(_basic_config())
        assert 'encoding="UTF-8"' in svg


# ---------------------------------------------------------------------------
# All 4 themes render without error
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("theme", ["dark", "light", "dracula", "nord"])
def test_all_themes_static(theme):
    svg = render_svg(_basic_config(theme=theme))
    assert "<svg" in svg


@pytest.mark.parametrize("theme", ["dark", "light", "dracula", "nord"])
def test_all_themes_animated(theme):
    svg = render_animated_svg(_basic_config(theme=theme))
    assert "<svg" in svg


# ---------------------------------------------------------------------------
# Step types
# ---------------------------------------------------------------------------

class TestStepTypes:
    def test_cmd_step_has_prompt(self):
        cfg = _basic_config(steps=[{"cmd": "ls -la", "output": "total 0"}])
        svg = render_svg(cfg)
        # Default prompt is "$ "
        assert "$ " in svg
        assert "ls -la" in svg

    def test_cmd_step_has_output(self):
        cfg = _basic_config(steps=[{"cmd": "pwd", "output": "/home/user"}])
        svg = render_svg(cfg)
        assert "/home/user" in svg

    def test_comment_step_rendered(self):
        cfg = _basic_config(steps=[{"comment": "# This is a comment"}])
        svg = render_svg(cfg)
        assert "# This is a comment" in svg

    def test_comment_step_no_prompt(self):
        """Comment lines should NOT contain the prompt character sequence."""
        cfg = _basic_config(
            prompt="%%> ",
            steps=[{"comment": "# just a comment"}],
        )
        svg = render_svg(cfg)
        # The prompt should not appear when there's only a comment step
        assert "%%&gt;" not in svg  # escaped form
        assert "%%>" not in svg     # raw form

    def test_mixed_steps(self):
        cfg = _basic_config(steps=[
            {"comment": "# step one"},
            {"cmd": "date", "output": "Thu Feb 26 2026"},
        ])
        svg = render_svg(cfg)
        assert "# step one" in svg
        assert "date" in svg
        assert "Thu Feb 26 2026" in svg


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_steps_no_crash(self):
        cfg = _basic_config(steps=[])
        svg = render_svg(cfg)
        assert "<svg" in svg

    def test_empty_steps_animated_no_crash(self):
        cfg = _basic_config(steps=[])
        svg = render_animated_svg(cfg)
        assert "<svg" in svg

    def test_long_output_line_no_crash(self):
        long_line = "x" * 200
        cfg = _basic_config(steps=[{"cmd": "cat big.txt", "output": long_line}])
        svg = render_svg(cfg)
        assert "<svg" in svg
        # Long line should be truncated (ellipsis present)
        assert "…" in svg

    def test_long_cmd_no_crash(self):
        long_cmd = "echo " + "a" * 200
        cfg = _basic_config(steps=[{"cmd": long_cmd}])
        svg = render_svg(cfg)
        assert "<svg" in svg
        assert "…" in svg

    def test_long_comment_no_crash(self):
        long_comment = "# " + "a" * 200
        cfg = _basic_config(steps=[{"comment": long_comment}])
        svg = render_svg(cfg)
        assert "<svg" in svg
        assert "…" in svg

    def test_unicode_in_cmd(self):
        cfg = _basic_config(steps=[{"cmd": "echo 'héllo wörld 日本語'"}])
        svg = render_svg(cfg)
        assert "<svg" in svg

    def test_unicode_in_output(self):
        cfg = _basic_config(steps=[{"cmd": "greet", "output": "こんにちは 🌸"}])
        svg = render_svg(cfg)
        assert "<svg" in svg
        assert "こんにちは" in svg

    def test_unicode_animated_no_crash(self):
        cfg = _basic_config(steps=[
            {"cmd": "echo '✨ done'", "output": "✨ done"},
        ])
        svg = render_animated_svg(cfg)
        assert "<svg" in svg

    def test_multiline_output(self):
        cfg = _basic_config(steps=[{
            "cmd": "ls",
            "output": "file1.txt\nfile2.txt\nfile3.txt",
        }])
        svg = render_svg(cfg)
        assert "file1.txt" in svg
        assert "file2.txt" in svg
        assert "file3.txt" in svg

    def test_no_output_key(self):
        """Steps without 'output' key should not crash."""
        cfg = _basic_config(steps=[{"cmd": "clear"}])
        svg = render_svg(cfg)
        assert "<svg" in svg

    def test_unknown_theme_falls_back(self):
        """Unknown theme should not crash (falls back to dark)."""
        cfg = _basic_config(theme="nonexistent")
        svg = render_svg(cfg)
        assert "<svg" in svg
