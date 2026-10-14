#!/usr/bin/env python3
"""Generate encrypted fictional USD educational PDF illustrations, not exact native app exports."""
from pathlib import Path
from math import pow
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak, Flowable
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter
import sys

BASE=Path(__file__).parent
BASE.mkdir(exist_ok=True)
PASSWORD='MWS-DEMO-2026'   # Intentionally public: these are invented demonstration records.
NAVY=HexColor('#173654'); TEAL=HexColor('#d4faf3'); GOLD=HexColor('#f6ca55')
GREY=HexColor('#dce2e8'); PALE=HexColor('#f3f7fb'); INK=HexColor('#23384b')
styles=getSampleStyleSheet()
for name,size,bold,color in [('HeadingSample',18,True,NAVY),('H2Sample',12,True,NAVY),('H3Sample',9,True,NAVY),('BodySample',8,False,INK),('TinySample',7,False,INK),('HeaderSample',7,True,white)]:
 styles.add(ParagraphStyle(name=name,fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,leading=size*1.35,textColor=color,spaceBefore=5 if bold else 0,spaceAfter=7 if bold else 2))
def P(s,style='BodySample'):
 return Paragraph(str(s).replace('&','&amp;').replace('<','&lt;'),styles[style])
def rm(n):return 'US${:,.0f}'.format(n)
def tab(rows,widths,padding=5):
 t=Table([[P(x,'HeaderSample' if i==0 else 'TinySample') for x in row] for i,row in enumerate(rows)],colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([
 ('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,PALE]),
 ('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),padding),
 ('BOTTOMPADDING',(0,0),(-1,-1),padding),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),5)
 ]));return t
def bottom(c,d):
 c.saveState();c.setFont('Helvetica',7);c.setFillColor(NAVY)
 c.drawString(16*mm,14*mm,'MY WEALTH SQUARE | FICTIONAL USD REPORT | NO REAL ACCOUNTS')
 c.drawRightString(195*mm,14*mm,str(d.page));c.restoreState()

categories=[
 ('cash','Cash & savings'),('investments','Public investments'),('privateInvestments','Private investments'),
 ('retirement','Retirement funds'),('property','Property'),('vehicles','Vehicles'),('otherAssets','Other assets')]
debts=[('homeLoan','Home / mortgage loans'),('vehicleLoan','Vehicle loans'),('cards','Cards / personal loans'),('otherDebt','Other liabilities')]
older_assets={
 'cash':[('Everyday checking account',55000),('Term-deposit ladder',85000),('Emergency savings account',30000)],
 'investments':[('US-listed shares',220000),('Global equity unit trusts',175000),('Bond / ETF portfolio',105000)],
 'privateInvestments':[('Family trading company stake (35%)',350000),('Partnership interest (20%)',180000),('Private venture loan note',120000)],
 'retirement':[('Employer 401(k) account',500000),('Roth IRA account',320000),('Individual retirement account',80000)],
 'property':[('Main residence - California',980000),('Rental condominium - Texas',540000),('Residential plot - Georgia',230000)],
 'vehicles':[('Family SUV',85000),('Compact sedan',43000),('Motorcycle',19000)],
 'otherAssets':[('Gold bullion',90000),('Art collection',45000),('Collectible watch',15000)]}
older_debts={
 'homeLoan':[('Residence housing mortgage',520000),('Condominium mortgage',180000),('Land financing',70000)],
 'vehicleLoan':[('SUV hire purchase',30000),('Sedan financing',15000),('Motorcycle instalment',10000)],
 'cards':[('Credit card A',11000),('Credit card B',5000),('Small personal credit line',2000)],
 'otherDebt':[('Private business borrowing',65000),('Education support loan',40000),('Family loan payable',20000)]}
young_assets={
 'cash':[('Daily savings',10500),('Emergency savings',7500)],
 'investments':[('Equity ETF',9000),('Index unit trust',3000)], 'privateInvestments':[],
 'retirement':[('Employer 401(k) plan',18000),('Roth IRA',2000)],
 'property':[], 'vehicles':[('Used compact car',23000)],
 'otherAssets':[('Laptop and work equipment',3200)]}
young_debts={
 'homeLoan':[], 'vehicleLoan':[('Car hire purchase',17500)],
 'cards':[('Credit card statement',1250)], 'otherDebt':[('Study loan',13500)]}
oldprogress=[
 ('2024-10-14',3015000,1410000),('2025-01-14',3120000,1340000),('2025-04-14',3260000,1280000),
 ('2025-07-14',3485000,1200000),('2025-10-14',3650000,1125000),('2026-01-14',3800000,1080000),
 ('2026-04-14',3980000,1055000),('2026-07-14',4110000,1020000),('2026-10-14',4267000,968000)]
youngprogress=[
 ('2024-10-14',34000,40000),('2025-01-14',37500,39200),('2025-04-14',42800,38500),
 ('2025-07-14',48900,37700),('2025-10-14',55000,36500),('2026-01-14',61000,35400),
 ('2026-04-14',67600,34000),('2026-07-14',74200,32700),('2026-10-14',76200,32250)]
profiles=[
 dict(age=50,name='Alex Tan',gender='Male',dob='1976-04-08',job='Operations Director',
     assets=older_assets,debts=older_debts,progress=oldprogress,retire=62,access=59,
     salary=26000,passive=3800,spend=13500,retireSpend=15500,inflation=2.75,cashReturn=3.1,
     invReturn=5.5,epfReturn=5.0,salaryGrowth=2.0,passiveGrowth=1.0,
     events=[(56,'Addition',150000,'Illustrative gift'),(61,'Withdrawal',200000,'Renovation'),(66,'Withdrawal',85000,'Vehicle replacement')]),
 dict(age=25,name='Maya Lim',gender='Female',dob='2001-03-18',job='Early-career designer',
     assets=young_assets,debts=young_debts,progress=youngprogress,retire=65,access=59,
     salary=7200,passive=220,spend=3700,retireSpend=6500,inflation=2.75,cashReturn=2.8,
     invReturn=6.0,epfReturn=5.0,salaryGrowth=3.0,passiveGrowth=2.0,
     events=[(27,'Withdrawal',15000,'Professional course'),(35,'Withdrawal',50000,'Possible home deposit'),(44,'Addition',25000,'Illustrative cash gift')])
]
class WealthSquare(Flowable):
 def __init__(self,assets,debt,width):self.a=assets;self.d=debt;self.width=width;self.height=150
 def draw(self):
  c=self.canv;w=self.width;h=self.height;half=w/2;debth=h*self.d/self.a if self.a else 0
  c.setStrokeColor(NAVY);c.setFillColor(TEAL);c.rect(0,0,half,h,fill=1,stroke=1)
  c.setFillColor(GREY);c.rect(half,h-debth,half,debth,fill=1,stroke=1)
  c.setFillColor(GOLD);c.rect(half,0,half,h-debth,fill=1,stroke=1)
  c.setFont('Helvetica-Bold',10);c.setFillColor(NAVY);c.drawCentredString(half/2,90,'ASSETS')
  c.drawCentredString(half/2,70,rm(self.a));c.setFont('Helvetica-Bold',8)
  c.drawCentredString(w*0.75,h-max(17,debth/2),'LIABILITIES '+rm(self.d))
  c.drawCentredString(w*0.75,max(16,(h-debth)/2),'NET WORTH '+rm(self.a-self.d))

def totals(d):return sum(v for rows in d.values() for _,v in rows)
def project(p):
 cash=sum(v for _,v in p['assets']['cash']);invest=sum(v for _,v in p['assets']['investments'])
 epf=sum(v for _,v in p['assets']['retirement']);output=[]
 for age in range(p['age'],91):
  work=age<p['retire'];salary=p['salary']*(1+p['salaryGrowth']/100)**(age-p['age']) if work else 0
  passive=p['passive']*(1+p['passiveGrowth']/100)**(age-p['age'])
  spend=(p['spend'] if work else p['retireSpend'])*(1+p['inflation']/100)**(age-p['age'])
  cprev=cash;iprev=invest;eprev=epf;epfIn=0;eventsIn=0;eventsOut=0
  for month in range(1,13):
   worker=salary*0.06;employer=salary*0.04;epfIn+=worker+employer
   cash+=salary-worker+passive-spend;epf+=worker+employer
   for aa,typ,amount,_ in p['events']:
    if aa==age and month==7:
     if typ=='Addition':cash+=amount;eventsIn+=amount
     else:cash-=amount;eventsOut+=amount
   if cash<0:invest+=cash;cash=0
   if invest<0 and age>=p['access']:epf+=invest;invest=0
   if invest<0:invest=0
   epf=max(0,epf)
   cash*=(1+p['cashReturn']/100)**(1/12)
   invest*=(1+p['invReturn']/100)**(1/12)
   epf*=(1+p['epfReturn']/100)**(1/12)
  output.append([str(age),rm((salary+passive)*12),rm(spend*12),rm(epfIn),rm(cash),rm(invest),rm(epf),rm(cash+invest+epf)])
 return output

def create(p):
 age=p['age'];filename=BASE/f'mws-demo-age-{age}.pdf';plain=BASE/f'_plain-{age}.pdf'
 doc=SimpleDocTemplate(str(plain),pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,
                       topMargin=16*mm,bottomMargin=20*mm)
 w=A4[0]-32*mm;story=[]
 a=totals(p['assets']);d=totals(p['debts'])
 assert a==p['progress'][-1][1] and d==p['progress'][-1][2]
 story+=[P('MY WEALTH SQUARE','H3Sample'),P('Your wealth, in one picture.','HeadingSample'),
         P('Fictional educational example | '+p['name']+' | Age '+str(age)+' | 14 October 2026'),
         P('FICTIONAL EXAMPLE ONLY. Names, references and figures are invented. Retirement numbers use a simplified demonstration model rather than the app calculation engine.'),
         Spacer(1,12),WealthSquare(a,d,w),Spacer(1,12),
         tab([['ASSETS','LIABILITIES','NET WORTH','DEBT / ASSETS'],
              [rm(a),rm(d),rm(a-d),'{:.1f}%'.format(100*d/a)]],[w/4]*4)]
 story.append(P('Profile and monthly inputs','H2Sample'))
 story.append(tab([['PROFILE','AGE / DATE OF BIRTH','OCCUPATION','CURRENCY'],
                   [p['name']+' / '+p['gender'],str(age)+' / '+p['dob'],p['job'],'USD (US$)'],
                   ['MONTHLY INCOME','MONTHLY SPENDING','RETIREMENT AGE','HORIZON'],
                   [rm(p['salary']+p['passive']),rm(p['spend']),str(p['retire']),'Age 90']],[w/4]*4))
 story.append(P('Full balance-sheet categories','H2Sample'))
 acc=[['ASSET CATEGORY','US$ AMOUNT','LIABILITY CATEGORY','US$ AMOUNT']]
 for j in range(7):
  ca,al=categories[j];de,dl=debts[j] if j<len(debts) else ('','')
  acc.append([al,rm(sum(v for _,v in p['assets'][ca])),dl,rm(sum(v for _,v in p['debts'].get(de,[]))) if de else ''])
 story.append(tab(acc,[w*.31,w*.19,w*.31,w*.19]))
 story.append(PageBreak());story.append(P('Asset and liability inventory','HeadingSample'))
 story.append(P('All amounts are in USD. Account names, providers and references are DEMO ONLY. Empty categories show RM0.'))
 for group,label,names in [(p['assets'],'ASSETS',categories),(p['debts'],'LIABILITIES',debts)]:
  story.append(P(label,'H2Sample'))
  for key,title in names:
   items=group[key];story.append(P(title+' | '+rm(sum(x[1] for x in items)),'H3Sample'))
   if not items:story.append(P('No entries | RM0'));continue
   rr=[['HOLDING','AMOUNT','DETAILS (ALL FICTIONAL)']]
   for idx,(name,value) in enumerate(items,1):
    ref='DEMO-'+str(age)+'-'+key.upper()+'-'+str(idx).zfill(2)
    extra='Valuation / outstanding amount; US dollars; example reference '+ref+'; Source: fictional provider '+str(idx)
    if key=='property':extra+='; demo title DEMO-TITLE-'+str(idx)
    if key=='vehicles':extra+='; demo registration DEMO-VEH-'+str(idx)
    if key=='privateInvestments':extra+='; ownership / book value, not liquid cash'
    rr.append([name,rm(value),extra])
   rr.append([title+' total',rm(sum(x[1] for x in items)),str(len(items))+' individually recorded items'])
   story.append(tab(rr,[w*.28,w*.16,w*.56],4))
 story.append(P('Saved progress: October 2024 to October 2026','H2Sample'))
 original=p['progress'][0][1]-p['progress'][0][2];rr=[['DATE','ASSETS','LIABILITIES','NET WORTH','VS. START']]
 for date,assets,debtsum in p['progress']:
  worth=assets-debtsum;delta=((worth-original)/abs(original)*100) if original else 0
  rr.append([date,rm(assets),rm(debtsum),rm(worth),'{:+.1f}%'.format(delta)])
 story.append(tab(rr,[w*.18,w*.20,w*.20,w*.23,w*.19],4))
 story.append(P('Financial Life - input assumptions','H2Sample'))
 inp=[['INPUT','VALUE','INPUT','VALUE'],
      ['Age now',str(age),'Plan to age','90'],
      ['Retirement age',str(p['retire']),'Retirement access age',str(p['access'])],
      ['Cash opening',rm(sum(v for _,v in p['assets']['cash'])),'Shares opening',rm(sum(v for _,v in p['assets']['investments']))],
      ['Retirement funds opening',rm(sum(v for _,v in p['assets']['retirement'])),'Drawdown strategy','Cash - shares - Retirement'],
      ['Salary / month',rm(p['salary']),'Passive income / month',rm(p['passive'])],
      ['Salary growth / year',str(p['salaryGrowth'])+'%','Passive income growth',str(p['passiveGrowth'])+'%'],
      ['Living spending / month',rm(p['spend']),'Retirement spending / month',rm(p['retireSpend'])],
      ['Inflation / year',str(p['inflation'])+'%','Cash return / year',str(p['cashReturn'])+'%'],
      ['Shares return / year',str(p['invReturn'])+'%','Retirement return / year',str(p['epfReturn'])+'%'],
      ['Employee retirement contributions', '6% salary','Employer retirement contributions','4% salary'],
      ['One-off events',str(len(p['events'])),'Yearly return overrides','None']]
 story.append(tab(inp,[w*.28,w*.22,w*.28,w*.22],4))
 story.append(P('One-time money events','H2Sample'))
 story.append(tab([['AGE','DIRECTION','US$ AMOUNT','PURPOSE']]+[[str(aa),kind,rm(value),desc] for aa,kind,value,desc in p['events']],[w*.12,w*.20,w*.22,w*.46],4))
 story.append(P('Annual Financial Life illustration through age 90','H2Sample'))
 story.append(P('These numbers illustrate the presentation only; they are not generated by the current MWS Financial Life calculation engine. Nominal US$, after hypothetical return / contribution / spending assumptions. Houses and vehicles are not counted as spendable funds.'))
 projections=[['AGE','INCOME / YEAR','SPEND / YEAR','Retirement ADDITIONS','END CASH','END SHARES','END Retirement','LIQUID + Retirement']]
 projections+=project(p)
 story.append(tab(projections,[w*.055,w*.15,w*.15,w*.135,w*.12,w*.12,w*.115,w*.155],3))
 story.append(Spacer(1,14));story.append(P('Password-protected sharing','H2Sample'))
 story.append(P('This example is AES-256-encrypted using a public demo password. Real reports should have a different, private and unique password, provided separately to a trusted recipient. A recipient can still screenshot, print, copy or forward a report after unlocking.'))
 story.append(P('Offline design: core financial calculations and local reports work on the device. Google Play, exchange-rate refresh, web links and recipient apps are separate online services.'))
 story.append(P('Fictional educational content, not personalised financial advice. 14 October 2026.','TinySample'))
 doc.build(story,onFirstPage=bottom,onLaterPages=bottom)
 reader=PdfReader(str(plain));writer=PdfWriter();writer.append_pages_from_reader(reader)
 writer.add_metadata({'/Title':'My Wealth Square - Fictional sample age '+str(age),'/Subject':'Fictional education PDF; password-protected'})
 writer.encrypt(user_password=PASSWORD,owner_password=PASSWORD+'-owner',algorithm='AES-256')
 with filename.open('wb') as f:writer.write(f)
 plain.unlink()
 verify=PdfReader(str(filename))
 assert verify.is_encrypted and verify.decrypt(PASSWORD)
 assert len(verify.pages)>=4
 assert len(p['assets']['cash'])>0
 print(str(filename),len(verify.pages),'pages',filename.stat().st_size,'bytes','A=',a,'L=',d)
for p in profiles:create(p)
