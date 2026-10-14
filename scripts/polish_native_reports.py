#!/usr/bin/env python3
"""Polish the existing native MWS PDF cover footer; preserve all native report pages.

Originals are native v3.1.2 exporter files. The native image-rendered totals
on page 1 overlap within two 50%-width cells at some currency lengths.
Correct only those two footer labels and re-encrypt into cache-busting v2 files.
"""
from pathlib import Path
import fitz
from pypdf import PdfReader

BASE=Path(__file__).resolve().parents[1]/'examples'
PREVIEWS=BASE/'previews'
PREVIEWS.mkdir(exist_ok=True)
PASSWORD='MWS-DEMO-2026'
NAVY=(24/255,58/255,93/255)
PALE=(237/255,243/255,251/255)

for age,asset in [(50,'USD 1.48m'),(25,'USD 90.0k')]:
    source=BASE/f'mws-native-age-{age}-usd-20261014.pdf'
    target=BASE/f'mws-native-age-{age}-usd-20261014-v2.pdf'
    pdf=fitz.open(source)
    assert pdf.is_encrypted and pdf.authenticate(PASSWORD)
    assert pdf.page_count >= 8
    cover=pdf[0]
    assert abs(cover.rect.width-595.28)<2 and abs(cover.rect.height-841.89)<2,(cover.rect,age)
    # Coordinates refer to the actual A4 page of the native MWS wealth-square export.
    cells=[fitz.Rect(90,568,299,610),fitz.Rect(299,568,506,610)]
    for rect in cells:
        cover.draw_rect(rect,color=NAVY,fill=PALE,width=1.1,overlay=True)
    labels=[f'Total Assets = {asset}',f'Liabilities + Net Worth = {asset}']
    for rect,label in zip(cells,labels):
        usable=fitz.Rect(rect.x0+5,rect.y0+5,rect.x1-5,rect.y1-3)
        size=10.0
        while size>=7:
            line=fitz.get_text_length(label,fontname='hebo',fontsize=size)
            if line <= usable.width:break
            size-=0.25
        rc=cover.insert_textbox(usable,label,fontname='hebo',fontsize=size,
                                lineheight=1.1,color=NAVY,align=1,overlay=True)
        assert rc >= 0,(age,label,rc)
    # Preview the full native first page and native Wealth Inventory (page three).
    for section,index in [('cover',0),('inventory',2)]:
        pdf[index].get_pixmap(matrix=fitz.Matrix(.8,.8),alpha=False).save(
             PREVIEWS/f'native-age-{age}-{section}-v2.png')
    pdf.save(target,garbage=3,deflate=True,encryption=fitz.PDF_ENCRYPT_AES_256,
             user_pw=PASSWORD,owner_pw='DEMO-MWS-OWNER-2026')
    pdf.close()
    chk=PdfReader(target)
    assert chk.is_encrypted and chk.decrypt(PASSWORD)
    assert len(chk.pages)>=8
    print('PASS',age,'pages',len(chk.pages),'bytes',target.stat().st_size)
print('NATIVE_MWS_SAMPLES_V2_READY')
