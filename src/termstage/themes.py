"""Terminal color themes for termstage."""

THEMES: dict[str, dict] = {
    "dark": {
        "bg": "#1e1e1e",
        "title_bar": "#323233",
        "text": "#d4d4d4",
        "prompt": "#4ec9b0",
        "dots": True,
    },
    "light": {
        "bg": "#ffffff",
        "title_bar": "#e0e0e0",
        "text": "#333333",
        "prompt": "#007acc",
        "dots": True,
    },
    "dracula": {
        "bg": "#282a36",
        "title_bar": "#44475a",
        "text": "#f8f8f2",
        "prompt": "#50fa7b",
        "dots": True,
    },
    "nord": {
        "bg": "#2e3440",
        "title_bar": "#3b4252",
        "text": "#eceff4",
        "prompt": "#88c0d0",
        "dots": True,
    },
}

COMMENT_COLOR = "#6a9955"
OUTPUT_COLOR = "#aaaaaa"
FONT_FAMILY = "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace"
FONT_SIZE = 14
LINE_HEIGHT = 22
TITLE_BAR_HEIGHT = 38
PADDING = 20
