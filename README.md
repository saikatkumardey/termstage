# termstage

<img src="demo-animated.svg" alt="termstage demo" width="720">

Fake terminal demos. Write a YAML file describing the session, run `termstage render`, get an SVG. No recording, no live shell, no asciinema.

Good for README headers and docs where you want to show what a CLI looks like without screenshotting your actual terminal.

---

## Install

```bash
pip install termstage
# or
uv add termstage
```

## Quick Start

**1. Write a demo YAML:**

```yaml
# demo.yaml
title: "notes — a simple CLI notes app"
theme: dark
prompt: "$ "
width: 700

steps:
  - cmd: "notes --version"
    output: "notes 1.0.0"
  - cmd: "notes add 'Fix the login bug before Friday'"
    output: "Added note #1"
  - cmd: "notes list"
    output: |
      #1  Fix the login bug before Friday
  - comment: "# Search works too"
  - cmd: "notes search 'login'"
    output: "#1  Fix the login bug before Friday"
```

**2. Render:**

```bash
termstage render demo.yaml            # → demo.svg
termstage render demo.yaml -o out.svg
termstage render demo.yaml --animated # CSS typewriter animation
```

**3. Preview:**

```bash
termstage preview demo.yaml
```

---

## Commands

| Command | Description |
|---------|-------------|
| `termstage render <file.yaml>` | Render static SVG |
| `termstage render <file.yaml> -o out.svg` | Custom output path |
| `termstage render <file.yaml> --animated` | Animated CSS typewriter SVG |
| `termstage init` | Create a starter `demo.yaml` in current directory |
| `termstage themes` | List available themes |
| `termstage preview <file.yaml>` | Render and open in browser |

---

## YAML Format

```yaml
title: "my cli demo"        # Window title bar text
theme: dark                 # dark | light | dracula | nord
prompt: "$ "                # Prompt string
width: 700                  # SVG width in pixels (default: 700)

steps:
  - cmd: "notes --version"
    output: "notes 1.0.0"

  - cmd: "notes add 'Fix the login bug before Friday'"
    output: "Added note #1"

  - cmd: "notes --help"
    output: |
      Usage: notes [OPTIONS] COMMAND
        add     Add a new note
        list    List all notes
        search  Search notes by keyword
        done    Mark a note as done

  - comment: "# Search works too"

  - cmd: "notes search 'login'"
    output: "#1  Fix the login bug before Friday"
```

Two step types: `cmd` (prompt + command + optional output) and `comment` (no prompt, styled like a code comment).

---

## Themes

| Theme | Background | Based on |
|-------|------------|----------|
| `dark` | `#1e1e1e` | VS Code Dark+ (default) |
| `light` | `#ffffff` | Clean light terminal |
| `dracula` | `#282a36` | Dracula |
| `nord` | `#2e3440` | Nord |

```bash
termstage themes
```

---

## Animated SVG

`--animated` generates a pure CSS animated SVG: commands type out character by character, output fades in after each one, cursor blinks. No JavaScript — works in GitHub READMEs and anywhere SVG is supported.

```bash
termstage render demo.yaml --animated -o demo-animated.svg
```

---

## Window

SVGs render with a macOS-style title bar (traffic light dots, centered title, rounded corners). Font stack: JetBrains Mono, Fira Code, Cascadia Code, monospace.

---

## Examples

```bash
termstage init
termstage render demo.yaml -o demo.svg
termstage render demo.yaml --animated -o demo-animated.svg
```

---

## License

MIT
