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
 """Use the same visual grammar as the app-export report screenshots."""
 c.saveState()
 w,h=A4
 c.setFillColor(PALE);c.rect(0,0,w,h,stroke=0,fill=1)
 c.setFillColor(HexColor('#ffdb56'));c.rect(0,0,3*mm,h,stroke=0,fill=1)
 c.setFillColor(NAVY);c.rect(0,h-35*mm,w,35*mm,stroke=0,fill=1)
 c.setFillColor(white);c.setFont('Helvetica-Bold',19)
 c.drawString(17*mm,h-18*mm,'My Wealth Square')
 c.setFont('Helvetica',8);c.setFillColor(HexColor('#c3d7e6'))
 c.drawString(17*mm,h-26*mm,'FICTIONAL SAMPLE  |  USD  |  FOR EDUCATIONAL USE')
 c.setFillColor(white);c.drawRightString(w-15*mm,h-20*mm,str(d.page))
 c.setFillColor(HexColor('#73889b'));c.setFont('Helvetica',6.5)
 c.drawString(17*mm,13*mm,'(c) 2026 Looi Boon Ping  |  All identities, banks and account numbers are fictional.')
 c.drawRightString(w-15*mm,13*mm,'MY WEALTH SQUARE  |  DEMONSTRATION ONLY')
 c.restoreState()

categories=[
 ('cash','Cash & savings'),('investments','Public investments'),('privateInvestments','Private investments'),
 ('retirement','Retirement funds'),('property','Property'),('vehicles','Vehicles'),('otherAssets','Other assets')]
debts=[('homeLoan','Home / mortgage loans'),('vehicleLoan','Vehicle loans'),('cards','Cards / personal loans'),('otherDebt','Other liabilities')]
older_assets={
 'cash':[('Everyday checking account',55000),('Fixed-deposit savings account',65000),('Emergency reserve account',30000)],
 'investments':[('Listed share portfolio',90000),('Global index funds',85000),('Bond and ETF portfolio',55000)],
 'privateInvestments':[('Private family-business stake (30%)',60000),('Small partnership ownership',40000),('Private company loan note',20000)],
 'retirement':[('Employer retirement plan',170000),('Individual retirement account',135000),('Supplementary retirement account',55000)],
 'property':[('Primary residence',320000),('Rental condominium',135000),('Residential land lot',45000)],
 'vehicles':[('Family SUV',38000),('Compact sedan',22000),('Motorcycle',10000)],
 'otherAssets':[('Physical investment gold',25000),('Art and collectibles',15000),('Watch collection',10000)]}
older_debts={
 'homeLoan':[('Primary residence mortgage',255000),('Condominium mortgage',100000),('Land financing',35000)],
 'vehicleLoan':[('SUV financing',20000),('Sedan financing',8000),('Motorcycle instalment',4000)],
 'cards':[('Credit card A balance',5000),('Credit card B balance',4000),('Personal credit line',4000)],
 'otherDebt':[('Small business loan',18000),('Education support loan',15000),('Family loan payable',12000)]}
young_assets={
 'cash':[('Current / salary savings',10000),('Emergency savings',8000)],
 'investments':[('Equity ETF holding',10000),('Index fund account',5000)],
 'privateInvestments':[], 'retirement':[('Employer retirement plan',21000),('Individual retirement savings',4000)],
 'property':[], 'vehicles':[('Used compact car',28000)],
 'otherAssets':[('Laptop and professional equipment',4000)]}
young_debts={
 'homeLoan':[], 'vehicleLoan':[('Compact car financing',24000)],
 'cards':[('Credit card statement balance',1000)], 'otherDebt':[('Student education loan',15000)]}

oldprogress=[
 ('2024-10-14',1220000,530000),('2025-01-14',1260000,527000),('2025-04-14',1300000,523000),
 ('2025-07-14',1340000,515000),('2025-10-14',1380000,508000),('2026-01-14',1415000,500000),
 ('2026-04-14',1440000,494000),('2026-07-14',1460000,487000),('2026-10-14',1480000,480000)]
youngprogress=[
 ('2024-10-14',48000,43000),('2025-01-14',51000,42400),('2025-04-14',55000,42000),
 ('2025-07-14',60000,41700),('2025-10-14',67000,41100),('2026-01-14',73000,40900),
 ('2026-04-14',79000,40500),('2026-07-14',85000,40200),('2026-10-14',90000,40000)]

profiles=[
 dict(age=50,name='Alex Tan',gender='Male',dob='1976-04-08',job='Operations Director',
     assets=older_assets,debts=older_debts,progress=oldprogress,retire=62,access=59,
     salary=11000,passive=1200,spend=5500,retireSpend=6500,inflation=2.75,cashReturn=3.1,
     invReturn=5.5,epfReturn=5.0,salaryGrowth=2.0,passiveGrowth=1.0,
     spendingChanges=[(55,5900,'Planned mid-career spending'),(62,6500,'Retirement budget'),(72,6100,'Planned later-life adjustment')],
     events=[(56,'Addition',40000,'Illustrative inheritance'),(61,'Withdrawal',60000,'Home renovation'),(66,'Withdrawal',25000,'Vehicle replacement')]),
 dict(age=25,name='Maya Lim',gender='Female',dob='2001-03-18',job='Early-career designer',
     assets=young_assets,debts=young_debts,progress=youngprogress,retire=65,access=59,
     salary=5800,passive=150,spend=3000,retireSpend=4200,inflation=2.75,cashReturn=2.8,
     invReturn=6.0,epfReturn=5.0,salaryGrowth=3.0,passiveGrowth=2.0,
     spendingChanges=[(30,3500,'Expected household changes'),(45,4300,'Planned family budget'),(65,4200,'Retirement living budget')],
     events=[(27,'Withdrawal',6000,'Professional course'),(35,'Withdrawal',18000,'Possible home deposit'),(44,'Addition',10000,'Illustrative cash gift')])
]
class WealthSquare(Flowable):
 """Full-category MWS-style balance-sheet square with a proportional right side."""
 def __init__(self,assets,debt,width,assetRows=None):
  self.a=assets;self.d=debt;self.width=width;self.height=258
  self.assetRows=assetRows or []
 def draw(self):
  c=self.canv;w=self.width;h=self.height;left=w*0.51;right=w-left
  base=34;area=h-base
  ratio=min(1,self.d/self.a) if self.a>0 else 0
  dh=area*ratio
  c.setLineWidth(2);c.setStrokeColor(NAVY)
  c.setFillColor(HexColor('#d5f1f4'));c.rect(0,base,left,area,fill=1,stroke=1)
  c.setFillColor(HexColor('#e5e9f1'));c.rect(left,base+area-dh,right,dh,fill=1,stroke=1)
  c.setFillColor(HexColor('#ffdb56'));c.rect(left,base,right,area-dh,fill=1,stroke=1)
  c.setFillColor(HexColor('#e8f2fc'))
  c.rect(0,0,left,base,fill=1,stroke=1);c.rect(left,0,right,base,fill=1,stroke=1)
  c.setFillColor(NAVY);c.setFont('Helvetica-Bold',11)
  c.drawString(12,base+area-23,'ASSETS')
  c.drawRightString(left-12,base+area-23,rm(self.a))
  yy=base+area-48
  c.setFont('Helvetica',7.1)
  for title,value in self.assetRows:
   if yy<base+12:break
   label=title if len(title)<=25 else title[:23]+'..'
   c.drawString(12,yy,label)
   c.setFont('Helvetica-Bold',7.1)
   c.drawRightString(left-10,yy,rm(value))
   c.setFont('Helvetica',7.1)
   c.setStrokeColor(HexColor('#c3d4de'));c.line(12,yy-6,left-10,yy-6)
   yy-=23
  c.setFillColor(NAVY);c.setFont('Helvetica-Bold',10)
  c.drawString(left+10,base+area-23,'LIABILITIES')
  c.drawRightString(w-8,base+area-42,rm(self.d))
  c.setFont('Helvetica',8)
  c.drawString(left+10,base+area-57,'{:.1f}% of assets'.format(100*ratio))
  if area-dh>=56:
   c.setFont('Helvetica-Bold',11)
   c.drawString(left+10,base+area-dh-25,'NET WORTH')
   c.drawRightString(w-10,base+area-dh-43,rm(self.a-self.d))
  c.setFillColor(NAVY);c.setFont('Helvetica-Bold',8)
  c.drawCentredString(left/2,12,'Assets = '+rm(self.a))
  c.drawCentredString(left+right/2,12,'Liabilities + equity = '+rm(self.a))

class ProgressTrend(Flowable):
 def __init__(self,progress,width):
  self.progress=progress
  self.width=width
  self.height=176
 def draw(self):
  c=self.canv;w=self.width;h=self.height
  left=58;right=w-20;bottom=34;top=h-17
  c.setLineWidth(0.8);c.setStrokeColor(GREY)
  c.line(left,bottom,right,bottom);c.line(left,bottom,left,top)
  series=[
   ('Assets',[p[1] for p in self.progress],HexColor('#148f85')),
   ('Liabilities',[p[2] for p in self.progress],HexColor('#6c7888')),
   ('Net worth',[p[1]-p[2] for p in self.progress],HexColor('#bc8d16'))
  ]
  maximum=max(v for _,data,_ in series for v in data)*1.08
  for fraction in [0,0.5,1.0]:
   y=bottom+(top-bottom)*fraction
   c.setStrokeColor(HexColor('#e0e7ed'));c.line(left,y,right,y)
   c.setFillColor(INK);c.setFont('Helvetica',6)
   c.drawRightString(left-6,y-2,'USD '+format(maximum*fraction/1e6,'.2f')+'m')
  count=len(self.progress)
  for title,data,color in series:
   c.setStrokeColor(color);c.setLineWidth(2)
   for i in range(1,count):
    x1=left+(right-left)*(i-1)/(count-1)
    y1=bottom+(top-bottom)*data[i-1]/maximum
    x2=left+(right-left)*i/(count-1)
    y2=bottom+(top-bottom)*data[i]/maximum
    c.line(x1,y1,x2,y2)
  for ix in [0,count//2,count-1]:
   x=left+(right-left)*ix/(count-1)
   c.setFillColor(INK);c.setFont('Helvetica',7)
   c.drawCentredString(x,bottom-15,self.progress[ix][0][:7])
  for j,(title,_,color) in enumerate(series):
   x=left+j*(w-left)/3
   c.setFillColor(color);c.rect(x,3,8,8,fill=1,stroke=0)
   c.setFillColor(INK);c.setFont('Helvetica',7)
   c.drawString(x+12,4,title)

def totals(d):return sum(v for rows in d.values() for _,v in rows)
def project(p,return_adjustment=0):
 cash=sum(v for _,v in p['assets']['cash']);invest=sum(v for _,v in p['assets']['investments'])
 epf=sum(v for _,v in p['assets']['retirement']);output=[]
 for age in range(p['age'],91):
  work=age<p['retire'];salary=p['salary']*(1+p['salaryGrowth']/100)**(age-p['age']) if work else 0
  passive=p['passive']*(1+p['passiveGrowth']/100)**(age-p['age'])
  revised_spend=p['spend'] if work else p['retireSpend']
  for change_age,new_amount,_ in p['spendingChanges']:
   if change_age<=age:revised_spend=new_amount
  spend=revised_spend*(1+p['inflation']/100)**(age-p['age'])
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
   cash*=(1+(p['cashReturn']+return_adjustment)/100)**(1/12)
   invest*=(1+(p['invReturn']+return_adjustment)/100)**(1/12)
   epf*=(1+(p['epfReturn']+return_adjustment)/100)**(1/12)
  output.append([str(age),rm((salary+passive)*12),rm(spend*12),rm(epfIn),rm(cash),rm(invest),rm(epf),rm(cash+invest+epf)])
 return output

def create(p):
 age=p['age'];filename=BASE/f'mws-demo-age-{age}.pdf';plain=BASE/f'_plain-{age}.pdf'
 doc=SimpleDocTemplate(str(plain),pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,
                       topMargin=44*mm,bottomMargin=23*mm)
 w=A4[0]-32*mm;story=[]
 a=totals(p['assets']);d=totals(p['debts'])
 assert a==p['progress'][-1][1] and d==p['progress'][-1][2]
 story+=[P('MY WEALTH SQUARE','H3Sample'),P('Your wealth, in one picture.','HeadingSample'),
         P('Fictional educational example | '+p['name']+' | Age '+str(age)+' | 14 October 2026'),
         P('FICTIONAL EXAMPLE ONLY. Names, references and figures are invented. Retirement numbers use a simplified demonstration model rather than the app calculation engine.'),
         Spacer(1,12),WealthSquare(a,d,w,[(title,sum(v for _,v in p['assets'][key])) for key,title in categories]),Spacer(1,12),
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
 story.append(PageBreak());story.append(P('Progress History','HeadingSample'))
 story.append(P('Saved progress: October 2024 to October 2026','H2Sample'))
 original=p['progress'][0][1]-p['progress'][0][2];rr=[['DATE','ASSETS','LIABILITIES','NET WORTH','VS. START']]
 for date,assets,debtsum in p['progress']:
  worth=assets-debtsum;delta=((worth-original)/abs(original)*100) if original else 0
  rr.append([date,rm(assets),rm(debtsum),rm(worth),'{:+.1f}%'.format(delta)])
 story.append(tab(rr,[w*.18,w*.20,w*.20,w*.23,w*.19],4))
 story.append(P('Two-year progress chart (USD)','H2Sample'))
 story.append(ProgressTrend(p['progress'],w))

 story.append(PageBreak());story.append(P('Wealth Inventory Report','HeadingSample'))
 story.append(P('USD only. Every institution, person, account identifier and loan reference is invented for this demonstration. Empty categories show US$0.'))
 for group,label,names in [(p['assets'],'ASSETS',categories),(p['debts'],'LIABILITIES',debts)]:
  story.append(P(label,'H2Sample'))
  for key,title in names:
   items=group[key];story.append(P(title+' | '+rm(sum(x[1] for x in items)),'H3Sample'))
   if not items:story.append(P('No entries | US$0'));continue
   rr=[['HOLDING','AMOUNT','DETAILS (ALL FICTIONAL)']]
   for idx,(name,value) in enumerate(items,1):
    ref='DEMO-'+str(age)+'-'+key.upper()+'-'+str(idx).zfill(2)

    fictional_banks=['Northstar Demo Bank (fictional)','Blue Oak Example Bank (fictional)','Maple Placeholder Credit Union (fictional)']
    financial_bank=fictional_banks[(idx-1)%3]
    extra='Record reference: '+ref+'; Amount: '+rm(value)+'; All names and accounts are FICTIONAL.'
    if key=='cash':
     extra='Bank: '+financial_bank+'; Branch: Illustrative Branch '+str(idx)+'; Account holder: '+p['name']+'; Account no: DEMO-'+str(age)+'-000'+str(idx)+'-CASH; Currency: USD; NOT A REAL BANK ACCOUNT.'
    elif key=='investments':
     extra='Broker: Example Securities Custody (fictional); Account no: DEMO-BROKER-'+str(age)+'-00'+str(idx)+'; Owner: '+p['name']+'; Portfolio value: '+rm(value)+'.'
    elif key=='retirement':
     extra='Provider: Fictional Retirement Trust; Member account: DEMO-RET-'+str(age)+'-0'+str(idx)+'; Owner: '+p['name']+'; Balance: '+rm(value)+'.'
    elif key=='privateInvestments':
     extra='Company / partnership ID: DEMO-CO-'+str(age)+'-0'+str(idx)+'; Contract / ownership reference: '+ref+'; Ownership is not bank cash.'
    elif key=='property':
     extra='Fictional property title: DEMO-TITLE-'+str(age)+'-'+str(idx)+'; Location: Example District, Fictional State; Owner: '+p['name']+'.'
    elif key=='vehicles':
     extra='Registration no: DEMO-VEH-'+str(age)+'-'+str(idx)+'; Fictional registered owner: '+p['name']+'.'
    elif key=='otherAssets':
     extra='Custody / insurance: Imaginary Vault & Insurance Co.; Asset reference: '+ref+'.'
    elif group is p['debts']:
     extra='Creditor: '+financial_bank+'; Loan / card account: DEMO-LOAN-'+str(age)+'-00'+str(idx)+'-'+key.upper()+'; Borrower: '+p['name']+'; Balance owed: '+rm(value)+'; FICTIONAL.'
    rr.append([name,rm(value),extra])
   rr.append([title+' total',rm(sum(x[1] for x in items)),str(len(items))+' individually recorded items'])
   story.append(tab(rr,[w*.28,w*.16,w*.56],4))
 story.append(PageBreak());story.append(P('Financial Independence Planning Report','HeadingSample'))
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
 story.append(P('Planned future spending changes','H2Sample'))
 story.append(tab([['AGE','NEW MONTHLY SPENDING','REASON']]+[[str(aa),rm(v),reason] for aa,v,reason in p['spendingChanges']],[w*.12,w*.3,w*.58],4))
 story.append(P('One-time money events','H2Sample'))
 story.append(tab([['AGE','DIRECTION','US$ AMOUNT','PURPOSE']]+[[str(aa),kind,rm(value),desc] for aa,kind,value,desc in p['events']],[w*.12,w*.20,w*.22,w*.46],4))
 story.append(P('Financial Life Simulator - 3 x 3','H2Sample'))
 story.append(P('Nine spending / return scenarios for age 90: this is a demonstrative sensitivity table, not the verified MWS simulator.'))
 sensitivity=[['MONTHLY SPENDING','RETURNS -1pp','BASE RETURNS','RETURNS +1pp']]
 for factor,label in [(0.9,'10% below base'),(1.0,'Base spending'),(1.1,'10% above base')]:
  pp=dict(p);pp['spend']=p['spend']*factor;pp['retireSpend']=p['retireSpend']*factor
  pp['spendingChanges']=[(year,monthly*factor,reason) for year,monthly,reason in p['spendingChanges']]
  sensitivity.append([label]+[project(pp,delta)[-1][-1] for delta in [-1,0,1]])
 story.append(tab(sensitivity,[w*.25]*4,4))
 story.append(P('Nine illustrative combinations of spending and annual returns. Values show cash + investments + retirement accounts at age 90, not total net worth. A zero end balance is not a guarantee of funding sufficiency.'))

 story.append(PageBreak())
 story.append(P('Financial Independence Planning Report','HeadingSample'))
 story.append(P('Yearly balances to age 90','H2Sample'))
 story.append(P('USD, hypothetical nominal values. Financial assets only.  Assumptions, not investment advice.'))
 forecast=project(p)
 cash0=sum(v for _,v in p['assets']['cash']);stock0=sum(v for _,v in p['assets']['investments']);ret0=sum(v for _,v in p['assets']['retirement'])
 balances=[['AGE','OPENING FUNDS','CASH & SAVINGS','PUBLIC INVESTMENTS','RETIREMENT FUND','END ACCESSIBLE BALANCE']]
 for record in forecast:
  year_age=int(record[0]);cash=record[4];shares=record[5];retirement=record[6]
  opening=rm(cash0+stock0+ret0) if year_age==age else forecast[year_age-age-1][7]
  balances.append([str(year_age),opening,cash,shares,retirement,record[7]])
 story.append(tab(balances,[w*.065,w*.185,w*.17,w*.18,w*.18,w*.22],4))
 story.append(PageBreak())
 story.append(P('Financial Independence Planning Report','HeadingSample'))
 story.append(P('Yearly cash flow to age 90','H2Sample'))
 cashflow=[['AGE','EARNED & PASSIVE INCOME','TOTAL SPENDING','RETIREMENT ADDITIONS','CLOSING LIQUID FUNDS','CLOSING TOTAL FUNDS']]
 for record in forecast:
  cashflow.append([record[0],record[1],record[2],record[3],record[4]+' + '+record[5],record[7]])
 story.append(tab(cashflow,[w*.07,w*.21,w*.17,w*.175,w*.205,w*.17],4))
 story.append(P('Financial values are illustrative and exclude property, vehicles and non-liquid holdings from funds available for spending.'))

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
