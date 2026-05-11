#!/usr/bin/env python3
"""Build Komento language pack ZIPs — one per locale, with Joomla XML manifest."""

import re
import zipfile
from datetime import date
from pathlib import Path

DIST = Path('dist')
DIST.mkdir(exist_ok=True)

LANG_NAMES = {
    "ar-SA": "Arabic",                  "bg-BG": "Bulgarian",
    "ca-ES": "Catalan",                 "cs-CZ": "Czech",
    "da-DK": "Danish",                  "de-DE": "German",
    "el-GR": "Greek",                   "es-ES": "Spanish",
    "et-EE": "Estonian",                "fa-IR": "Persian",
    "fi-FI": "Finnish",                 "fr-FR": "French",
    "hu-HU": "Hungarian",               "it-IT": "Italian",
    "nb-NO": "Norwegian",               "nl-NL": "Dutch",
    "pl-PL": "Polish",                  "pt-BR": "Portuguese (Brazil)",
    "pt-PT": "Portuguese",
    "ro-RO": "Romanian",                "ru-RU": "Russian",
    "sk-SK": "Slovak",                  "sr-Cyrl": "Serbian",
    "sv-SE": "Swedish",                 "tr-TR": "Turkish",
    "vi-VN": "Vietnamese",              "zh-CN": "Chinese (Simplified)",
}

VERSION      = "5.0.1"
CREATED      = date.today().strftime("%-d %B %Y")
AUTHOR       = "CRE8"
AUTHOR_URL   = "https://cre8.social"
AUTHOR_EMAIL = "support@birdgraphics.ch"


def make_manifest(locale: str, name: str, admin_files: list, site_files: list) -> str:
    def file_tags(files):
        return "\n".join(f"            <filename>{f}</filename>" for f in files)

    return f"""<?xml version="1.0" encoding="utf-8"?>
<extension type="file" version="3.0.0" method="upgrade">
\t<name>Komento - Language Pack {name} ({locale})</name>
\t<version>{VERSION}</version>
\t<creationDate>{CREATED}</creationDate>
\t<author>{AUTHOR}</author>
\t<authorEmail>{AUTHOR_EMAIL}</authorEmail>
\t<authorUrl>{AUTHOR_URL}</authorUrl>
\t<copyright>Copyright {date.today().year} {AUTHOR}. All rights reserved.</copyright>
\t<license>GPL License</license>
\t<description>{name} Language Pack for Komento {VERSION}</description>
\t<fileset>
\t\t<files folder="administrator/language/{locale}" target="administrator/language/{locale}">
{file_tags(admin_files)}
\t\t</files>
\t\t<files folder="language/{locale}" target="language/{locale}">
{file_tags(site_files)}
\t\t</files>
\t</fileset>
</extension>
"""


locales = sorted([
    d.name for d in Path('language').iterdir()
    if d.is_dir()
    and d.name != 'en-GB'
    and re.match(r'^([a-z]{2}-[A-Z]{2}|[a-z]{2}Cyrl)$', d.name)
])

for locale in locales:
    name = LANG_NAMES.get(locale, locale)

    site_dir  = Path('language') / locale
    admin_dir = Path('administrator') / 'language' / locale

    site_files  = sorted(f.name for f in site_dir.iterdir())  if site_dir.exists()  else []
    admin_files = sorted(f.name for f in admin_dir.iterdir()) if admin_dir.exists() else []

    manifest = make_manifest(locale, name, admin_files, site_files)
    manifest_name = f'komento_{locale}.xml'

    zip_path = DIST / f'com_komento_{locale}.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(manifest_name, manifest)
        for f in sorted(site_dir.iterdir()) if site_dir.exists() else []:
            zf.write(f, f'language/{locale}/{f.name}')
        for f in sorted(admin_dir.iterdir()) if admin_dir.exists() else []:
            zf.write(f, f'administrator/language/{locale}/{f.name}')

    print(f'Built {zip_path.name}  ({zip_path.stat().st_size:,} bytes)')

print(f'\nTotal: {len(locales)} language packs')
