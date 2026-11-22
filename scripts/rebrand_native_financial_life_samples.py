#!/usr/bin/env python3
"""Rebrand fictional native PDF *presentation* without changing projected values.

Original native report pages are image-based, not searchable PDF text.
Only the report title strips and the outdated FI status/explanation on the
single Financial Life Simulator summary page are overlaid. All numeric grids,
tables, transactions and assumptions remain unchanged.
"""
from __future__ import annotations

import base64
import csv
import io
import re
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import fitz

ROOT=Path(__file__).resolve().parents[1]
PASSWORD='MWS-DEMO-2026'
TITLE_OLD=['financial','independence','planning','report']
TITLE_NEW='Financial Life Planning Report'
PDF_SEGMENTS={50:range(10,28),25:range(5,26)}  # zero-based; validated against the original PDFs
SUMMARY_PAGE={50:10,25:5}
QA=ROOT/'qa'/'financial-life'
QA.mkdir(parents=True,exist_ok=True)

def ocr_words(page:fitz.Page,clip:fitz.Rect,scale=2.5):
    pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),clip=clip,
                       colorspace=fitz.csRGB,alpha=False)
    run=subprocess.run(['tesseract','stdin','stdout','--psm','6','tsv'],
                       input=pix.tobytes('png'),capture_output=True,check=True)
    result=[]
    for item in csv.DictReader(io.StringIO(run.stdout.decode(errors='replace')),delimiter='\t'):
        word=(item.get('text') or '').strip()
        if not word or float(item.get('conf') or -1)<0:continue
        x=float(item['left'])/scale+clip.x0
        y=float(item['top'])/scale+clip.y0
        w=float(item['width'])/scale
        h=float(item['height'])/scale
        result.append({'word':word,'token':re.sub('[^a-z]','',word.lower()),
                       'rect':fitz.Rect(x,y,x+w,y+h),
                       'group':(item['block_num'],item['par_num'],item['line_num'])})
    return result

def group_lines(words):
    lines=defaultdict(list)
    for word in words:lines[word['group']].append(word)
    return [sorted(items,key=lambda x:x['rect'].x0) for items in lines.values()]

def sequence_bbox(words,tokens):
    for line in group_lines(words):
        names=[x['token'] for x in line]
        for i in range(len(names)-len(tokens)+1):
            if names[i:i+len(tokens)]==tokens:
                points=[x['rect'] for x in line[i:i+len(tokens)]]
                return fitz.Rect(min(x.x0 for x in points),min(x.y0 for x in points),
                                 max(x.x1 for x in points),max(x.y1 for x in points))
    raise ValueError(f'Cannot locate exact words: {tokens}; OCR lines='+
                     repr([' '.join(x['word'] for x in line) for line in group_lines(words)]))

def background(page:fitz.Page,area:fitz.Rect):
    # Native exporter uses flat filled title strips; choose the modal dark/teal
    # background pixel rather than a guess based on a screenshot.
    clip=fitz.Rect(max(0,area.x0),max(0,area.y0),
                   min(page.rect.width,area.x1),min(page.rect.height,area.y1))
    pix=page.get_pixmap(matrix=fitz.Matrix(1,1),clip=clip,
                        colorspace=fitz.csRGB,alpha=False)
    candidates=[]
    for y in range(1,pix.height-1,2):
        for x in range(1,pix.width-1,2):
            r,g,b=pix.pixel(x,y)[:3]
            candidates.append((r//4,g//4,b//4))
    if not candidates:
        raise ValueError('No suitable filled background pixels in '+str(area))
    key=Counter(candidates).most_common(1)[0][0]
    near=[(r*4,g*4,b*4) for r,g,b in candidates if (r,g,b)==key]
    rgb=tuple(statistics.median(v[i] for v in near)/255 for i in range(3))
    return rgb

def relabel_header(page:fitz.Page,age:int,index:int):
    words=ocr_words(page,fitz.Rect(0,0,page.rect.width,88))
    box=sequence_bbox(words,TITLE_OLD)
    if box.x0<12 or box.y0>50:
        raise ValueError(f'Unexpected title geometry age={age} page={index+1} box={box}')
    patch=fitz.Rect(box.x0-3,box.y0-3,box.x1+4,box.y1+3)
    color=background(page,patch)
    page.draw_rect(patch,color=None,fill=color,overlay=True)
    size=min(21.0,max(16.0,box.height*1.12))
    line_width=fitz.get_text_length(TITLE_NEW,fontname='hebo',fontsize=size)
    if box.x0+line_width >=page.rect.width-55:
        raise ValueError(f'Header replacement overflows page {age}/{index+1}')
    page.insert_text(fitz.Point(box.x0,box.y1+1.0),TITLE_NEW,
                     fontname='hebo',fontsize=size,color=(1,1,1),overlay=True)
    print('HEADER_UPDATED',age,index+1,'old_box',tuple(round(v,1) for v in box),
          'font',round(size,1),'bg',tuple(round(v,3) for v in color),flush=True)

def patch_summary(page:fitz.Page,age:int,index:int):
    words=ocr_words(page,fitz.Rect(25,98,page.rect.width-26,192),scale=3)
    label=sequence_bbox(words,['financial','independent'])
    status=sequence_bbox(words,['not','reached'])
    all_box=fitz.Rect(min(label.x0,status.x0)-4,min(label.y0,status.y0)-3,
                      max(label.x1,status.x1)+9,max(label.y1,status.y1)+3)
    if not(95<all_box.y0<145 and all_box.y1<183):
        raise ValueError(f'Unexpected status geometry {age}: {all_box}')
    teal=background(page,all_box)
    page.draw_rect(all_box,color=None,fill=teal,overlay=True)
    page.insert_text(fitz.Point(label.x0,label.y1+1),'Financial Life',
                     fontname='hebo',fontsize=12,color=(1,1,1),overlay=True)
    page.insert_text(fitz.Point(status.x0,status.y1+1),'Plan scenarios',
                     fontname='hebo',fontsize=min(22,max(18,status.height*1.05)),
                     color=(1,1,1),overlay=True)

    # Also retire the sentence defining FI eligibility, not just its badge.
    description=ocr_words(page,fitz.Rect(20,191,page.rect.width-20,242),scale=3)
    old_lines=[]
    for line in group_lines(description):
        tokens={w['token'] for w in line}
        if tokens.intersection({'earliest','passive','earned','sustainability','guarantee','projected'}):
            old_lines.extend(w['rect'] for w in line)
    if not old_lines:
        raise ValueError(f'Cannot verify outdated FI explanatory sentence age={age}')
    desc=fitz.Rect(25,min(x.y0 for x in old_lines)-2,
                   page.rect.width-25,max(x.y1 for x in old_lines)+3)
    if desc.y1>242:raise ValueError(f'Description mask might cover 3x3 title: {desc}')
    paper=background(page,desc)
    page.draw_rect(desc,color=None,fill=paper,overlay=True)
    newcopy='Financial life scenarios use your selected spending and fund assumptions.\nProjected figures are illustrative, not guarantees.'
    written=page.insert_textbox(
        fitz.Rect(desc.x0+1,desc.y0,desc.x1-1,desc.y1+1),
        newcopy,fontname='hebo',fontsize=9.0,lineheight=1.17,
        color=(.35,.41,.47),overlay=True)
    if written<0:raise ValueError(f'Description text does not fit age={age}: {written}')
    print('SUMMARY_UPDATED',age,index+1,
          'status_box',tuple(round(v,1) for v in all_box),
          'description_box',tuple(round(v,1) for v in desc),flush=True)

def verify(doc:fitz.Document,age:int):
    assert doc.page_count==31
    for index in PDF_SEGMENTS[age]:
        page=doc[index]
        header=ocr_words(page,fitz.Rect(0,0,page.rect.width,88))
        try:sequence_bbox(header,['financial','life','planning','report'])
        except ValueError as e:raise AssertionError(f'New heading not visible {age}/{index+1}: {e}')
        try:sequence_bbox(header,TITLE_OLD)
        except ValueError:pass
        else:raise AssertionError(f'Old title visible {age}/{index+1}')
    page=doc[SUMMARY_PAGE[age]]
    words=ocr_words(page,fitz.Rect(25,98,page.rect.width-25,192),scale=3)
    sequence_bbox(words,['financial','life'])
    try:sequence_bbox(words,['not','reached'])
    except ValueError:pass
    else:raise AssertionError(f'Old FI status visible for age {age}')
    # Grid area unaffected: pixel-rendered output below the edited note must be
    # byte-identical to the source page, including every amount and age.
    source=fitz.open(ROOT/f'examples/mws-native-age-{age}-usd-20261014-v2.pdf')
    assert source.authenticate(PASSWORD)
    before=source[SUMMARY_PAGE[age]].get_pixmap(
       matrix=fitz.Matrix(1,1),
       clip=fitz.Rect(0,260,page.rect.width,page.rect.height),alpha=False)
    after=page.get_pixmap(matrix=fitz.Matrix(1,1),
       clip=fitz.Rect(0,260,page.rect.width,page.rect.height),alpha=False)
    assert before.samples==after.samples,'3x3 grid or lower report content was modified'

for age in (50,25):
    original=ROOT/f'examples/mws-native-age-{age}-usd-20261014-v2.pdf'
    out=ROOT/f'examples/mws-native-age-{age}-usd-20261014-v3.pdf'
    doc=fitz.open(original)
    assert doc.is_encrypted and doc.authenticate(PASSWORD)
    assert doc.page_count==31
    for index in PDF_SEGMENTS[age]:relabel_header(doc[index],age,index)
    patch_summary(doc[SUMMARY_PAGE[age]],age,SUMMARY_PAGE[age])
    verify(doc,age)
    meta=doc.metadata
    meta['title']=f'My Wealth Square - Financial Life Planning - fictional age {age} sample'
    meta['subject']='Fictional encrypted USD sample; presentation-only Financial Life terminology'
    doc.set_metadata(meta)
    doc.save(out,garbage=4,deflate=True,
             encryption=fitz.PDF_ENCRYPT_AES_256,
             user_pw=PASSWORD,owner_pw='MWS-DEMO-2026-OWNER')
    check=fitz.open(out)
    assert check.is_encrypted and check.authenticate(PASSWORD) and check.page_count==31
    verify(check,age)
    summary=check[SUMMARY_PAGE[age]]
    clip=fitz.Rect(0,0,summary.rect.width,255)
    pix=summary.get_pixmap(matrix=fitz.Matrix(1.6,1.6),clip=clip,alpha=False)
    (QA/f'age-{age}-summary-preview.b64').write_text(
        base64.b64encode(pix.tobytes('png')).decode('ascii'))
    print('VERIFIED',age,'pages',check.page_count,'bytes',out.stat().st_size,
          'password_protected',True,flush=True)
print('BOTH_FINANCIAL_LIFE_PDFS_READY')
