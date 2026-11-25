"""Row delete and row insert in a running LibreOffice (what a buyer does with sample rows). Run: /usr/bin/python3 qa_rows_uno.py"""
import os, subprocess, sys, time, datetime as dt, uno
from com.sun.star.beans import PropertyValue
HERE=os.path.dirname(os.path.abspath(__file__)); J=os.path.join(HERE,"..","..","Options Day Trader Journal.xlsx")
proc=subprocess.Popen(["soffice","--headless","--norestore","--accept=pipe,name=qapipe;urp;"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
ctx=None
local=uno.getComponentContext(); res=local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver",local)
for _ in range(60):
    try: ctx=res.resolve("uno:pipe,name=qapipe;urp;StarOffice.ComponentContext"); break
    except Exception: time.sleep(0.5)
desk=ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop",ctx)
p=PropertyValue(); p.Name="Hidden"; p.Value=True
doc=desk.loadComponentFromURL(uno.systemPathToFileUrl(os.path.abspath(J)),"_blank",0,(p,))
sh=doc.Sheets.getByName("Journal"); st=doc.Sheets.getByName("Stats")
c=lambda s,a: s.getCellRangeByName(a)
fails=[]
def check(n,got,want):
    if not (abs(got-want)<1e-6 if isinstance(want,(int,float)) else got==want): fails.append(f"{n}: got {got!r} want {want!r}")
def trade(r,ex):
    c(sh,f"A{r}").setValue(46300); c(sh,f"C{r}").setString("ORB"); c(sh,f"D{r}").setString("Long")
    c(sh,f"E{r}").setValue(1.0); c(sh,f"F{r}").setValue(ex); c(sh,f"G{r}").setValue(1); c(sh,f"I{r}").setValue(0); c(sh,f"J{r}").setValue(100)
def errs():
    out=[]
    for col in "LMNOPQSTU":
        for r in range(1,30):
            if c(sh,f"{col}{r}").getError(): out.append(f"{col}{r}")
    for a in ("B3","B7","B16","B21","B22"):
        if c(st,a).getError(): out.append("Stats!"+a)
    return out
# 1) delete the five sample rows, then type two wins and one loss
sh.Rows.removeByIndex(1,5); trade(2,1.5); trade(3,1.4); trade(4,0.8); doc.calculateAll()
check("after delete errors",errs(),[]); check("trades",c(st,"B3").getValue(),3); check("total",c(st,"B7").getValue(),70)
check("win streak",c(st,"B21").getValue(),2); check("loss streak",c(st,"B22").getValue(),1); check("chart last",c(st,"F25").getValue(),70)
# 2) insert a copy of a whole row above the last journal row (now row 496) and type a trade in it
last=496; sh.Rows.insertByIndex(last-1,1)
sh.copyRange(c(sh,f"A{last}").getCellAddress(), c(sh,"A4:U4").getRangeAddress()); trade(last,1.2); doc.calculateAll()
check("after insert errors",errs(),[]); check("inserted row counted",c(st,"B3").getValue(),4); check("total2",c(st,"B7").getValue(),90)
check("running on inserted",c(sh,f"O{last}").getValue(),90); check("chart last2",c(st,"F26").getValue(),90)
doc.close(True)
try: desk.terminate()
except Exception: pass
proc.wait(timeout=30)
print("PASS (delete + insert)" if not fails else "\n".join("FAIL "+f for f in fails)); sys.exit(bool(fails))
