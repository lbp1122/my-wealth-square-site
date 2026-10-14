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
