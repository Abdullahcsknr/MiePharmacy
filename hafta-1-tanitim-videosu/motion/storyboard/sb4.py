import sys,subprocess,random,math
sys.path.insert(0,sys.argv[1]); import render as R
from PIL import Image,ImageDraw,ImageFont,ImageFilter
S=sys.argv[2]; W,H=1080,1920
OR=(255,100,24); WH=(255,255,255); BK=(10,10,10); GR=(85,85,85)
M=lambda w,s: ImageFont.truetype(f'{S}/fonts/montserrat-{w}.ttf',s)
mono=ImageFont.truetype(f'{S}/fonts/jetbrains-mono-500.ttf',24)
def grab(v,t):
    p=f'{S}/sb/x.png'; subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',f'{S}/arsiv/{v}','-frames:v','1',p]); return Image.open(p).convert('RGB')
def black(): return Image.new('RGB',(W,H),BK)
def full(v,t,dark=0.45,zoom=1.0):
    fr=R.cover(grab(v,t),(W,H),zoom); ov=Image.new('RGB',(W,H),(0,0,0)); return Image.blend(fr,ov,dark)
def grad(fr,y0,y1,a=200):
    g=Image.new('L',(1,H),0)
    for y in range(y0,y1): g.putpixel((0,y),int(a*(y-y0)/(y1-y0)))
    for y in range(y1,H): g.putpixel((0,y),a)
    fr.paste(Image.new('RGB',(W,H),(0,0,0)),(0,0),g.resize((W,H)))
def lines(d,x,y,ls,font,fills,lh,anchor='la'):
    for l,f in zip(ls,fills): d.text((x,y),l,font=font,fill=f,anchor=anchor); y+=lh
    return y
def caption(fr,words,active):
    d=ImageDraw.Draw(fr); f=M('800',58); x=W//2; y=1330
    txt=' '.join(words); wtot=d.textlength(txt,font=f); cx=(W-wtot)/2
    for i,w in enumerate(words):
        if i==active:
            bw=d.textlength(w,font=f); d.rounded_rectangle([cx-10,y-8,cx+bw+10,y+70],12,fill=OR)
        d.text((cx,y),w,font=f,fill=WH); cx+=d.textlength(w+' ',font=f)
def window(fr,src,lab,box,rad=26,bar=50):
    x,y,w,h=box; c=Image.new('RGB',(w,h),(28,30,30)); c.paste(R.cover(src,(w,h-bar)),(0,bar)); cd=ImageDraw.Draw(c)
    for j in range(3): cd.ellipse([22+j*20,bar//2-6,34+j*20,bar//2+6],fill=OR if j==0 else (88,90,90))
    cd.text((96,bar//2),lab,font=M('700',22),fill=(220,220,220),anchor='lm')
    sh=Image.new('RGBA',(w+160,h+160),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([80,110,80+w,110+h],rad,fill=(0,0,0,180))
    fr.paste(sh.filter(ImageFilter.GaussianBlur(35)),(x-80,y-80),sh.filter(ImageFilter.GaussianBlur(35))); fr.paste(c,(x,y),R.rounded_mask((w,h),rad))
def chip(fr,xy,t,checked,rot=0,big=False):
    f=M('800',40 if big else 34); d0=ImageDraw.Draw(Image.new('RGB',(1,1)))
    tw=d0.textlength(t,font=f); w,h=int(tw+(110 if checked else 60)),84
    c=Image.new('RGBA',(w,h),(0,0,0,0)); cd=ImageDraw.Draw(c)
    cd.rounded_rectangle([0,0,w-1,h-1],18,fill=WH)
    tx=30
    if checked: cd.ellipse([22,22,62,62],fill=OR); cd.line([(32,42),(40,51),(54,33)],fill=WH,width=6); tx=78
    cd.text((tx,h//2),t,font=f,fill=BK,anchor='lm')
    c=c.rotate(rot,expand=True,resample=Image.BICUBIC); fr.paste(c,xy,c)
def progress(fr,n):
    d=ImageDraw.Draw(fr)
    for i in range(6):
        x=80+i*150; d.rounded_rectangle([x,260,x+130,268],4,fill=OR if i<n else (70,70,70))
    d.text((80,300),f'0{n}/06',font=M('800',40),fill=OR)
ITEMS=['FORMÜLASYON','STABİLİTE','MİKROBİYOLOJİK','CHALLENGE TEST','MSDS','PIF','CPSR','ÜTS BİLDİRİMİ','AMBALAJ','ETİKET','GRAFİK TASARIM','SERİ ÜRETİM']
T=[]
# A hook word 1
fr=black(); d=ImageDraw.Draw(fr); f=M('900',150)
d.text((80,700),'KOZMETİK',font=f,fill=OR); T.append(('A','0.0–0.6','HOOK: kelime kelime çarpma (scale %140 > %100, bas vuruşu her kelimede)',fr))
fr=black(); d=ImageDraw.Draw(fr); f=M('900',132)
lines(d,80,560,['KOZMETİK','SEKTÖRÜNE','GİRMEK','İSTİYOSUN?'],f,[OR,WH,WH,WH],150); T.append(('B','0.6–2.5','Soru tamamlanır, ekran hafif sarsılır. VO: "Kozmetik sektörüne girmek istiyosun?"',fr))
# C avalanche
fr=black(); random.seed(4)
for i,t in enumerate(ITEMS*1):
    chip(fr,(random.randint(20,560),random.randint(380,1450)),t,False,rot=random.uniform(-22,22))
d=ImageDraw.Draw(fr); d.text((W-80,250),'12',font=M('900',120),fill=OR,anchor='ra'); d.text((W-80,380),'ADIM',font=mono,fill=WH,anchor='ra')
T.append(('C','2.5–5.5','PROBLEM: zorunlu süreçler yukarıdan yağar, üst üste yığılır, hızlanır; sayaç 1 > 12. Tık-tık düşme sesleri',fr))
# D stamp
fr=black(); d=ImageDraw.Draw(fr)
for i,t in enumerate(ITEMS[:6]):
    a=i/6*6.28; chip(fr,(int(400+330*math.cos(a)),int(860+420*math.sin(a))),t,False,rot=int(30*math.sin(a)))
d.rounded_rectangle([170,780,910,1060],30,fill=WH); d.text((540,920),'ANAHTAR\nTESLİM',font=M('900',96),fill=BK,anchor='mm',align='center',spacing=4)
d.rounded_rectangle([170,780,910,1060],30,outline=OR,width=10)
T.append(('D','5.5–7.0','ÇÖZÜM: tüm kartlar tek kutuya emilir, "ANAHTAR TESLİM" damgası iner (stamp SFX, müzik susar)',fr))
fr=Image.new('RGB',(W,H),WH); d=ImageDraw.Draw(fr)
d.rounded_rectangle([290,560,790,760],26,fill=BK); d.text((540,660),'ANAHTAR TESLİM',font=M('900',50),fill=WH,anchor='mm')
lines(d,540,900,['Kendi markanı','oluşturmak artık','çok daha kolay.'],M('800',84),[BK,BK,OR],104,'ma')
T.append(('E','7.0–9.0','Kutu küçülür, cümle kelime kelime yazılır. VO birebir okur',fr))
# F door  >  factory
fr=full('MIE_3.mp4',9.5,0.35,1.15); grad(fr,1000,1600,220); d=ImageDraw.Draw(fr)
lines(d,80,1060,['MİE KOZMETİK','FASON ÜRETİM','MERKEZİ'],M('900',104),[WH,OR,OR],118)
T.append(('F','9.0–10.5','REVEAL + MARKA: kutu kapı gibi açılır, koridordan içeri itme; marka adı ve konumu',fr))
fr=full('MIE_30.mp4',7,0.15,1.0); grad(fr,1250,1700,200); d=ImageDraw.Draw(fr)
lines(d,80,1290,['Onaylanan numune ile','birebir aynı kalitede','seri imalat'],M('800',66),[WH,WH,OR],80)
T.append(('G','10.5–12.0','KANIT: dev dolum hattı tam ekran, yavaş zoom-out; slogan yerine somut bilgi',fr))
# H/I steps
for key,tm,n,lab,v,t,note in [('H','12.0–13.5',1,'STRATEJİK PLANLAMA','MIE_43_PART_000.mp4',6,'KANIT: ilerleme çubuğu 01/06; pencere (referans stil) açılır, alttaki kart tik olur'),
                          ('I','13.5–15.0',2,'FORMÜLASYON GELİŞTİRME','MIE_6..mp4',4,'Her adım ~1,5 sn: pencere yerinde kalır, görüntü ve etiket değişir'),
                          ('J','16.5–18.0',5,'SERİ ÜRETİM VE KALİTE KONTROL','MIE_7.mp4',11,'05: pencere içinde 3 hızlı kesme (kazan  >  pano  >  dolum) müziğin vuruşlarında')]:
    fr=black(); progress(fr,n); d=ImageDraw.Draw(fr)
    d.text((80,360),lab.title() if False else lab,font=M('900',60 if len(lab)<20 else 46),fill=WH)
    window(fr,grab(v,t),lab,(110,520,860,760))
    chip(fr,(110,1330),{1:'STRATEJİK PLANLAMA',2:'FORMÜLASYON',5:'SERİ ÜRETİM'}[n],True)
    T.append((key,tm,note,fr))
# K grid
fr=black(); d=ImageDraw.Draw(fr)
clips=[('MIE_28.mp4',6),('MIE_38.mp4',6),('MIE_9.mp4',6),('MIE_34.mp4',5),('YENI_MIE_12.mp4',3),('MIE_41.mp4',5),('MIE_37.mp4',10),('MIE_29.mp4',9),('MIE_39.mp4',9)]
for k,(v,t) in enumerate(clips):
    x=60+(k%3)*325; y=420+(k//3)*325
    fr.paste(R.cover(grab(v,t),(305,305)),(x,y),R.rounded_mask((305,305),20))
d.text((60,1400),'ORTALAMA PROJE SÜRESİ',font=mono,fill=WH); d.text((60,1560),'3-6 hafta*',font=M('900',130),fill=OR,anchor='ls'); d.text((60,1610),'*Proje bazlı yeni ürünler için ek süre gerekebilir.',font=M('500',26),fill=(170,170,170))
T.append(('K','18.0–21.0','ÖLÇEK + SOMUT BİLGİ: 9 pencere aynı anda açılır; altta süre sayaçla 0 > 3-6 dolar',fr))
fr=Image.new('RGB',(W,H),WH); d=ImageDraw.Draw(fr)
d.rectangle([330,560,750,760],outline=GR,width=3); d.text((540,660),'ORİJİNAL LOGO',font=mono,fill=GR,anchor='mm')
lines(d,540,880,['Markanı oluştur,','üretimini','bize bırak.'],M('800',84),[BK,BK,OR],104,'ma')
d.rounded_rectangle([170,1250,910,1360],55,fill=OR); d.text((540,1305),'Teklif ve Katalog İçin İletişime Geçin',font=M('800',34),fill=WH,anchor='mm')
d.text((540,1420),'miepharma.com',font=M('500',36),fill=GR,anchor='mm')
T.append(('L','21.0–25.0','OUTRO: beyaza geçiş, logo, kapanış cümlesi kelime kelime; CTA butonu nabız gibi',fr))
# board
tw,th=300,533; cols=6; capf=ImageFont.truetype(f'{S}/fonts/inter-600.ttf',15); capn=ImageFont.truetype(f'{S}/fonts/inter-400.ttf',13)
rows=(len(T)+cols-1)//cols; bh=th+120
board=Image.new('RGB',(cols*(tw+12)+12,rows*bh+12),'white'); bd=ImageDraw.Draw(board)
for i,(k,tm,note,fr) in enumerate(T):
    x=12+(i%cols)*(tw+12); y=12+(i//cols)*bh
    bd.text((x,y),f'{k} · {tm} sn',font=capf,fill='black')
    board.paste(fr.resize((tw,th),Image.LANCZOS),(x,y+24)); bd.rectangle([x,y+24,x+tw-1,y+24+th-1],outline=(210,210,210))
    yy=y+th+30; line=''
    for w in note.split():
        if bd.textlength(line+' '+w,font=capn)>tw: bd.text((x,yy),line,font=capn,fill=(60,60,60)); yy+=17; line=w
        else: line=(line+' '+w).strip()
    bd.text((x,yy),line,font=capn,fill=(60,60,60))
board.save(sys.argv[3],quality=88); print('ok')
