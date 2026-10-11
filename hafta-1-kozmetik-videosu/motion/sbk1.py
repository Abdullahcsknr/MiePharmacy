"""Kozmetik Reels storyboard v1 panosu (fason sb5 stilinde)."""
import sys, subprocess
sys.path.insert(0, sys.argv[1]); import render as R
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S, REPO, OUT = sys.argv[2], sys.argv[3], sys.argv[4]; W, H = 1080, 1920
OR=(255,100,24); WH=(255,255,255); GR=(85,85,85); LG=(244,244,244); INK=(20,20,20)
FD=f'{REPO}/motion/fonts'; AN=lambda s: ImageFont.truetype(f'{FD}/anton-400.ttf',s); PO=lambda w,s: ImageFont.truetype(f'{FD}/poppins-{w}.ttf',s)
LOGO=Image.open(f'{REPO}/kimlik/logo-mie-siyah-hd.png')
def grab(v,t,hd=False):
    p=f'{S}/sb/k.png'; subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',(f'{S}/hd/{v}' if hd else f'{S}/{v}'),'-frames:v','1',p]); return Image.open(p).convert('RGB')
def full(v,t,dim=0.3,hd=False): return Image.blend(R.cover(grab(v,t,hd),(W,H)),Image.new('RGB',(W,H)),dim)
def cap(fr,text,y,size=74,active=1,col=WH,box=OR):
    f=PO('900',size); d=ImageDraw.Draw(fr); words=text.split(); lines=[[]]
    for w in words:
        if f.getlength(' '.join(lines[-1]+[w]))>770 and lines[-1]: lines.append([w])
        else: lines[-1].append(w)
    k=0
    for ln in lines:
        x=80
        for w in ln:
            bw=f.getlength(w)
            if k==active: d.rounded_rectangle([x-12,y-6,x+bw+12,y+size+14],14,fill=box)
            else: d.text((x+2,y+4),w,font=f,fill=(0,0,0) if col==WH else (230,230,230))
            d.text((x,y),w,font=f,fill=col); x+=bw+f.getlength(' '); k+=1
        y+=size+28
def window(fr,src,lab,box,rad=28,bar=54):
    x,y,w,h=box; c=Image.new('RGB',(w,h),WH); c.paste(R.cover(src,(w,h-bar)),(0,bar)); d=ImageDraw.Draw(c)
    r,g,x0=(7,22,24) if bar>45 else (5,15,16)
    for j,col in enumerate([OR,(210,210,210),(210,210,210)]): d.ellipse([x0+j*g,bar//2-r,x0+j*g+2*r,bar//2+r],fill=col)
    lx=x0+2*g+2*r+(14 if bar>45 else 10); fs=22 if bar>45 else 16
    while fs>10 and PO('800',fs).getlength(lab)>w-lx-12: fs-=1
    d.text((lx,bar//2),lab,font=PO('800',fs),fill=GR,anchor='lm')
    sh=Image.new('RGBA',(w+160,h+160),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([80,105,80+w,105+h],rad,fill=(0,0,0,70)); sh=sh.filter(ImageFilter.GaussianBlur(30)); fr.paste(sh,(x-80,y-80),sh)
    fr.paste(c,(x,y),R.rounded_mask((w,h),rad))
def chip(fr,xy,t,fill=WH,col=INK,size=34):
    f=PO('800',size); w=int(f.getlength(t)+56); h=size+40; c=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(c)
    d.rounded_rectangle([0,0,w-1,h-1],h//2,fill=fill); d.text((28,h//2),t,font=f,fill=col,anchor='lm'); fr.paste(c,xy,c); return w
def safe(fr):
    d=ImageDraw.Draw(fr,'RGBA'); d.rectangle([0,0,W,230],fill=(0,120,255,40)); d.rectangle([0,1440,W,H],fill=(0,120,255,40)); d.rectangle([W-230,230,W,1440],fill=(0,120,255,40))
V=lambda n: f'vids/{n}.mp4'
T=[]
fr=full(V('06'),5.5,0.25); cap(fr,'Hassas ciltlerde nasıl işlem yapılmalıdır?',800,80,0)
T.append(('HOOK','0–3','Jel dökülmesi makro, tam ekran. Soru kelime kelime (kare 1\'de hareket)','VO: "Hassas ciltlerde nasıl işlem yapılmalıdır?"',fr))
fr=Image.new('RGB',(W,H),OR); ws=[('02',4),('04',9),('05',10),('06',10),('08',9),('09',9)]
for k,(n,t) in enumerate(ws): window(fr,grab(V(n),t),'',(80+(k%3)*262,300+(k//3)*400,240,370),20,36)
cap(fr,'Hassas ciltlerde çözüm daha fazla ürün kullanmak değildir.',1110,62,4,WH,INK)
T.append(('CEVAP','3–7','Turuncu zemin: ürün pencereleri birikir ("daha fazla ürün"); "değildir" kelimesinde hepsi kapanır, tek pencere kalır','VO: "Hassas ciltlerde çözüm daha fazla ürün kullanmak değildir."',fr))
fr=full(V('07'),5.6,0.3); cap(fr,'Doğru içeriklerle cildi sakinleştirmek ve bariyeri korumaktır.',900,68,1)
T.append(('İÇGÖRÜ','7–10,5','Elde ürün (gerçek el, tek pencere tam ekrana açılır)','VO: "Doğru içeriklerle cildi sakinleştirmek ve bariyeri korumaktır."',fr))
fr=Image.new('RGB',(W,H),LG); window(fr,grab(V('05'),4),'MİE YÜZ TEMİZLEME SÜTÜ',(80,300,770,820)); chip(fr,(80,1180),'Her cilt tipine uygundur.',OR,WH,36)
T.append(('ÜRÜN 1','10,5–13,5','Pencere (referans stil), başlık = sitedeki ürün adı; altta site ifadesi','VO: "Her cilt tipine uygundur."',fr))
fr=Image.new('RGB',(W,H),LG); window(fr,grab(V('06'),10.5),'MİE C VİTAMİNLİ YÜZ TEMİZLEME JELİ',(80,300,770,820)); chip(fr,(80,1180),'tahriş etmeyen güçlü cilt temizliği',OR,WH,32)
T.append(('ÜRÜN 2','13,5–16,5','Aynı pencere, görüntü ve başlık değişir; doku makrosuna kesme (6. sn jel)','VO: "Cildi rahatlatıcı ve tahriş etmeyen güçlü cilt temizliği."',fr))
fr=full('MIE_28.mp4',6,0.15,True); d=ImageDraw.Draw(fr)
g=Image.new('L',(1,H)); [g.putpixel((0,y),max(0,min(200,int((y-800)*0.5)))) for y in range(H)]; fr.paste((0,0,0),(0,0,W,H),g.resize((W,H)))
d.text((80,1040),'YERLİ ÜRETİM,',font=AN(128),fill=WH); d.text((80,1180),'ÖZEL FORMÜL',font=AN(128),fill=OR)
window(fr,grab('arsiv/MIE_6..mp4',4),'FORMÜLASYON',(80,330,420,330),22,44)
T.append(('GÜVEN','16,5–20','Gerçek dolum hattı (fason arşivi) + lab penceresi','VO: "Yerli üretim, özel formül."',fr))
fr=Image.new('RGB',(W,H),WH); d=ImageDraw.Draw(fr); lg=LOGO.copy(); lg.thumbnail((520,520)); fr.paste(lg,(80,320),lg)
d.text((80,600),'DERMATOLOGICAL SKINCARE',font=PO('800',40),fill=GR)
d.text((80,690),'PROFESYONEL',font=AN(118),fill=INK); d.text((80,820),'DERMOKOZMETİK',font=AN(118),fill=INK); d.text((80,950),'ÇÖZÜMLER',font=AN(118),fill=OR)
x=80
for t in ['#Klinik','#Güzellik merkezleri','#Uzmanlar']:
    if x+PO('800',30).getlength(t)+56>850: x=80
    x+=chip(fr,(x,1150 if t!='#Uzmanlar' else 1235),t,LG,INK,30)+14
T.append(('MARKA','20–24','Orijinal logo, konumlandırma satır satır, etiketler pop','VO: "Mie Dermatological Skincare. Profesyonel dermokozmetik çözümler."',fr))
fr=Image.new('RGB',(W,H),WH); d=ImageDraw.Draw(fr); lg=LOGO.copy(); lg.thumbnail((420,420)); fr.paste(lg,(80,330),lg)
d.text((80,620),'BİZİMLE',font=AN(120),fill=INK); d.text((80,760),'İLETİŞİME GEÇİN',font=AN(120),fill=OR)
c=Image.new('RGB',(770,300),LG); cd=ImageDraw.Draw(c); cd.rounded_rectangle([0,0,769,299],36,outline=OR,width=4)
cd.text((40,52),'İLETİŞİM',font=PO('800',26),fill=GR,anchor='lm'); cd.text((136,120),'@mie_cosmeticss',font=PO('800',46),fill=INK,anchor='lm'); cd.text((136,220),'miepharma.com',font=PO('800',46),fill=INK,anchor='lm')
cd.ellipse([40,84,112,156],outline=OR,width=5); cd.ellipse([40,184,112,256],outline=OR,width=5)
fr.paste(c,(80,1080),R.rounded_mask((770,300),36))
T.append(('ÇAĞRI','24–28','Fason v6 iletişim kartı animasyonu (ikon zıplar, daktilo, ışık geçer); son kare turuncu = döngü','VO: "Bizimle iletişime geçin."',fr))
tw,th=300,533; cols=4; cf=PO('800',17); nf=PO('600',13); bh=th+150
board=Image.new('RGB',(cols*(tw+14)+14,2*bh+14),'white'); bd=ImageDraw.Draw(board)
for i,(k,tm,note,vo,fr) in enumerate(T):
    x=14+(i%cols)*(tw+14); y=14+(i//cols)*bh; bd.text((x,y),f'{i+1:02d} {k} · {tm} sn',font=cf,fill='black')
    f2=fr.copy(); safe(f2); board.paste(f2.resize((tw,th),Image.LANCZOS),(x,y+26)); yy=y+th+34
    for txt,col in [(note,(60,60,60)),(vo,OR)]:
        line=''
        for w in txt.split():
            if bd.textlength(line+' '+w,font=nf)>tw: bd.text((x,yy),line,font=nf,fill=col); yy+=17; line=w
            else: line=(line+' '+w).strip()
        if line: bd.text((x,yy),line,font=nf,fill=col); yy+=19
board.save(OUT,quality=88); print('ok')
