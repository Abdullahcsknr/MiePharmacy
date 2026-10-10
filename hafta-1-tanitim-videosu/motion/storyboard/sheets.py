import glob,os,subprocess,sys,json
from PIL import Image,ImageDraw,ImageFont
src,out,tmp=sys.argv[1:4]
font=ImageFont.truetype(sys.argv[4],18)
vids=sorted(glob.glob(src+'/*.mp4'))
N=5; TW=230
rows=[]
for v in vids:
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',v]).decode().strip() or 1)
    ims=[]
    for k in range(N):
        t=d*(k+0.5)/N; p=f'{tmp}/f.jpg'
        subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{t:.2f}','-i',v,'-frames:v','1','-vf',f'scale={TW}:-2',p])
        ims.append(Image.open(p).convert('RGB').copy() if os.path.exists(p) else Image.new('RGB',(TW,130)))
        if os.path.exists(p): os.remove(p)
    h=max(i.height for i in ims)
    row=Image.new('RGB',(N*(TW+4)+4,h+30),'white'); dr=ImageDraw.Draw(row)
    dr.text((6,4),f'{os.path.basename(v)}  ({d:.1f}s)  t= '+' / '.join(f'{d*(k+0.5)/N:.1f}' for k in range(N)),font=font,fill='black')
    for k,i in enumerate(ims): row.paste(i,(4+k*(TW+4),26))
    rows.append(row)
for s in range(0,len(rows),7):
    grp=rows[s:s+7]; H=sum(r.height for r in grp)
    sh=Image.new('RGB',(grp[0].width,H),'white'); y=0
    for r in grp: sh.paste(r,(0,y)); y+=r.height
    sh.save(f'{out}/sheet_{s//7:02d}.jpg',quality=85)
print(len(rows))
