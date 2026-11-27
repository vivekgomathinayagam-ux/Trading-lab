"""Store images for the Drawdown Tracker, plus the Toolkit Stats screenshot.
Screenshots are exports of the shipped files (LibreOffice rendering, cropped to a cell range); cover art is original.
Run: python3 make_listing_art.py   (needs soffice, /usr/bin/python3 with uno, pdftoppm, Pillow, playwright)."""
import os, subprocess, sys, tempfile
from PIL import Image, ImageChops
HERE=os.path.dirname(os.path.abspath(__file__)); H=os.path.join(HERE,"..","..","..")
PD=os.path.join(H,"propdd","product"); TK=os.path.join(H,"templates","product")
TMP=tempfile.mkdtemp()
SHOTS=[(os.path.join(PD,"Funded Account Drawdown Tracker.xlsx"),"Rules","A1:D22",os.path.join(PD,"listing","screenshot-1-rules-status.png")),
       (os.path.join(PD,"Funded Account Drawdown Tracker.xlsx"),"Daily log","A1:J14",os.path.join(PD,"listing","screenshot-2-daily-log.png")),
       (os.path.join(TK,"Options Day Trader Journal.xlsx"),"Stats","A1:C22",os.path.join(TK,"listing","screenshot-1-stats.png"))]
UNO=r'''
import sys,time,subprocess,os,uno
from com.sun.star.beans import PropertyValue
def pv(n,v):
    p=PropertyValue(); p.Name=n; p.Value=v; return p
proc=subprocess.Popen(["soffice","--headless","--norestore","--accept=pipe,name=artpipe;urp;"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
local=uno.getComponentContext(); res=local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver",local)
for _ in range(60):
    try: ctx=res.resolve("uno:pipe,name=artpipe;urp;StarOffice.ComponentContext"); break
    except Exception: time.sleep(0.5)
desk=ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop",ctx)
a=sys.argv[1:]
for src,sheet,rng,out in zip(a[0::4],a[1::4],a[2::4],a[3::4]):
    doc=desk.loadComponentFromURL(uno.systemPathToFileUrl(src),"_blank",0,(pv("Hidden",True),))
    doc.calculateAll(); sh=doc.Sheets.getByName(sheet)
    st=doc.StyleFamilies.getByName("PageStyles").getByName(sh.PageStyle)
    st.IsLandscape=True; st.Width=33866; st.Height=19050; st.HeaderIsOn=False; st.FooterIsOn=False
    st.LeftMargin=st.RightMargin=st.TopMargin=st.BottomMargin=500; st.ScaleToPagesX=1; st.ScaleToPagesY=1
    fd=uno.Any("[]com.sun.star.beans.PropertyValue",(pv("Selection",sh.getCellRangeByName(rng)),))
    uno.invoke(doc,"storeToURL",(uno.systemPathToFileUrl(out),uno.Any("[]com.sun.star.beans.PropertyValue",(pv("FilterName","calc_pdf_Export"),pv("FilterData",fd)))))
    doc.close(True)
try: desk.terminate()
except Exception: pass
proc.wait(timeout=30)
'''
args=[]
for i,(src,sheet,rng,_) in enumerate(SHOTS): args+=[os.path.abspath(src),sheet,rng,os.path.join(TMP,f"s{i}.pdf")]
subprocess.run(["/usr/bin/python3","-c",UNO,*args],check=True,timeout=240)
for i,(_,_,_,out) in enumerate(SHOTS):
    base=os.path.join(TMP,f"s{i}")
    subprocess.run(["pdftoppm","-png","-r","220","-singlefile",base+".pdf",base],check=True)
    im=Image.open(base+".png").convert("RGB")
    box=ImageChops.difference(im,Image.new("RGB",im.size,"white")).getbbox(); im=im.crop(box)
    k=min(1220/im.width,660/im.height); im=im.resize((round(im.width*k),round(im.height*k)),Image.LANCZOS)
    c=Image.new("RGB",(1280,720),"white"); c.paste(im,((1280-im.width)//2,(720-im.height)//2)); c.save(out,optimize=True)
    print("wrote",os.path.relpath(out,H))
# ---- original cover art: a balance line above a floor that steps up behind it (made-up shape, no results)
bal=[40,52,44,66,50,72,96,84,108,92,98,80]
peak=[max(bal[:i+1]) for i in range(len(bal))]; floor=[min(p-34,66) for p in peak]
def pts(v,w,h,x0,y0): return [(x0+i*w/(len(v)-1),y0+h-(a-0)*h/140) for i,a in enumerate(v)]
def art(w,h,x0,y0):
    b=pts(bal,w,h,x0,y0); f=pts(floor,w,h,x0,y0)
    line=" ".join(f"{x:.0f},{y:.0f}" for x,y in b)
    d=f"M{f[0][0]:.0f},{f[0][1]:.0f}"+"".join(f" H{x:.0f} V{y:.0f}" for x,y in f[1:])
    gap=f"M{b[-1][0]:.0f},{b[-1][1]:.0f} V{f[-1][1]:.0f}"
    return (f'<path d="{d}" fill="none" stroke="#ff7a59" stroke-width="9" stroke-linejoin="round"/>'
            f'<polyline points="{line}" fill="none" stroke="#5ad1e6" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<path d="{gap}" stroke="#ffffff" stroke-width="4" stroke-dasharray="8 8"/>'
            f'<circle cx="{b[-1][0]:.0f}" cy="{b[-1][1]:.0f}" r="12" fill="#ffffff"/>')
CSS="html,body{margin:0;padding:0}body{font-family:Inter,sans-serif;background:#0c1a24;color:#fff;overflow:hidden;position:relative}div{position:absolute;white-space:nowrap}.h{font-weight:800;letter-spacing:-1px}.s{color:#b9cbd6;font-weight:600}.t{background:#ff7a59;color:#14100e;font-weight:800;border-radius:40px;padding:10px 22px}.p{border:4px solid #5ad1e6;color:#5ad1e6;font-weight:700;border-radius:14px;padding:12px 22px}svg{position:absolute;left:0;top:0}"
cover=f'''<style>{CSS}</style><body style="width:1280px;height:720px"><svg width="1280" height="720">{art(430,430,800,150)}</svg>
<div class="t" style="left:64px;top:70px;font-size:24px">FUNDED-ACCOUNT TRADERS</div>
<div class="h" style="left:62px;top:168px;font-size:88px;line-height:1.08">HOW FAR IS<br>YOUR <span style="color:#ff7a59">FLOOR?</span></div>
<div class="s" style="left:66px;top:410px;font-size:32px;line-height:1.5">Drawdown floor · cushion in dollars<br>daily-loss use, from your firm's rules</div>
<div class="p" style="left:64px;top:560px;font-size:30px">Spreadsheet (.xlsx) · $9</div></body>'''
thumb=f'''<style>{CSS}</style><body style="width:1280px;height:1280px"><svg width="1280" height="1280">{art(1080,470,100,590)}</svg>
<div class="h" style="left:90px;top:90px;font-size:150px;line-height:1.08">DRAWDOWN<br><span style="color:#ff7a59">TRACKER</span></div>
<div class="s" style="left:96px;top:450px;font-size:52px">Funded-account spreadsheet</div>
<div class="p" style="left:92px;top:1130px;font-size:52px">.xlsx · $9</div></body>'''
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    br=p.chromium.launch()
    for name,html,size in (("cover.png",cover,(1280,720)),("thumb_square.png",thumb,(1280,1280))):
        pg=br.new_page(viewport={"width":size[0],"height":size[1]}); pg.set_content(html); pg.evaluate("document.fonts.ready")
        pg.screenshot(path=os.path.join(PD,"listing",name)); pg.close(); print("wrote propdd/product/listing/"+name)
    br.close()
