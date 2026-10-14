/* Generate website PDFs from the native v3.1.2 report exporter.
   Private MWS repo ONLY. This file contains exclusively made-up accounts.
   Run with Playwright + Vite; do not publish app source to the website repo. */
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { createHash } = require('node:crypto');

const SITE_LANG=process.env.MWS_SAMPLE_LANG || 'en';
const APP_LANGUAGE={en:'en',bm:'ms',zh:'zh','zh-TW':'zh-Hant',th:'th',ja:'ja',ko:'ko',vi:'vi'};
if(!Object.hasOwn(APP_LANGUAGE,SITE_LANG))throw Error('Unsupported website language: '+SITE_LANG);
const OUT=path.resolve(process.env.MWS_SAMPLE_OUTPUT || 'scripts/website-demo-output');
// Keep generated output isolated within the language-specific destination.
fs.rmSync(OUT,{recursive:true,force:true});
fs.mkdirSync(OUT,{recursive:true});
const ASSET_KEYS=['cash','investments','privateInvestments','retirement','property','vehicles','otherAssets'];
const DEBT_KEYS=['homeLoan','vehicleLoan','cards','otherDebt'];
const p50 = {
 age:50, name:'Alex Tan',dob:'1976-04-08',job:'Operations Director',retirementAge:62,
 salary:11000,passive:1200,spend:5500,
 assets: {
  cash:[['Everyday checking account',55000],['Fixed deposit account',65000],['Emergency reserve',30000]],
  investments:[['Listed share portfolio',90000],['Global index funds',85000],['Bond and ETF account',55000]],
  privateInvestments:[['Family business stake (30%)',60000],['Partnership investment',40000],['Private loan note',20000]],
  retirement:[['Employer retirement plan',170000],['Individual retirement account',135000],['Retirement savings fund',55000]],
  property:[['Primary residence',320000],['Rental condominium',135000],['Residential land plot',45000]],
  vehicles:[['Family SUV',38000],['Compact sedan',22000],['Motorcycle',10000]],
  otherAssets:[['Gold bullion',25000],['Art and collectibles',15000],['Watch collection',10000]]
 },
 debts:{
  homeLoan:[['Primary residence mortgage',255000],['Condominium mortgage',100000],['Land financing',35000]],
  vehicleLoan:[['SUV financing',20000],['Sedan financing',8000],['Motorcycle loan',4000]],
  cards:[['Credit card A balance',5000],['Credit card B balance',4000],['Personal credit line',4000]],
  otherDebt:[['Business loan',18000],['Education support loan',15000],['Family loan',12000]]
 },
 progress:[
 ['2024-10-14',1220000,530000],['2025-01-14',1260000,527000],['2025-04-14',1300000,523000],
 ['2025-07-14',1340000,515000],['2025-10-14',1380000,508000],['2026-01-14',1415000,500000],
 ['2026-04-14',1440000,494000],['2026-07-14',1460000,487000],['2026-10-14',1480000,480000]
 ],
 spendingChanges:[[55,400],[62,600],[72,-400]],
 events:[[56,'add',40000],[61,'withdraw',60000],[66,'withdraw',25000]]
};
const p25 = {
 age:25,name:'Maya Lim',dob:'2001-03-18',job:'Designer',retirementAge:65,
 salary:5800,passive:150,spend:3000,
 assets:{
  cash:[['Salary account',10000],['Emergency reserve',8000]],
  investments:[['Listed stock ETF',10000],['Index fund',5000]],
  privateInvestments:[],
  retirement:[['Employer retirement plan',21000],['Individual retirement fund',4000]],
  property:[],
  vehicles:[['Used compact car',28000]],
  otherAssets:[['Laptop and professional equipment',4000]]
 },
 debts:{
  homeLoan:[],vehicleLoan:[['Compact car finance',24000]],
  cards:[['Credit card outstanding',1000]],otherDebt:[['Student loan',15000]]
 },
 progress:[
 ['2024-10-14',48000,43000],['2025-01-14',51000,42400],['2025-04-14',55000,42000],
 ['2025-07-14',60000,41700],['2025-10-14',67000,41100],['2026-01-14',73000,40900],
 ['2026-04-14',79000,40500],['2026-07-14',85000,40200],['2026-10-14',90000,40000]
 ],
 spendingChanges:[[30,500],[45,800],[65,-100]],
 events:[[27,'withdraw',6000],[35,'withdraw',18000],[44,'add',10000]]
};
function sum(list){return list.reduce((total,item)=>total+item[1],0);}
function createData(p) {
 const values={monthlyExpenses:p.spend};
 for(const key of ASSET_KEYS) values[key]=sum(p.assets[key]);
 for(const key of DEBT_KEYS) values[key]=sum(p.debts[key]);
 const assets=ASSET_KEYS.reduce((n,key)=>n+values[key],0);
 const liabilities=DEBT_KEYS.reduce((n,key)=>n+values[key],0);
 if(assets-liabilities!== (p.age===50?1000000:50000))throw Error('Net worth mismatch age '+p.age);
 const fictionalBanks=['Northstar Demonstration Bank','Blue Oak Fictional Bank','Maple Example Credit'];
 function details(list,key,isDebt=false) {
   return {holdings:list.map(([displayName,value],index)=>{
     const count=index+1,bank=fictionalBanks[index%3];
     const ref='DEMO-'+p.age+'-'+key.toUpperCase()+'-'+String(count).padStart(3,'0');
     const base={id:ref,displayName,value,currency:'USD',originalValue:value,isActive:true,
         provider:(key==='cash'||isDebt)?bank:key==='investments'?'Example Securities Demo Custody':
         key==='retirement'?'Imaginary Retirement Trust':key==='privateInvestments'?'Fictional Partnership Holdings':'Example Asset Registry',
         branch:'Example Branch '+count,
         reference:'DEMO-ACCT-'+p.age+'-'+String(count).padStart(4,'0')+'-'+key.toUpperCase(),
         notes:'FICTIONAL DEMONSTRATION ONLY - NOT A REAL ACCOUNT / REFERENCE',
         contactPerson:'Sample Contact '+count};
     if(key==='property'){base.address='Fictional '+count+' Example Street, Imaginary District';base.propertyTitleReference='DEMO-TITLE-'+p.age+'-'+count;}
     if(key==='vehicles')base.vehicleRegistration='DEMO-VEH-'+p.age+'-'+count;
     if(key==='privateInvestments'){base.ownershipPercent=count===1?30:20;base.companyRegistration='DEMO-CO-'+p.age+'-'+count;}
     if(key==='otherAssets'){base.insurer='Illustrative Insurance Group';base.insuranceReference='DEMO-INS-'+p.age+'-'+count;}
     if(isDebt)base.creditorName=bank;
     return base;
   }),source:'holdings'};
 }
 const cashInventory=details(p.assets.cash,'cash');
 const assetInventories=Object.fromEntries(ASSET_KEYS.filter(key=>key!=='cash').map(key=>[key,details(p.assets[key],key)]));
 const debtInventories=Object.fromEntries(DEBT_KEYS.map(key=>[key,details(p.debts[key],key,true)]));
 const progressHistory=p.progress.map(([date,assets,liabilities])=>({date,assets,liabilities,equity:assets-liabilities}));
 const input={
   currentAge:p.age,retirementAge:p.retirementAge,planToAge:90,retirementAccessAge:59,
   cashSavings:values.cash,investmentSavings:values.investments,retirementSavings:values.retirement,
   currentMonthlySpending:p.spend,preRetirementExpenses:p.spend,
   inflation:2.75,cashReturn:3.1,investmentReturn:5.5,retirementReturn:5,
   retirementContributionIncomePct:6,retirementContributionEmployerPct:4,
   voluntaryRetirementContribution:0,voluntaryContributionEndAge:p.retirementAge,
   surplusDestination:'cash',drawdownStrategy:'cash-investments-retirement',
   incomeSources:[
     {id:'example-job',type:'active',label:'Employment income',sourceKind:'salary',startAge:p.age,endAge:p.retirementAge,monthlyAmount:p.salary,annualGrowth:2,retirementContributionEligible:true},
     {id:'example-dividends',type:'passive',label:'Dividends and interest',startAge:p.age,endAge:95,monthlyAmount:p.passive,annualGrowth:1}
   ],
   futureSpendingChanges:p.spendingChanges.map(([age,monthlyChange],index)=>({id:'spend-'+index,age,monthlyChange})),
   moneyEvents:p.events.map(([age,type,amount],index)=>({id:'event-'+index,age,month:7,type,amount,destination:'cash'})),
   yearlyAssumptions:[],
 };
 return {p,values,cashInventory,assetInventories,debtInventories,progressHistory,input,assets,liabilities,netWorth:assets-liabilities};
}

(async()=>{
 let server=null,browser=null;
 try {
   server=spawn('npx',['vite','--host','127.0.0.1','--port','5173','--strictPort'],{stdio:'ignore'});
   let started=false;
   for(let i=0;i<80;i++) {
     try{const response=await fetch('http://127.0.0.1:5173/');if(response.ok){started=true;break;}}catch(_){}
     await new Promise(resolve=>setTimeout(resolve,500));
   }
   if(!started)throw Error('Vite browser server could not start');
   browser=await chromium.launch({headless:true,args:['--no-sandbox']});
   const page=await browser.newPage({viewport:{width:1280,height:900},deviceScaleFactor:1});
   page.on('pageerror',error=>console.log('PAGE_ERROR '+String(error).slice(0,550)));
   await page.goto('http://127.0.0.1:5173/',{waitUntil:'domcontentloaded'});
   const summaries=[];
   for(const p of [p50,p25]){
    const data=createData(p);
    console.log('GENERATING age '+p.age+' A='+data.assets+' L='+data.liabilities+' NW='+data.netWorth);
    const base64=await page.evaluate(async input=>{
       const [{createReportPdf},{calculateBalance},{calculateFinancialPlan,createPlanScenarios},{translations}] = await Promise.all([
         import('/src/pdf.js'),import('/src/finance.js'),import('/src/financial-plan.js'),import('/src/data.js')]);
       const balance=calculateBalance(input.values);
       const retirement=calculateFinancialPlan(input.input,{includeLimit:false});
       if(retirement.calcVersion!=='2.0-candidate')throw Error('Production engine unavailable');
       const report=await createReportPdf({
         profile:{name:input.p.name,dateOfBirth:input.p.dob,profession:input.p.job},
         calculatedAge:input.p.age,values:input.values,balance,
         cashInventory:input.cashInventory,assetInventories:input.assetInventories,debtInventories:input.debtInventories,
         retirement,retirementInput:input.input,planScenarios:createPlanScenarios(input.input),
         currency:'USD',language:input.appLanguage,t:translations[input.appLanguage],
         edition:'paid',sections:['wealth','inventory','simulator'],detailLevel:'detailed',
         progressHistory:input.progressHistory,progressFromDate:'2024-10-14',progressToDate:'2026-10-14',
         pdfPassword:'MWS-DEMO-2026'
       });
       return await new Promise((resolve,reject)=>{
         const fr=new FileReader();
         fr.onload=()=>resolve(String(fr.result).split(',')[1]);
         fr.onerror=()=>reject(fr.error);
         fr.readAsDataURL(report.pdf);
       });
    },{...data,appLanguage:APP_LANGUAGE[SITE_LANG]});
    const bytes=Buffer.from(base64,'base64');
    const name='mws-native-age-'+p.age+'-usd-'+SITE_LANG+'.pdf';
    fs.writeFileSync(path.join(OUT,name),bytes);
    summaries.push({age:p.age,name,netWorth:data.netWorth,assets:data.assets,liabilities:data.liabilities,pdfBytes:bytes.length,
       sha256:createHash('sha256').update(bytes).digest('hex')});
    console.log('PDF '+name+' bytes='+bytes.length);
   }
   fs.writeFileSync(path.join(OUT,'manifest.json'),JSON.stringify({generator:'Native MWS v3.1.2 report functions',language:SITE_LANG,currency:'USD',password:'MWS-DEMO-2026',samples:summaries},null,2));
   console.log('GENERATION_SUCCESS');
 }finally{
   if(browser)await browser.close();
   if(server)server.kill('SIGTERM');
 }
})().catch(error=>{console.error(error.stack||error);process.exitCode=1;});
