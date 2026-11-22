import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve, join } from 'node:path';
import { mkdirSync } from 'node:fs';

const languages = ['en','bm','zh','zh-TW','th','ja','ko','vi'];
const sizes = [320,360,390,768,1280];
const files = ['index.html','sample-reports.html'];
const browsers = await chromium.launch({headless:true});
mkdirSync('qa/screenshots',{recursive:true});
let total=0;
const errors=[];
try {
 for (const file of files) {
  for (const lang of languages) {
   for (const width of sizes) {
    const page=await browsers.newPage({viewport:{width,height:900},deviceScaleFactor:1});
    const url=pathToFileURL(resolve(file)).href+'?lang='+encodeURIComponent(lang);
    await page.goto(url,{waitUntil:'load'});
    const info=await page.evaluate(() => {
      const els=Array.from(document.querySelectorAll('body *'));
      const offending=els.filter(el => {
       const r=el.getBoundingClientRect();
       const css=getComputedStyle(el);
       return css.display!=='none' && css.visibility!=='hidden' && r.width>0 && (r.right>innerWidth+2 || r.left< -2);
      }).slice(0,10).map(el=>({tag:el.tagName,cl:el.className,text:(el.textContent||'').slice(0,60),rect:{left:Math.round(el.getBoundingClientRect().left),right:Math.round(el.getBoundingClientRect().right)}}));
      const title=document.querySelector('[data-k="sampleFifty"]')?.textContent||'';
      return {width:document.documentElement.scrollWidth,viewport:innerWidth,lang:document.getElementById('language')?.value||'missing',brand:document.querySelector('.brand span')?.textContent,offending,title,
        rmLabel:document.querySelector('.sample-amount')?.textContent||'',
        englishNotice:document.querySelector('.sample-note span[lang="en"], .sample-language-notice span[lang="en"]')?.textContent||'',
        localizedNotice:document.querySelector('.sample-translated-notice')?.textContent||'',
        localizedHidden:document.querySelector('.sample-translated-notice')?.hidden,
        legacyCards:Array.from(document.querySelectorAll('#legacy .legacy-cards article')).map(a=>({number:a.querySelector('.legacy-card-number')?.textContent.trim(),title:a.querySelector('h4')?.textContent.trim(),body:a.querySelector('p')?.textContent.trim()})),
        multiFeature:{title:document.querySelector('[data-k="fMultiTitle"]')?.textContent||'',body:document.querySelector('[data-k="fMultiBody"]')?.textContent||''},
        featuresOrder:Array.from(document.querySelectorAll('#features .features article h3')).map(h=>h.getAttribute('data-k')),
        backupFeature:{title:document.querySelector('[data-k="f5Title"]')?.textContent||'',body:document.querySelector('[data-k="f5Body"]')?.textContent||''},
        backupExpected:(typeof copy!=='undefined'&&copy[document.getElementById('language')?.value])?{title:copy[document.getElementById('language').value].f5Title,body:copy[document.getElementById('language').value].f5Body}:null,
        multiExpected:(typeof copy!=='undefined'&&copy[document.getElementById('language')?.value])?{title:copy[document.getElementById('language').value].fMultiTitle,body:copy[document.getElementById('language').value].fMultiBody}:null,
        legacyExpected:(typeof copy!=='undefined'&&copy[document.getElementById('language')?.value])? {title:copy[document.getElementById('language').value].legacyDistributionTitle,body:copy[document.getElementById('language').value].legacyDistributionBody,prepare:copy[document.getElementById('language').value].legacyPrepareBody}:null,
        topnav: Array.from(document.querySelectorAll('.links a')).map(a=>{const r=a.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom}})};
    });
    if (info.width > width+2 || info.offending.length) errors.push(file+' '+lang+' '+width+'px overflow: '+JSON.stringify(info).slice(0,550));
    if (info.lang!==lang) errors.push(file+' '+lang+' '+width+'px selection mismatch: '+info.lang);
    if (info.brand!=='My Wealth Square') errors.push(file+' '+lang+' '+width+'px brand changed: '+info.brand);
    if (info.englishNotice!=='Sample PDF reports are all in English and USD, while your actual PDF report follows the language and currency selected in your My Wealth Square app.') errors.push(file+' '+lang+' English notice altered/missing');
    if (info.localizedHidden!==(lang==='en')) errors.push(file+' '+lang+' translation visibility mismatch');
    if (lang!=='en' && (!info.localizedNotice || info.localizedNotice===info.englishNotice)) errors.push(file+' '+lang+' translation missing');
    if (/detailed wealth|building financial foundations/i.test(info.title)) errors.push(file+' '+lang+' old sample title: '+info.title);
    if (file==='sample-reports.html' && (!info.rmLabel.includes('US$')||info.rmLabel.includes('RM'))) errors.push(lang+' non-USD sample label: '+info.rmLabel);
    if (file==='index.html' && width<450 && info.topnav.length===4) {
     const bad=info.topnav.some(r=>r.right>width+2||r.left< -2);
     if(bad) errors.push('nav overflow '+lang+' '+width);
    }
    if(file==='index.html') {
      if(!info.multiExpected || !info.multiFeature.title || info.multiFeature.title!==info.multiExpected.title || info.multiFeature.body!==info.multiExpected.body) errors.push(lang+' '+width+' multi-profile feature translation missing or inconsistent');
      if(info.featuresOrder[1]!=='fMultiTitle') errors.push(lang+' '+width+' five-user feature must appear immediately below Wealth Square');
      if(!info.backupExpected || info.backupFeature.title!==info.backupExpected.title || info.backupFeature.body!==info.backupExpected.body) errors.push(lang+' '+width+' backup/restore translation mismatch');
      if(!info.backupFeature.body.includes('.mwsbackup') || !info.backupFeature.body.includes('Android') || !info.backupFeature.body.includes('iPhone/iPad')) errors.push(lang+' '+width+' cross-platform backup explanation missing');
      if(info.legacyCards.length!==2) errors.push(lang+' '+width+' legacy panel expected 2 cards, got '+info.legacyCards.length);
      else {
        if(info.legacyCards[0].number!=='01'||info.legacyCards[1].number!=='02')errors.push(lang+' '+width+' legacy numbering incorrect');
        if(!info.legacyExpected || info.legacyCards[0].title!==info.legacyExpected.title || info.legacyCards[0].body!==info.legacyExpected.body) errors.push(lang+' '+width+' estate distribution translation mismatch');
        if(info.legacyCards[1].body!==info.legacyExpected?.prepare) errors.push(lang+' '+width+' trusted-person translation mismatch');
      }
    }
    if(lang==='bm' && width===360) await page.screenshot({path:join('qa','screenshots',file+'-bm-360.png'),fullPage:true});
    total++;
    await page.close();
   }
  }
 }
} finally { await browsers.close(); }
console.log('Checked '+total+' language/viewport/page combinations');
if (errors.length) {
 console.error(errors.join('\n'));
 process.exitCode=1;
} else console.log('All website layout checks passed.');
