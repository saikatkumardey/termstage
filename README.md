# termsvg

> Generate polished terminal demo SVGs from a YAML file — no recording required.

Write a simple YAML file describing your CLI demo, run `termsvg render`, and get a beautiful terminal screenshot or animated typewriter SVG — perfect for README headers, docs, and blog posts.

---

## Install

```bash
pip install termsvg
# or
uv add termsvg
```

## Quick Start

**1. Create a demo YAML:**

```yaml
# demo.yaml
title: "My CLI Tool"
theme: dark
prompt: "$ "
width: 700

steps:
  - comment: "# Install and run"
  - cmd: "mytool --version"
    output: "mytool 1.2.0"
  - cmd: "mytool encode 37.7749 -122.4194"
    output: "8928308280fffff"
```

**2. Render to SVG:**

```bash
termsvg render demo.yaml            # → demo.svg (static)
termsvg render demo.yaml -o out.svg # custom output path
termsvg render demo.yaml --animated # CSS typewriter animation
```

**3. Preview in browser:**

```bash
termsvg preview demo.yaml
termsvg preview demo.yaml --animated
```

---

## Commands

| Command | Description |
|---------|-------------|
| `termsvg render <file.yaml>` | Render static SVG |
| `termsvg render <file.yaml> -o out.svg` | Render to custom output path |
| `termsvg render <file.yaml> --animated` | Render animated CSS typewriter SVG |
| `termsvg init` | Scaffold a `demo.yaml` in the current directory |
| `termsvg themes` | List available themes |
| `termsvg preview <file.yaml>` | Render and open in default browser |

---

## YAML Format

```yaml
title: "my cli demo"        # Window title bar text
theme: dark                 # dark | light | dracula | nord
prompt: "$ "                # Prompt string (styled in theme color)
width: 700                  # SVG width in pixels (default: 700)

steps:
  - cmd: "mytool encode 37.7749 -122.4194"
    output: "8928308280fffff"

  - cmd: "mytool --help"
    output: |
      Usage: mytool [OPTIONS] COMMAND
        encode    Encode lat/lng to cell ID
        decode    Decode cell ID to lat/lng

  - comment: "# Supports batch mode"   # styled as a comment

  - cmd: "mytool encode --batch coords.csv"
    output: "Processed 1000 rows → output.jsonl"
```

### Step types

- **`cmd`** — a command line (prompt + command text, optional output)
- **`comment`** — a comment line (no prompt, green VS Code comment color)

---

## Themes

Four built-in themes:

| Theme | Background | Description |
|-------|------------|-------------|
| `dark` | `#1e1e1e` | VS Code Dark+ (default) |
| `light` | `#ffffff` | Clean light terminal |
| `dracula` | `#282a36` | Dracula color scheme |
| `nord` | `#2e3440` | Nord Arctic color scheme |

```bash
termsvg themes  # list all themes with colors
```

---

## Animated SVG

The `--animated` flag generates a pure CSS animated SVG:

- **Typewriter effect** — each command types out character by character
- **Fade-in output** — command output fades in after typing completes
- **Cursor blink** — blinking cursor tracks active typing position
- **Staggered timing** — each step starts after the previous finishes
- **No JavaScript** — works in any SVG-capable viewer, GitHub READMEs, etc.

```bash
termsvg render demo.yaml --animated -o demo-animated.svg
```

---

## Window Chrome

All SVGs include a macOS-style terminal window with:
- Title bar with red/yellow/green traffic light dots
- Centered title text
- Rounded corners
- Monospace font: JetBrains Mono › Fira Code › Cascadia Code › system monospace

---

## Examples

See [`examples/demo.yaml`](examples/demo.yaml) for a ready-to-render demo.

```bash
termsvg render examples/demo.yaml -o demo.svg
termsvg render examples/demo.yaml --animated -o demo-animated.svg
```

---

## License

MIT
