"""Generate a contribution snake SVG from public GitHub contribution data."""

import json
import urllib.request
from pathlib import Path

USERNAME = "nanfaweb"
OUT = Path(__file__).resolve().parents[1] / "assets" / "snake.svg"

# GitHub contribution colors (dark theme, purple accent snake)
COLORS = ["#161b22", "#1e1033", "#3b0764", "#6b21a8", "#a855f7"]
SNAKE_COLOR = "#c084fc"
BG = "#0d1117"
CELL = 11
PAD = 16


def fetch_grid(username: str) -> list[list[int]]:
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    # Parse contribution counts from tooltip text in the HTML calendar
    import re

    counts = [int(x) for x in re.findall(r'(\d+) contributions on', html)]
    if not counts:
        raise RuntimeError("Could not parse contribution data from GitHub")

    cols = len(counts) // 7
    grid = [[0] * cols for _ in range(7)]
    i = 0
    for c in range(cols):
        for r in range(7):
            if i < len(counts):
                grid[r][c] = counts[i]
                i += 1
    return grid


def color_for(count: int) -> str:
    if count == 0:
        return COLORS[0]
    if count == 1:
        return COLORS[1]
    if count <= 3:
        return COLORS[2]
    if count <= 6:
        return COLORS[3]
    return COLORS[4]


def snake_path(cols: int, rows: int = 7) -> list[tuple[int, int]]:
    path: list[tuple[int, int]] = []
    for c in range(cols):
        row_range = range(rows) if c % 2 == 0 else range(rows - 1, -1, -1)
        for r in row_range:
            path.append((r, c))
    return path


def main() -> None:
    grid = fetch_grid(USERNAME)
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    width = PAD * 2 + cols * CELL
    height = PAD * 2 + rows * CELL

    path = snake_path(cols, rows)
    snake_cells = {path[i] for i in range(min(len(path), max(1, sum(sum(r) for r in grid) // 2)))}

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{BG}" rx="6"/>',
    ]

    for r in range(rows):
        for c in range(cols):
            x = PAD + c * CELL
            y = PAD + r * CELL
            count = grid[r][c]
            fill = SNAKE_COLOR if (r, c) in snake_cells else color_for(count)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL - 2}" height="{CELL - 2}" rx="2" fill="{fill}"/>'
            )

    parts.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
