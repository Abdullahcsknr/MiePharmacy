import json,base64,glob,os,re,sys
out=sys.argv[1]
for f in sorted(glob.glob(sys.argv[2]+'/mcp-Google_Drive-download_file_content-17916*.txt')):
    d=json.load(open(f)); t=d['title']
    t=t.replace('M─░E','MIE').replace('MİE','MIE').replace('V─░DEOSU','VIDEOSU').replace('KAPANI┼₧','KAPANIS')
    t=re.sub(r'[^A-Za-z0-9_.]+','_',t)
    open(os.path.join(out,t),'wb').write(base64.b64decode(d['content']))
