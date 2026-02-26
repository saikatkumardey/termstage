# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versions follow [Semantic Versioning](https://semver.org/).

---

## [0.2.0] — 2026-02-25

### Changed
- `termstage init` now reads the starter template from `src/termstage/templates/starter.yaml` via `importlib.resources` — no more hardcoded YAML string in cli.py
- Starter template has inline comments explaining each field

### Added
- Animated self-demo SVG in README (`demo-animated.svg`, Dracula theme)
- `demo.yaml` in repo root — the demo used to generate the README SVG
- Rewritten README with clear 5-step flow: init → edit → preview → render → embed

---

## [0.1.0] — 2026-02-25

### Added
- Initial release
- YAML-driven terminal demo SVG generation — no recording required
- `termstage` CLI with `render` command
- Support for typing, pause, output, and clear actions
- Typer-based CLI with `--output` flag
- PyPI packaging via hatchling + uv
