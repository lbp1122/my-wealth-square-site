#!/usr/bin/env python3
"""Checks actual app-generated encrypted reports; writes page previews."""
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'examples'/'localized'
PREV=ROOT/'examples'/'previews'
PREV.mkdir(parents=True,exist_ok=True)
LANGUAGES=['en','bm','zh','zh-TW','th','ja','ko','vi']
for lang in LANGUAGES:
    manifest=DIR/f'manifest-{lang}.json'
    if manifest.exists():
        m=json.loads(manifest.read_text())
        assert m['currency']=='USD' and m['language']==lang, (lang,m)
    for age,expected in [(50,1000000),(25,50000)]:
        path=DIR/f'mws-native-age-{age}-usd-{lang}.pdf'
        assert path.exists(), f'Missing {path}'
        doc=fitz.open(path)
        assert doc.is_encrypted and doc.authenticate('MWS-DEMO-2026'),f'Password error {path}'
        assert doc.page_count>=8,f'Incomplete document {path}: {doc.page_count}'
        for name,idx in [('cover',0),('inventory',2)]:
            out=PREV/f'native-age-{age}-{lang}-{name}.png'
            doc[idx].get_pixmap(matrix=fitz.Matrix(.8,.8),alpha=False).save(out)
        print(f'PASS lang={lang} age={age} pages={doc.page_count} bytes={path.stat().st_size} expected_nw={expected}',flush=True)
        doc.close()
print('SIXTEEN_LANGUAGE_SAMPLES_VERIFIED')
