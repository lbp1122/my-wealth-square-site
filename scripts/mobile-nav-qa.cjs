const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
const languages=['en','bm','zh','zh-TW','th','ja','ko','vi'];
const widths=[320,360,393];
(async()=>{
 const browser=await chromium.launch({headless:true});
 const output=path.join('examples','previews');fs.mkdirSync(output,{recursive:true});
 const failures=[];
 try{
  for(const width of widths){
   const page=await browser.newPage({viewport:{width,height:740},deviceScaleFactor:1});
   for(const lang of languages){
    const url='http://127.0.0.1:8777/index.html?lang='+encodeURIComponent(lang);
    await page.goto(url,{waitUntil:'load'});
    const nav=await page.locator('.nav .links a').evaluateAll(elements=>{
     const measure=document.createElement('canvas').getContext('2d');
     return elements.map(el=>{
      const box=el.getBoundingClientRect();
      const style=getComputedStyle(el,'::after');
      const text=style.content.replace(/^["']|["']$/g,'');
      measure.font=style.font;
      return {top:box.top,left:box.left,right:box.right,width:box.width,
        label:text,visibleWidth:measure.measureText(text).width};
     });
    });
    if(nav.length!==5)failures.push(width+' '+lang+': expected five navigation items');
    if(nav.length===5){
     const maxTop=Math.max(...nav.map(x=>x.top)),minTop=Math.min(...nav.map(x=>x.top));
     if(maxTop-minTop>1)failures.push(width+' '+lang+': navigation wrapped into multiple rows');
     for(let i=0;i<nav.length;i++){
      const x=nav[i];
      if(x.visibleWidth>x.width-1)failures.push(width+' '+lang+': label '+x.label+' clipped by '+(x.visibleWidth-x.width).toFixed(1)+'px');
      if(x.left<0||x.right>width+1)failures.push(width+' '+lang+': link outside viewport');
     }
    }
    if(width===320&&['en','bm','vi','th'].includes(lang)){
      await page.screenshot({path:path.join(output,'nav-320-'+lang+'.png'),clip:{x:0,y:0,width,height:190}});
    }
   }
   await page.close();
  }
 }finally{await browser.close();}
 if(failures.length){console.error(failures.join('\n'));process.exit(1);}
 console.log('PASS: five mobile links fit one row and are not clipped across eight languages at 320, 360 and 393px');
})().catch(e=>{console.error(e);process.exit(1);});
