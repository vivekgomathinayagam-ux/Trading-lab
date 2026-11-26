"""Row delete and row insert in a running LibreOffice. Run: /usr/bin/python3 qa_propdd_rows_uno.py"""
import os, subprocess, sys, time, uno
from com.sun.star.beans import PropertyValue
HERE=os.path.dirname(os.path.abspath(__file__)); F=os.path.join(HERE,"..","..","Funded Account Drawdown Tracker.xlsx")
proc=subprocess.Popen(["soffice","--headless","--norestore","--accept=pipe,name=qapdd;urp;"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
local=uno.getComponentContext(); res=local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver",local)
ctx=None
for _ in range(60):
    try: ctx=res.resolve("uno:pipe,name=qapdd;urp;StarOffice.ComponentContext"); break
    except Exception: time.sleep(0.5)
desk=ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop",ctx)
p=PropertyValue(); p.Name="Hidden"; p.Value=True
doc=desk.loadComponentFromURL(uno.systemPathToFileUrl(os.path.abspath(F)),"_blank",0,(p,))
d=doc.Sheets.getByName("Daily log"); r=doc.Sheets.getByName("Rules")
c=lambda s,a: s.getCellRangeByName(a)
fails=[]
def check(n,got,want):
    if not (abs(got-want)<1e-6 if isinstance(want,(int,float)) else got==want): fails.append(f"{n}: got {got!r} want {want!r}")
def day(row,date,pnl): c(d,f"A{row}").setValue(date); c(d,f"B{row}").setValue(pnl)
def errs():
    out=[f"{col}{x}" for col in "CDEFGHJK" for x in range(5,30) if c(d,f"{col}{x}").getError()]
    return out+["Rules!B%d"%x for x in range(9,23) if c(r,f"B{x}").getError()]
# 1) delete the eight sample rows, then log three days
d.Rows.removeByIndex(4,8); day(5,46300,500); day(6,46301,-200); day(7,46302,-300); doc.calculateAll()
check("delete errors",errs(),[]); check("days",c(r,"B11").getValue(),3); check("balance",c(r,"B12").getValue(),50000)
check("floor",c(r,"B14").getValue(),48500); check("last",c(r,"B17").getValue(),-300); check("status",c(r,"B22").getString(),"OK")
check("row flag",c(d,"J7").getString(),"OK")
# 2) insert an empty row between days and type a loss over the daily limit: must not read OK (the floor is not hit)
d.Rows.insertByIndex(5,1); day(6,46300.5,-1100); doc.calculateAll()
check("insert flagged",c(r,"B22").getString(),"CHECK LOG: a row has no formulas")
# 3) copy a full formula row into it: counted and the breach shows
d.copyRange(c(d,"A6").getCellAddress(), c(d,"A5:K5").getRangeAddress()); day(6,46300.5,-1100); doc.calculateAll()
check("copied errors",errs(),[]); check("copied counted",c(r,"B11").getValue(),4); check("copied breach",c(r,"B22").getString(),"BREACHED: check your firm")
check("copied flag",c(d,"J6").getString(),"BREACH: daily limit")
doc.close(True)
try: desk.terminate()
except Exception: pass
proc.wait(timeout=30)
print("PASS (delete + insert + copy)" if not fails else "\n".join("FAIL "+f for f in fails)); sys.exit(bool(fails))
