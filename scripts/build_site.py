#!/usr/bin/env python3
"""Prepare shirapaper landing page for Vercel deployment."""
from __future__ import annotations

import base64
import gzip
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
DS_DIR = ROOT / "_ds" / "shirapaper-design-system-44268b31-83a5-46a5-9317-330e22242c21"
ASSETS = ROOT / "assets"

UUID_LOGO = "6a2a1711-7d49-43c7-a01f-53e500ae0668"
UUID_STORY = "7ae7fe59-5dfd-45e4-bb28-4ddcc8f8bbff"
UUID_HERO = "f526d5fb-2de1-482b-aaf4-876f068b75b7"
UUID_DC = "bda35eb6-6e80-4ec3-b132-c58767827c3b"
UUID_DS_LOADER = "0c485c21-e9aa-4bfa-a2f8-58fd6e45fde7"

SITE_URL = "https://shirapaper.vercel.app"
SITE_TITLE = "שירה בנייר | סדנאות עיצוב בנייר בצפון הגולן"
SITE_DESC = "סדנאות וחוגי עיצוב בנייר בקלע אלון. סדנאות משפחתיות, קבוצות ואירועים. הרשמה בוואטסאפ."

FAQ_JSON_LD = [
    ("צריך ניסיון קודם או כישרון ציור?", "ממש לא! הסדנאות מונחות שלב-אחר-שלב ומתאימות לכולם."),
    ("מאיזה גיל אפשר להשתתף?", "הסדנאות מתאימות מגיל 6 ומעלה ולמבוגרים בכל גיל."),
    ("כמה זמן נמשכת סדנה?", "סדנה טיפוסית נמשכת בין שעתיים לשלוש שעות."),
    ("אילו חומרים כלולים בסדנה?", "הכל כלול — חומרי גלם איכותיים וסביבת עבודה מאובזרת."),
    ("צריך להירשם מראש?", "כן, המקומות מוגבלים. משאירים פרטים בטופס ואני חוזרת לתיאום."),
    ("איפה הסטודיו ממוקם?", "הסטודיו בקלע אלון שבצפון הגולן, באווירה ביתית וחמה."),
    ("אפשר להזמין סדנה פרטית?", "בהחלט — ימי הולדת, גיבוש, בת מצווה ומשפחות."),
]


def write_design_system() -> None:
    tokens = DS_DIR / "tokens"
    tokens.mkdir(parents=True, exist_ok=True)

    (tokens / "fonts.css").write_text(
        """@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&family=Rubik:wght@500;600;700;800&display=swap');

:root {
  --font-body: 'Heebo', 'Arial Hebrew', Arial, sans-serif;
  --font-display: 'Rubik', 'Arial Hebrew', Arial, sans-serif;
  --font-ui: 'Heebo', 'Arial Hebrew', Arial, sans-serif;
}
""",
        encoding="utf-8",
    )

    (tokens / "colors.css").write_text(
        """:root {
  --white: #ffffff;
  --pink-200: #f8d9e8;
  --pink-300: #efb8d4;
  --pink-600: #c23d7a;
  --purple-500: #8b3f9b;
  --purple-600: #6f2c79;
  --purple-700: #5a2370;
  --gold-300: #fde4a8;
  --gold-500: #fab847;
  --gold-600: #e09a2e;
  --blue-300: #b8d4f0;
  --blue-500: #5b9bd5;
  --blue-600: #3d7ab8;
  --text-body: #3d3340;
  --text-muted: #7a6e82;
  --text-strong: #2a1f30;
  --text-on-dark: #fce8f2;
  --surface-page: #faf7f9;
  --surface-sunken: #f3edf2;
  --surface-card: #ffffff;
  --surface-dark: #3d1f4a;
  --border-subtle: rgba(111, 44, 121, 0.12);
  --gradient-brand: linear-gradient(135deg, #fab847 0%, #e8a6c1 50%, #6f2c79 100%);
  --gradient-brand-soft: linear-gradient(135deg, rgba(250,184,71,.15) 0%, rgba(232,166,193,.15) 50%, rgba(111,44,121,.12) 100%);
  --gradient-text: linear-gradient(135deg, #c23d7a 0%, #8b3f9b 50%, #6f2c79 100%);
}
""",
        encoding="utf-8",
    )

    (tokens / "typography.css").write_text(
        """:root {
  --text-xs: 12px;
  --text-sm: 14px;
  --text-base: 16px;
  --text-lg: 18px;
  --text-xl: 22px;
}
""",
        encoding="utf-8",
    )

    (tokens / "spacing.css").write_text(
        """:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
}
""",
        encoding="utf-8",
    )

    (tokens / "effects.css").write_text(
        """:root {
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 28px;
  --radius-pill: 999px;
  --shadow-xs: 0 1px 2px rgba(42, 31, 48, 0.06);
  --shadow-sm: 0 2px 8px rgba(42, 31, 48, 0.08);
  --shadow-md: 0 4px 16px rgba(42, 31, 48, 0.1);
  --shadow-lg: 0 8px 32px rgba(42, 31, 48, 0.12);
  --shadow-xl: 0 16px 48px rgba(42, 31, 48, 0.16);
  --shadow-pink: 0 8px 24px rgba(194, 61, 122, 0.25);
  --dur-fast: 0.15s;
  --dur-base: 0.25s;
  --dur-slow: 0.4s;
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
}
""",
        encoding="utf-8",
    )

    (tokens / "base.css").write_text(
        """*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; }
""",
        encoding="utf-8",
    )

    (DS_DIR / "styles.css").write_text(
        """.ds-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: var(--font-ui);
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: transform var(--dur-fast) var(--ease-out), box-shadow var(--dur-fast) var(--ease-out), opacity var(--dur-fast);
  text-decoration: none;
  line-height: 1.2;
}
.ds-btn:hover { transform: translateY(-1px); }
.ds-btn:active { transform: translateY(0); }
.ds-btn--block { width: 100%; }
.ds-btn--pill { border-radius: var(--radius-pill); }
.ds-btn--sm { padding: 10px 18px; font-size: 14px; }
.ds-btn--lg { padding: 14px 28px; font-size: 16px; }
.ds-btn--md { padding: 12px 22px; font-size: 15px; }
.ds-btn--primary { background: var(--purple-600); color: #fff; box-shadow: var(--shadow-sm); }
.ds-btn--primary:hover { box-shadow: var(--shadow-md); }
.ds-btn--gradient { background: var(--gradient-brand); color: #fff; box-shadow: var(--shadow-pink); }
.ds-btn--secondary { background: #fff; color: var(--purple-600); border: 2px solid var(--purple-600); }
.ds-btn--gold { background: linear-gradient(135deg, var(--gold-500), var(--gold-600)); color: var(--text-strong); }
.ds-btn--ghost { background: transparent; color: var(--purple-600); border: 1px solid var(--border-subtle); }
.ds-field { display: flex; flex-direction: column; gap: 6px; width: 100%; }
.ds-label { font-family: var(--font-ui); font-size: 14px; font-weight: 600; color: var(--text-strong); }
.ds-input, .ds-select, .ds-textarea {
  width: 100%;
  font-family: var(--font-body);
  font-size: 16px;
  padding: 12px 14px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: #fff;
  color: var(--text-body);
  direction: rtl;
}
.ds-input:focus, .ds-select:focus, .ds-textarea:focus {
  outline: 2px solid rgba(111, 44, 121, 0.25);
  border-color: var(--purple-500);
}
.ds-textarea { resize: vertical; min-height: 96px; }
""",
        encoding="utf-8",
    )

    (DS_DIR / "_ds_bundle.js").write_text(
        r"""(function () {
  function whenReact(cb) {
    if (window.React) return cb(window.React);
    var n = 0;
    (function tick() {
      if (window.React) return cb(window.React);
      if (++n > 600) return console.error('[ds] React not available');
      setTimeout(tick, 50);
    })();
  }

  function cls() {
    return Array.prototype.join.call(arguments, ' ');
  }

  whenReact(function (React) {
    var h = React.createElement;

    function Button(props) {
      var variant = props.variant || 'primary';
      var size = props.size || 'md';
      var classes = cls(
        'ds-btn',
        'ds-btn--' + variant,
        'ds-btn--' + size,
        props.pill ? 'ds-btn--pill' : '',
        props.block ? 'ds-btn--block' : ''
      );
      return h('button', {
        type: props.type || 'button',
        className: classes,
        onClick: props.onClick,
        children: props.children
      });
    }

    function Input(props) {
      return h('label', { className: 'ds-field' }, [
        props.label ? h('span', { className: 'ds-label', children: props.label }) : null,
        h('input', {
          className: 'ds-input',
          type: props.type || 'text',
          value: props.value || '',
          placeholder: props.placeholder || '',
          onChange: props.onChange
        })
      ]);
    }

    function Select(props) {
      var options = props.options || [];
      return h('label', { className: 'ds-field' }, [
        props.label ? h('span', { className: 'ds-label', children: props.label }) : null,
        h('select', {
          className: 'ds-select',
          value: props.value || '',
          onChange: props.onChange,
          children: options.map(function (o) {
            return h('option', { key: o.value, value: o.value, children: o.label });
          })
        })
      ]);
    }

    function Textarea(props) {
      return h('label', { className: 'ds-field' }, [
        props.label ? h('span', { className: 'ds-label', children: props.label }) : null,
        h('textarea', {
          className: 'ds-textarea',
          rows: props.rows || 3,
          value: props.value || '',
          placeholder: props.placeholder || '',
          onChange: props.onChange
        })
      ]);
    }

    window.ShirapaperDesignSystem_44268b = {
      Button: Button,
      Input: Input,
      Select: Select,
      Textarea: Textarea
    };
  });
})();
""",
        encoding="utf-8",
    )


def decode_manifest_entry(entry: dict) -> bytes:
    data = base64.b64decode(entry["data"])
    if entry.get("compressed"):
        data = gzip.decompress(data)
    return data


def extract_and_optimize_images(manifest: dict) -> dict[str, str]:
    ASSETS.mkdir(parents=True, exist_ok=True)
    mapping = {
        UUID_LOGO: "logo.png",
        UUID_STORY: "story.jpg",
        UUID_HERO: "hero.jpg",
    }
    paths: dict[str, str] = {}

    if all(uuid in manifest for uuid in mapping):
        for uuid, filename in mapping.items():
            out = ASSETS / filename
            out.write_bytes(decode_manifest_entry(manifest[uuid]))
            paths[uuid] = f"assets/{filename}"

        gallery_sources = [
            ("g1-album.jpg", "story.jpg"),
            ("g2-calendar.jpg", "hero.jpg"),
            ("g3-box.jpg", "story.jpg"),
            ("g4-group.jpg", "hero.jpg"),
            ("g5-cards.jpg", "story.jpg"),
            ("g6-family.jpg", "hero.jpg"),
        ]
        for name, src_name in gallery_sources:
            shutil.copyfile(ASSETS / src_name, ASSETS / name)
    else:
        hero = "assets/hero.webp" if (ASSETS / "hero.webp").exists() else "assets/hero.jpg"
        story = "assets/story.webp" if (ASSETS / "story.webp").exists() else "assets/story.jpg"
        paths = {
            UUID_LOGO: "assets/logo.png",
            UUID_STORY: story,
            UUID_HERO: hero,
        }

    for img in ASSETS.glob("*.jpg"):
        subprocess.run(
            ["sips", "-Z", "1200", "-s", "format", "jpeg", "-s", "formatOptions", "80", str(img), "--out", str(img)],
            check=False,
            capture_output=True,
        )

    hero = ASSETS / "hero.jpg"
    subprocess.run(
        ["sips", "-Z", "1400", "-s", "format", "jpeg", "-s", "formatOptions", "72", str(hero), "--out", str(hero)],
        check=False,
        capture_output=True,
    )

    webp_bin = shutil.which("cwebp")
    if webp_bin:
        for jpg in ASSETS.glob("*.jpg"):
            webp = jpg.with_suffix(".webp")
            subprocess.run([webp_bin, "-q", "82", str(jpg), "-o", str(webp)], check=False, capture_output=True)
        paths[UUID_HERO] = "assets/hero.webp"
        paths[UUID_STORY] = "assets/story.webp"

    return paths


def seo_head_block() -> str:
    return f"""{shell_json_ld()}
<title>{SITE_TITLE}</title>
<meta name="description" content="{SITE_DESC}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{SITE_URL}/">
<meta property="og:type" content="website">
<meta property="og:locale" content="he_IL">
<meta property="og:url" content="{SITE_URL}/">
<meta property="og:title" content="{SITE_TITLE}">
<meta property="og:description" content="{SITE_DESC}">
<meta property="og:image" content="{SITE_URL}/assets/hero-collage.webp">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{SITE_TITLE}">
<meta name="twitter:description" content="{SITE_DESC}">
<meta name="twitter:image" content="{SITE_URL}/assets/hero-collage.webp">"""


def shell_json_ld() -> str:
    faq_entities = ",\n    ".join(
        json.dumps(
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            },
            ensure_ascii=False,
        )
        for q, a in FAQ_JSON_LD
    )
    return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "LocalBusiness",
      "name": "שירה בנייר",
      "description": {json.dumps(SITE_DESC, ensure_ascii=False)},
      "url": {json.dumps(SITE_URL)},
      "image": {json.dumps(SITE_URL + '/assets/hero-collage.webp')},
      "telephone": "+972-50-4417031",
      "address": {{
        "@type": "PostalAddress",
        "addressLocality": "קלע אלון",
        "addressRegion": "צפון הגולן",
        "addressCountry": "IL"
      }},
      "sameAs": [
        "https://www.instagram.com/shira_papers/",
        "https://www.facebook.com/shirapaper"
      ]
    }},
    {{
      "@type": "FAQPage",
      "mainEntity": [
    {faq_entities}
      ]
    }}
  ]
}}
</script>"""


def patch_template(tpl: str, image_paths: dict[str, str]) -> str:
    tpl = tpl.replace("<html><head>", '<html lang="he" dir="rtl"><head>', 1)

    helmet_insert = seo_head_block() + "\n"
    tpl = tpl.replace("<helmet>\n\n\n\n\n\n", "<helmet>\n" + helmet_insert, 1)

    tpl = tpl.replace(
        '<section style="background:var(--surface-sunken); padding:clamp(48px,8vw,96px) clamp(18px,5vw,40px);">\n    <div style="max-width:1120px; margin:0 auto;">\n      <div data-anim="" style="text-align:center; max-width:640px; margin:0 auto 40px;">\n        <span style="display:inline-block; font-family:var(--font-ui); font-weight:700; font-size:13px; letter-spacing:.08em; color:var(--pink-600); margin-bottom:12px;">גלריית השראה</span>',
        '<section id="gallery" style="background:var(--surface-sunken); padding:clamp(48px,8vw,96px) clamp(18px,5vw,40px);">\n    <div style="max-width:1120px; margin:0 auto;">\n      <div data-anim="" style="text-align:center; max-width:640px; margin:0 auto 40px;">\n        <span style="display:inline-block; font-family:var(--font-ui); font-weight:700; font-size:13px; letter-spacing:.08em; color:var(--pink-600); margin-bottom:12px;">גלריית השראה</span>',
        1,
    )

    tpl = tpl.replace(
        '<section style="background:var(--surface-sunken); padding:clamp(48px,8vw,96px) clamp(18px,5vw,40px);">\n    <div style="max-width:760px; margin:0 auto;">\n      <div data-anim="" style="text-align:center; margin:0 auto 40px;">\n        <span style="display:inline-block; font-family:var(--font-ui); font-weight:700; font-size:13px; letter-spacing:.08em; color:var(--pink-600); margin-bottom:12px;">שאלות נפוצות</span>',
        '<section id="faq" style="background:var(--surface-sunken); padding:clamp(48px,8vw,96px) clamp(18px,5vw,40px);">\n    <div style="max-width:760px; margin:0 auto;">\n      <div data-anim="" style="text-align:center; margin:0 auto 40px;">\n        <span style="display:inline-block; font-family:var(--font-ui); font-weight:700; font-size:13px; letter-spacing:.08em; color:var(--pink-600); margin-bottom:12px;">שאלות נפוצות</span>',
        1,
    )

    tpl = tpl.replace(
        '<a href="#form" style="text-decoration:none; color:var(--pink-200); font-size:14px;">גלריית השראה</a>',
        '<a href="#gallery" style="text-decoration:none; color:var(--pink-200); font-size:14px;">גלריית השראה</a>',
    )
    tpl = tpl.replace(
        '<a href="#form" style="text-decoration:none; color:var(--pink-200); font-size:14px;">שאלות נפוצות</a>',
        '<a href="#faq" style="text-decoration:none; color:var(--pink-200); font-size:14px;">שאלות נפוצות</a>',
    )

    for uuid, path in image_paths.items():
        tpl = tpl.replace(uuid, path)

    return tpl


def patch_bundler(html: str) -> str:
    needle = "    for (const old of dead) {\n      const s = document.createElement('script');"
    insert = "    for (const old of dead) {\n      if (old.type === 'application/ld+json') continue;\n      const s = document.createElement('script');"
    if needle not in html:
        raise SystemExit("Could not patch bundler script loop")
    return html.replace(needle, insert, 1)


def patch_shell(html: str) -> str:
    html = re.sub(
        r"<html>\s*<head>\s*<meta charset=\"utf-8\">\s*<title>Bundled Page</title>",
        f'<html lang="he" dir="rtl">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n  <title>{SITE_TITLE}</title>\n  <meta name="description" content="{SITE_DESC}">\n  <link rel="canonical" href="{SITE_URL}/">',
        html,
        count=1,
    )
    return html


def read_script_json(content: str, script_type: str) -> dict | str:
    open_tag = f'<script type="{script_type}">'
    start = content.find(open_tag)
    if start < 0:
        raise SystemExit(f"Missing {script_type} in index.html")
    json_start = start + len(open_tag)
    end = content.find("</script>", json_start)
    raw = content[json_start:end].strip().replace("<\\/", "</")
    return json.loads(raw)


def write_script_json(content: str, script_type: str, data: dict | str) -> str:
    open_tag = f'<script type="{script_type}">'
    start = content.find(open_tag)
    json_start = start + len(open_tag)
    end = content.find("</script>", json_start)
    payload = json.dumps(data, ensure_ascii=True).replace("</", "<\\/")
    return content[:json_start] + "\n" + payload + "\n  " + content[end:]


def main() -> None:
    write_design_system()
    content = INDEX.read_text(encoding="utf-8")

    manifest = read_script_json(content, "__bundler/manifest")
    tpl = read_script_json(content, "__bundler/template")

    image_paths = extract_and_optimize_images(manifest)
    for uuid in (UUID_LOGO, UUID_STORY, UUID_HERO):
        manifest.pop(uuid, None)

    tpl = patch_template(tpl, image_paths)
    content = patch_shell(content)
    content = patch_bundler(content)
    content = write_script_json(content, "__bundler/manifest", manifest)
    content = write_script_json(content, "__bundler/template", tpl)

    INDEX.write_text(content, encoding="utf-8")
    print(f"Built design system at {DS_DIR}")
    print(f"Assets in {ASSETS}")
    print(f"index.html size: {INDEX.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
