#!/usr/bin/env python3
import base64,hashlib
from pathlib import Path
from pypdf import PdfReader
import fitz
root=Path(__file__).resolve().parents[1]
partdir=root/'examples/native-parts'
expected={
 50:('e3c68507e9bf4fa4453cd3fa836a4119d84c8346c3827203bcb6310275fde0bb',6608213),
 25:('bf69e6289f3e10049ad2f34ed0fb352c589d759230f96aaa4039198bd6996e10',6802841)}
for age,(checksum,length) in expected.items():
 pieces=sorted(partdir.glob(f'age-{age}-*.b64'))
 assert len(pieces)==10
 data=base64.b64decode(''.join(p.read_text().strip() for p in pieces),validate=True)
 actual=hashlib.sha256(data).hexdigest()
 print(f'CHECK age={age} actualSize={len(data)} expectedSize={length} actualSHA={actual} expectedSHA={checksum}',flush=True)
 assert len(data)==length,(age,len(data),length)
 assert actual==checksum,(age,actual,checksum)
 pdf=root/f'examples/mws-native-age-{age}-usd-20261014.pdf'
 pdf.write_bytes(data)
 reader=PdfReader(pdf)
 assert reader.is_encrypted and reader.decrypt('MWS-DEMO-2026')
 assert len(reader.pages)>8
 doc=fitz.open(pdf)
 assert doc.authenticate('MWS-DEMO-2026')
 # The native v3.1.2 image report is used in full. The original first-page
 # total-bar captions overlap at this paper width; repaint those two boxes.
 page=doc[0]
 sx=page.rect.width/1240
 sy=page.rect.height/1754
 def panel(x,y,width,height):
  return fitz.Rect(x*sx,y*sy,(x+width)*sx,(y+height)*sy)
 totalY=410+(860-86-6)+6
 left=panel(190,totalY,427,86)
 right=panel(623,totalY,427,86)
 for rectangle in (left,right):
  page.draw_rect(rectangle,color=(.09,.23,.36),fill=(.929,.953,.984),width=.4,overlay=True)
 captions=[
  ('Assets = USD '+format(1480000 if age==50 else 90000,',.0f'),left),
  ('Liabilities + equity = USD '+format(1480000 if age==50 else 90000,',.0f'),right)
 ]
 for caption,rectangle in captions:
  inner=fitz.Rect(rectangle.x0+2,rectangle.y0+4,rectangle.x1-2,rectangle.y1-2)
  remaining=page.insert_textbox(inner,caption,fontname='helv',fontsize=8,color=(.09,.23,.36),align=1,overlay=True)
  assert remaining>=0,(age,caption,remaining)
 fixed=root/f'examples/mws-native-age-{age}-usd-v2.pdf'
 doc.save(fixed,encryption=fitz.PDF_ENCRYPT_AES_256,user_pw='MWS-DEMO-2026',owner_pw='MWS-DEMO-2026-OWNER',garbage=4,deflate=True)
 confirm=fitz.open(fixed)
 assert confirm.is_encrypted and confirm.authenticate('MWS-DEMO-2026')
 assert confirm.page_count==doc.page_count
 for section,index in [('cover',0),('inventory',2)]:
  preview=root/f'examples/previews/native-age-{age}-{section}.png'
  doc[index].get_pixmap(matrix=fitz.Matrix(.8,.8)).save(preview)
 print(f'PASS age={age}, pages={doc.page_count}, bytes={len(data)}')
