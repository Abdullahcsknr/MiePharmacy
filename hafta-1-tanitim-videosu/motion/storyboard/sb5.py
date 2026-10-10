import sys,subprocess,random,math
sys.path.insert(0,sys.argv[1]); import render as R
from PIL import Image,ImageDraw,ImageFont,ImageFilter
S,REPO,OUT=sys.argv[2],sys.argv[3],sys.argv[4]; W,H=1080,1920
OR=(255,100,24); WH=(255,255,255); GR=(85,85,85); LG=(244,244,244); INK=(20,20,20)
FD=f'{REPO}/motion/fonts'
AN=lambda s: ImageFont.truetype(f'{FD}/anton-400.ttf',s)
PO=lambda w,s: ImageFont.truetype(f'{FD}/poppins-{w}.ttf',s)
LOGO=Image.open(f'{REPO}/kimlik/logo-mie-siyah-hd.png')
def grab(v,t,hd=False):
    p=f'{S}/sb/y.png'; src=f'{S}/hd/{v}' if hd else f'{S}/arsiv/{v}'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',src,'-frames:v','1',p]); return Image.open(p).convert('RGB')
def bg(c): return Image.new('RGB',(W,H),c)
def full(v,t,dim=0.25,zoom=1.0):
    fr=R.cover(grab(v,t,True),(W,H),zoom); return Image.blend(fr,Image.new('RGB',(W,H)),dim)
def shade(fr,y0,y1,a=210):
    g=Image.new('L',(1,H),0)
    for y in range(H): g.putpixel((0,y),0 if y<y0 else min(a,int(a*(y-y0)/max(1,y1-y0))))
    fr.paste(Image.new('RGB',(W,H)),(0,0),g.resize((W,H)))
def stack(d,x,y,lines,font,cols,lh):
    for l,c in zip(lines,cols): d.text((x,y),l,font=font,fill=c); y+=lh
    return y
def cap(fr,words,active,y=1240,size=64):
    # Reels caption: Poppins Black, white + shadow, active word in orange box
    f=PO('900',size); d=ImageDraw.Draw(fr); lines=[[]]; mx=820
    for w in words:
        t=' '.join(lines[-1]+[w])
        if d.textlength(t,font=f)>mx and lines[-1]: lines.append([w])
        else: lines[-1].append(w)
    k=0
    for ln in lines:
        x=80
        for w in ln:
            bw=d.textlength(w,font=f)
            if k==active: d.rounded_rectangle([x-12,y-6,x+bw+12,y+size+14],14,fill=OR)
            else:
                sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text((x+3,y+5),w,font=f,fill=(0,0,0,170)); fr.paste(sh.filter(ImageFilter.GaussianBlur(4)),(0,0),sh.filter(ImageFilter.GaussianBlur(4)))
            d.text((x,y),w.upper(),font=f,fill=WH) if False else d.text((x,y),w,font=f,fill=WH)
            x+=bw+d.textlength(' ',font=f); k+=1
        y+=size+26
def window(fr,src,lab,box,rad=28,bar=54,shadow=True):
    x,y,w,h=box; c=Image.new('RGB',(w,h),WH); c.paste(R.cover(src,(w,h-bar)),(0,bar)); cd=ImageDraw.Draw(c)
    for j,col in enumerate([OR,(210,210,210),(210,210,210)]): cd.ellipse([24+j*22,bar//2-7,38+j*22,bar//2+7],fill=col)
    cd.text((104,bar//2),lab,font=PO('800',22),fill=GR,anchor='lm')
    if shadow:
        sh=Image.new('RGBA',(w+160,h+160),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([80,105,80+w,105+h],rad,fill=(0,0,0,70)); sh=sh.filter(ImageFilter.GaussianBlur(30)); fr.paste(sh,(x-80,y-80),sh)
    fr.paste(c,(x,y),R.rounded_mask((w,h),rad))
def chip(fr,xy,t,state=0,rot=0):
    f=PO('800',36); d0=ImageDraw.Draw(Image.new('RGB',(1,1))); tw=d0.textlength(t,font=f)
    w,h=int(tw+(118 if state else 64)),88; c=Image.new('RGBA',(w,h),(0,0,0,0)); cd=ImageDraw.Draw(c)
    cd.rounded_rectangle([0,0,w-1,h-1],20,fill=WH,outline=OR if state==0 else (230,230,230),width=4)
    tx=32
    if state: cd.ellipse([24,22,68,66],fill=OR); cd.line([(35,44),(44,54),(58,34)],fill=WH,width=7); tx=84
    cd.text((tx,h//2),t,font=f,fill=INK,anchor='lm'); c=c.rotate(rot,expand=True,resample=Image.BICUBIC); fr.paste(c,xy,c)
def safe(fr):
    d=ImageDraw.Draw(fr,'RGBA'); d.rectangle([0,0,W,230],fill=(0,120,255,40)); d.rectangle([0,1440,W,H],fill=(0,120,255,40)); d.rectangle([W-230,230,W,1440],fill=(0,120,255,40))
ITEMS=['FORMÜLASYON','STABİLİTE','MİKROBİYOLOJİK','CHALLENGE TEST','MSDS','PIF','CPSR','ÜTS BİLDİRİMİ','AMBALAJ','ETİKET','GRAFİK TASARIM','SERİ ÜRETİM']
T=[]
# 1 HOOK orange
fr=bg(OR); d=ImageDraw.Draw(fr)
stack(d,80,330,['KOZMETİK','SEKTÖRÜNE','GİRMEK','İSTİYOR','MUSUN?'],AN(158),[WH,WH,WH,INK,INK],178)
T.append(('HOOK','0–2','Turuncu zemin; kelimeler alttan fırlar (her kelime 0,3 sn), son iki kelime koyu. Kare 1\'de yazı zaten hareket halinde','VO: "Kozmetik sektörüne girmek istiyor musun?"',fr))
# 2 STAKE white pile
fr=bg(LG); random.seed(7); d=ImageDraw.Draw(fr)
pos=[(70,300),(420,330),(120,430),(460,470),(60,560),(400,600),(150,700),(470,740),(80,830),(380,880),(120,980),(430,1020)]
for (x,y),t in zip(pos,ITEMS): chip(fr,(x+random.randint(-30,30),y+random.randint(-20,20)+120),t,0,random.uniform(-14,14))
d.text((80,250),'12',font=AN(150),fill=OR); 
T.append(('STAKE','2–5,5','12 süreç kartı yukarıdan yağar, yığılır, hızlanır; sayaç 1>12 sayar','Sessiz, sadece düşme efektleri',fr))
# 3 TURN stamp
fr=bg(LG); d=ImageDraw.Draw(fr)
for i,t in enumerate(ITEMS[:5]):
    a=i/5*6.28; chip(fr,(int(330+300*math.cos(a)),int(820+430*math.sin(a))),t,0,int(25*math.sin(a)))
d.rounded_rectangle([110,720,890,1080],36,fill=OR); stack(d,500,745,['ANAHTAR','TESLİM'],AN(150),[WH,WH],160) if False else None
d.text((500,900),'ANAHTAR\nTESLİM',font=AN(150),fill=WH,anchor='mm',align='center',spacing=8)
T.append(('ÇÖZÜM','5,5–7','Kartlar turuncu kutuya emilir, "ANAHTAR TESLİM" damgası iner (damga sesi, müzik susar)','',fr))
# 4 PROMISE over door
fr=full('MIE_3.mp4',0.8,0.45); cap(fr,'Kendi markanı oluşturmak artık çok daha kolay.'.split(),3,y=900,size=76)
T.append(('VAAT','7–9','Kutu kapıya dönüşür: kapının ilk karesi; altyazı kelime kelime','VO: "Kendi markanı oluşturmak artık çok daha kolay."',fr))
# 5 REVEAL walk-in
fr=full('MIE_3.mp4',13.5,0.15,1.05); shade(fr,600,1100,200); d=ImageDraw.Draw(fr)
d.text((80,1010),'MİE KOZMETİK',font=AN(128),fill=WH)
d.rounded_rectangle([80,1180,780,1290],18,fill=OR); d.text((110,1235),'FASON ÜRETİM MERKEZİ',font=AN(72),fill=WH,anchor='lm')
T.append(('REVEAL','9–11,5','MIE_3 tek plan: kapıdan girilir, "DOLUM ALANI"na yürünür (gerçek kamera hareketi + hafif hız rampası)','VO: "Mie Kozmetik, fason üretim merkezi." Bas drop, müzik başlar',fr))
# 6 SCALE
fr=full('MIE_30.mp4',7,0.1); shade(fr,800,1300,190); cap(fr,'Onaylanan numune ile birebir aynı kalitede seri imalat.'.split(),6,y=1050,size=62)
T.append(('ÖLÇEK','11,5–14','Dev dolum hattı tam ekran, yavaş zoom-out','VO: "Onaylanan numune ile birebir aynı kalitede seri imalat."',fr))
# 7 STEPS checklist
fr=bg(LG); d=ImageDraw.Draw(fr)
for i in range(6): d.rounded_rectangle([80+i*125,250,190+i*125,262],6,fill=OR if i<4 else (215,215,215))
window(fr,grab('MIE_6..mp4',4),'02 · FORMÜLASYON GELİŞTİRME',(80,310,770,600))
for i,(t,s) in enumerate([('STRATEJİK PLANLAMA',1),('FORMÜLASYON GELİŞTİRME',1),('TASARIM VE AMBALAJ SEÇİMİ',1),('YASAL KAYITLAR',1)]):
    chip(fr,(80,960+i*112),t,s)
T.append(('ADIMLAR 01–04','14–17','Üstte ilerleme çubuğu; pencere içinde görüntü her 0,75 sn değişir (toplantı > lab > ambalaj rafı > ofis); listedeki kart tik alır','Tik sesleri, vuruşa kesme',fr))
# 8 SERI URETIM full + strip
fr=full('MIE_7.mp4',10,0.1); shade(fr,900,1300,170); d=ImageDraw.Draw(fr)
d.rounded_rectangle([80,250,840,330],40,fill=OR); d.text((110,290),'05 · SERİ ÜRETİM VE KALİTE KONTROL',font=PO('800',30),fill=WH,anchor='lm')
for k,(v,t) in enumerate([('MIE_9.mp4',6),('MIE_28.mp4',6),('MIE_38.mp4',6)]):
    window(fr,grab(v,t,True),['ÜRETİM','ÜRÜN DOLUMLARI','KALİTE KONTROL'][k],(80+k*258,1110,240,300),rad=20,bar=40,shadow=False)
T.append(('ADIM 05','17–19,5','Kazan tam ekran; altta 3 pencere sırayla açılır (pano > dolum > etiketli şişeler), her biri vuruşta','',fr))
# 9 FACT
fr=bg(WH); d=ImageDraw.Draw(fr)
for k,(v,t) in enumerate([('MIE_30.mp4',7),('MIE_28.mp4',6),('MIE_38.mp4',6),('MIE_9.mp4',6),('MIE_7.mp4',10),('MIE_3.mp4',20)]):
    im=R.cover(grab(v,t,True),(270,270)); im=Image.blend(im,Image.new('RGB',im.size,WH),0.35); fr.paste(im,(80+(k%3)*285,880+(k//3)*285),R.rounded_mask((270,270),22))
d.text((80,290),'ORTALAMA PROJE SÜRESİ',font=PO('800',40),fill=GR)
d.text((70,360),'3-6 HAFTA*',font=AN(180),fill=OR)
d.text((80,1440-50),'*Proje bazlı yeni ürünler için ek süre gerekebilir.',font=PO('600',26),fill=GR)
T.append(('BİLGİ','19,5–22','Rakam sayaçla dolar (0 > 3-6); arkada 6 gerçek makine penceresi','VO: "Ortalama proje süresi 3-6 hafta."',fr))
# 10 OUTRO
fr=bg(WH); d=ImageDraw.Draw(fr)
lg=LOGO.copy(); lg.thumbnail((560,560)); fr.paste(lg,(80,330),lg)
stack(d,80,700,['MARKANI OLUŞTUR,','ÜRETİMİNİ','BİZE BIRAK.'],AN(100),[INK,INK,OR],118)
d.rounded_rectangle([80,1160,850,1270],55,fill=OR); d.text((465,1215),'Teklif ve Katalog İçin İletişime Geçin',font=PO('800',32),fill=WH,anchor='mm')
d.text((80,1320),'miepharma.com',font=PO('600',34),fill=GR)
T.append(('ÖDÜL + ÇAĞRI','22–25','Orijinal logo; cümle kelime kelime; CTA nabız gibi. Son kare turuncuya kesilir = döngü başa bağlanır','VO: "Markanı oluştur, üretimini bize bırak."',fr))
# board
tw,th=300,533; cols=5; cf=PO('800',17); nf=PO('600',13)
rows=(len(T)+cols-1)//cols; bh=th+150
board=Image.new('RGB',(cols*(tw+14)+14,rows*bh+14),'white'); bd=ImageDraw.Draw(board)
for i,(k,tm,note,vo,fr) in enumerate(T):
    x=14+(i%cols)*(tw+14); y=14+(i//cols)*bh
    bd.text((x,y),f'{i+1:02d} {k} · {tm} sn',font=cf,fill='black')
    f2=fr.copy(); safe(f2); board.paste(f2.resize((tw,th),Image.LANCZOS),(x,y+26))
    yy=y+th+34
    for txt,col in [(note,(60,60,60)),(vo,OR)]:
        line=''
        for w in txt.split():
            if bd.textlength(line+' '+w,font=nf)>tw: bd.text((x,yy),line,font=nf,fill=col); yy+=17; line=w
            else: line=(line+' '+w).strip()
        if line: bd.text((x,yy),line,font=nf,fill=col); yy+=19
board.save(OUT,quality=88); print('ok',len(T))
