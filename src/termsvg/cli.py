"""termsvg CLI — typer app."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
import yaml

from .animator import render_animated_svg
from .renderer import render_svg
from .themes import THEMES

app = typer.Typer(
    name="termsvg",
    help="Generate polished terminal demo SVGs from YAML — no recording required.",
    add_completion=False,
)


def _load_yaml(path: Path) -> dict:
    try:
        with path.open() as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        typer.echo(f"Error: file not found: {path}", err=True)
        raise typer.Exit(1)
    except yaml.YAMLError as e:
        typer.echo(f"Error: invalid YAML: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def render(
    input_file: Annotated[Path, typer.Argument(help="Input YAML file")],
    output: Annotated[
        Optional[Path],
        typer.Option("-o", "--output", help="Output SVG file (default: <input>.svg)"),
    ] = None,
    animated: Annotated[
        bool, typer.Option("--animated", help="Generate animated CSS typewriter SVG")
    ] = False,
):
    """Render a terminal demo SVG from a YAML file."""
    config = _load_yaml(input_file)

    if animated:
        svg_content = render_animated_svg(config)
    else:
        svg_content = render_svg(config)

    if output is None:
        output = input_file.with_suffix(".svg")

    output.write_text(svg_content, encoding="utf-8")
    typer.echo(f"✅ Rendered {'animated ' if animated else ''}SVG → {output}")


@app.command()
def init(
    output: Annotated[
        Path,
        typer.Argument(help="Output YAML file (default: demo.yaml)"),
    ] = Path("demo.yaml"),
):
    """Scaffold a demo.yaml in the current directory."""
    if output.exists():
        overwrite = typer.confirm(f"{output} already exists. Overwrite?")
        if not overwrite:
            raise typer.Exit(0)

    content = """\
title: "My CLI Demo"
theme: dark          # dark | light | dracula | nord
prompt: "$ "
width: 700

steps:
  - comment: "# Welcome to termsvg — terminal demos without recording"

  - cmd: "mytool encode 37.7749 -122.4194"
    output: "8928308280fffff"

  - cmd: "mytool --help"
    output: |
      Usage: mytool [OPTIONS] COMMAND

        encode    Encode lat/lng to H3 cell ID
        decode    Decode H3 cell ID to lat/lng

      Options:
        --help    Show this message and exit.

  - comment: "# Supports batch mode too"

  - cmd: "mytool encode --batch coords.csv"
    output: "Processed 1000 rows → output.jsonl"
"""
    output.write_text(content, encoding="utf-8")
    typer.echo(f"✅ Created {output}")
    typer.echo("Run: termsvg render demo.yaml")


@app.command()
def themes():
    """List available themes."""
    typer.echo("Available themes:\n")
    for name, config in THEMES.items():
        bg = config["bg"]
        prompt = config["prompt"]
        typer.echo(f"  {name:<10}  bg={bg}  prompt={prompt}")
    typer.echo(
        "\nUsage: set `theme: <name>` in your YAML file, or pass --theme on the CLI."
    )


@app.command()
def preview(
    input_file: Annotated[Path, typer.Argument(help="Input YAML file")],
    animated: Annotated[
        bool, typer.Option("--animated", help="Generate animated CSS typewriter SVG")
    ] = False,
):
    """Render the SVG and open it in the default browser."""
    import tempfile

    config = _load_yaml(input_file)

    if animated:
        svg_content = render_animated_svg(config)
    else:
        svg_content = render_svg(config)

    # Write to a temp file and open it
    suffix = ".svg"
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=suffix, mode="w", encoding="utf-8"
    ) as f:
        f.write(svg_content)
        tmp_path = f.name

    typer.echo(f"Opening preview: {tmp_path}")

    try:
        if sys.platform == "darwin":
            subprocess.run(["open", tmp_path], check=True)
        elif sys.platform == "win32":
            subprocess.run(["start", tmp_path], shell=True, check=True)
        else:
            subprocess.run(["xdg-open", tmp_path], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        typer.echo(f"Could not open browser: {e}", err=True)
        typer.echo(f"SVG saved at: {tmp_path}")


if __name__ == "__main__":
    app()
