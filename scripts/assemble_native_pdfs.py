#!/usr/bin/env python3
import base64,hashlib
from pathlib import Path
from pypdf import PdfReader
import fitz
root=Path(__file__).resolve().parents[1]
partdir=root/'examples/native-parts'
expected={
 50:('4c870519e50eafcdc96fd6a3d58a5f5e51b53a3b89f066372b3c2a19c8134d3a',6608213),
 25:('fd8514209a2a6fb9cbe23db2914aa9415d95b8fc3eda2da00d2999f781c0cd22',6802841)}
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
 for section,index in [('cover',0),('inventory',2)]:
  preview=root/f'examples/previews/native-age-{age}-{section}.png'
  doc[index].get_pixmap(matrix=fitz.Matrix(.8,.8)).save(preview)
 print(f'PASS age={age}, pages={doc.page_count}, bytes={len(data)}')
