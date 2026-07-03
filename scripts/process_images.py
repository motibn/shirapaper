#!/usr/bin/env python3
"""Process workshop photos: gallery WebPs, hero collage, patch index.html."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
ASSETS = ROOT / "assets"
GALLERY_DIR = ASSETS / "gallery"
SOURCE_DIR = ASSETS / "source"
CURSOR_ASSETS = Path(
    "/Users/admin-pc/.cursor/projects/Users-admin-pc-Library-Mobile-Documents-com-apple-CloudDocs-shirapaper-shirapaper/assets"
)

GALLERY_ITEMS = [
    ("IMG-20250825-WA0024", "g01.webp", "אלבום זכרונות מעוצב"),
    ("IMG-20240810-WA0005", "g02.webp", "לוח שנה שולחני"),
    ("IMG-20250824-WA0030", "g03.webp", "קופסת יצירה אישית"),
    ("20250727_214424", "g04.webp", "סדנה קבוצתית בסטודיו"),
    ("IMG-20250919-WA0120", "g05.webp", "סדנה משפחתית"),
    ("IMG-20250919-WA0087", "g06.webp", "ריכוז ויצירה"),
    ("IMG-20250919-WA0118", "g07.webp", "ילדים בסדנת יצירה"),
    ("20250727_213810", "g08.webp", "מחברת דונאטס מעוצבת"),
    ("20250809_235356", "g09.webp", "משתתפות מציגות יצירות"),
    ("20250727_183606", "g10.webp", "סדנת סקרפ בוק"),
    ("20250811_124134", "g11.webp", "יצירה בסטנסיל"),
    ("IMG-20250825-WA0026", "g12.webp", "חוויית יצירה בסדנה"),
]

HERO_COLLAGE = {
    "left": "20250727_214424",
    "right_top": "IMG-20250919-WA0118",
    "right_mid": "IMG-20250825-WA0024",
    "right_bl": "20250809_235356",
    "right_br": "20250727_213810",
}

COLLAGE_W, COLLAGE_H, GAP = 1200, 900, 4
GALLERY_MAX = 800
WEBP_QUALITY = 82


def find_source(prefix: str) -> Path:
    for base in (CURSOR_ASSETS, SOURCE_DIR):
        if not base.exists():
            continue
        matches = sorted(base.glob(f"{prefix}*"))
        if matches:
            return matches[0]
    raise FileNotFoundError(f"No source image matching prefix: {prefix}")


def copy_all_sources() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    if not CURSOR_ASSETS.exists():
        return
    for src in CURSOR_ASSETS.glob("*.png"):
        dest = SOURCE_DIR / src.name
        if not dest.exists():
            shutil.copy2(src, dest)


def load_rgb(path: Path) -> Image.Image:
    img = Image.open(path).convert("RGB")
    return img


def fit_cover(img: Image.Image, w: int, h: int) -> Image.Image:
    if w <= 0 or h <= 0:
        raise ValueError("invalid target size")
    src_w, src_h = img.size
    scale = max(w / src_w, h / src_h)
    nw, nh = int(src_w * scale), int(src_h * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return resized.crop((left, top, left + w, top + h))


def save_webp(img: Image.Image, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp.jpg")
    img.save(tmp, "JPEG", quality=90, optimize=True)
    subprocess.run(
        ["cwebp", "-q", str(WEBP_QUALITY), str(tmp), "-o", str(dest)],
        check=True,
        capture_output=True,
    )
    tmp.unlink(missing_ok=True)


def build_gallery() -> list[dict[str, str]]:
    GALLERY_DIR.mkdir(parents=True, exist_ok=True)
    items: list[dict[str, str]] = []
    for prefix, filename, label in GALLERY_ITEMS:
        src = find_source(prefix)
        img = load_rgb(src)
        img.thumbnail((GALLERY_MAX, GALLERY_MAX), Image.Resampling.LANCZOS)
        out = GALLERY_DIR / filename
        save_webp(img, out)
        items.append({"label": label, "img": f"assets/gallery/{filename}"})
        print(f"  gallery: {filename} <- {src.name}")
    return items


def build_hero_collage() -> Path:
    gap = GAP
    left_w = (COLLAGE_W - gap) * 2 // 3
    right_w = COLLAGE_W - gap - left_w
    row_h = (COLLAGE_H - gap * 2) // 3
    bottom_w = (right_w - gap) // 2

    canvas = Image.new("RGB", (COLLAGE_W, COLLAGE_H), (250, 247, 249))

    placements = [
        (HERO_COLLAGE["left"], 0, 0, left_w, COLLAGE_H),
        (HERO_COLLAGE["right_top"], left_w + gap, 0, right_w, row_h),
        (HERO_COLLAGE["right_mid"], left_w + gap, row_h + gap, right_w, row_h),
        (HERO_COLLAGE["right_bl"], left_w + gap, 2 * (row_h + gap), bottom_w, row_h),
        (HERO_COLLAGE["right_br"], left_w + gap + bottom_w + gap, 2 * (row_h + gap), right_w - bottom_w - gap, row_h),
    ]

    for prefix, x, y, w, h in placements:
        src = find_source(prefix)
        tile = fit_cover(load_rgb(src), w, h)
        canvas.paste(tile, (x, y))
        print(f"  collage tile: {src.name} at {x},{y} {w}x{h}")

    out = ASSETS / "hero-collage.webp"
    save_webp(canvas, out)
    return out


def read_template() -> str:
    content = INDEX.read_text(encoding="utf-8")
    start = content.find('<script type="__bundler/template">')
    end = content.find("</script>", start)
    raw = content[start + len('<script type="__bundler/template">'):end].strip().replace("<\\/", "</")
    return json.loads(raw)


def write_template(tpl: str) -> None:
    content = INDEX.read_text(encoding="utf-8")
    open_tag = '<script type="__bundler/template">'
    start = content.find(open_tag)
    json_start = start + len(open_tag)
    end = content.find("</script>", json_start)
    payload = json.dumps(tpl, ensure_ascii=True).replace("</", "<\\/")
    INDEX.write_text(content[:json_start] + "\n" + payload + "\n  " + content[end:], encoding="utf-8")


def patch_index(gallery_items: list[dict[str, str]]) -> None:
    tpl = read_template()

    gallery_js = "gallery = [\n" + "".join(
        f"    {{ label: '{item['label']}', img: '{item['img']}' }},\n" for item in gallery_items
    ) + "  ];"
    tpl = re.sub(
        r"gallery = \[[\s\S]*?\];",
        gallery_js,
        tpl,
        count=1,
    )

    tpl = tpl.replace('hint-placeholder-count="6"', 'hint-placeholder-count="12"', 1)

    tpl = tpl.replace(
        '<img src="assets/hero.webp" alt="ילדים יוצרים בסדנת עיצוב בנייר בסטודיו שירה בנייר"',
        '<img src="assets/hero-collage.webp" alt="סדנאות עיצוב בנייר — שירה בנייר"',
        1,
    )

    write_template(tpl)
    print("Patched index.html template")


def remove_old_placeholders() -> None:
    patterns = ["g1-album*", "g2-calendar*", "g3-box*", "g4-group*", "g5-cards*", "g6-family*", "hero.jpg", "hero.webp"]
    for pat in patterns:
        for path in ASSETS.glob(pat):
            path.unlink()
            print(f"  removed {path.name}")


def main() -> None:
    print("Copying sources...")
    copy_all_sources()

    print("Building gallery...")
    gallery_items = build_gallery()

    print("Building hero collage...")
    collage = build_hero_collage()
    print(f"  -> {collage} ({collage.stat().st_size // 1024} KB)")

    print("Patching index.html...")
    patch_index(gallery_items)

    print("Removing old placeholders...")
    remove_old_placeholders()

    print("Done.")


if __name__ == "__main__":
    main()
