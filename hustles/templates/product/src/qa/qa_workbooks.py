"""Recalculates the Toolkit workbooks in LibreOffice and checks them, including bad inputs.
Run: python3 qa_workbooks.py   (needs openpyxl and soffice). Exits 1 on any failure."""
import datetime as dt, os, subprocess, sys, tempfile
import openpyxl
HERE=os.path.dirname(os.path.abspath(__file__)); P=os.path.join(HERE,"..","..")
CALC=os.path.join(P,"Options Risk and Position Size Calculator.xlsx")
JRN=os.path.join(P,"Options Day Trader Journal.xlsx")
TMP=tempfile.mkdtemp(); fails=[]; n=0
def check(name,got,want):
    global n; n+=1
    ok = abs(got-want)<1e-6 if isinstance(want,(int,float)) and isinstance(got,(int,float)) else got==want
    if not ok: fails.append(f"{name}: got {got!r}, want {want!r}")
def recalc(src,name,edits=None):
    wb=openpyxl.load_workbook(src)
    for (sh,cell),v in (edits or {}).items(): wb[sh][cell].value=v
    f=os.path.join(TMP,name+".xlsx"); wb.save(f); out=os.path.join(TMP,"out")
    subprocess.run(["soffice","--headless","--convert-to","xlsx","--outdir",out,f],check=True,capture_output=True)
    return openpyxl.load_workbook(os.path.join(out,name+".xlsx"),data_only=True)
def errors(wb):
    bad=[]
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value,str) and c.value.startswith("#") and c.value!="#":
                    # empty chart slots on Stats are #N/A on purpose
                    if not (ws.title=="Stats" and c.column==6 and 23<=c.row<=82 and c.value=="#N/A"): bad.append((ws.title,c.coordinate,c.value))
    return bad
L,V,J="Long option","Vertical spread","Journal"

# ---- calculator, valid inputs (defaults: account 5000, 5% = 250)
w=recalc(CALC,"c0"); l,v=w[L],w[V]
check("long max loss",l["B11"].value,1.25*2*100+2); check("long per contract",l["B12"].value,126)
check("long breakeven",l["B13"].value,500+1.25+2/200); check("long n",l["B17"].value,250//126)
check("long fits",str(l["B16"].value).startswith("No: max loss"),True); check("long check",l["B18"].value,"OK")
check("vert max loss",v["B14"].value,212); check("vert max profit",v["B15"].value,288); check("vert be",v["B16"].value,502.1)
check("vert fits",v["B19"].value,"Yes"); check("vert n",v["B20"].value,1); check("calc errors",errors(w),[])
# the four spread types: (type, price, max loss, max profit, breakeven) for 500/505, 1 contract, $2 fees
for i,(t,px,ml,mp,be) in enumerate([("Bull call (debit)",2.1,212,288,502.1),("Bear put (debit)",2.1,212,288,502.9),
    ("Bull put (credit)",1.5,352,148,503.5),("Bear call (credit)",1.5,352,148,501.5)]):
    v=recalc(CALC,f"t{i}",{(V,"B3"):t,(V,"B6"):px})[V]
    for cell,want in (("B14",ml),("B15",mp),("B16",be),("B21","OK")): check(f"{t} {cell}",v[cell].value,want)
# boundary: a limit that is an exact multiple of the per-contract loss
l=recalc(CALC,"bd",{("Account","B3"):70000,("Account","B4"):0.01,(L,"B3"):0.07,(L,"B4"):100,(L,"B6"):0})[L]
check("boundary n",l["B17"].value,100); check("boundary fits",l["B16"].value,"Yes")
# bad inputs must never say Yes or give a contract count
bad_long={"blank premium":{(L,"B3"):None},"zero contracts":{(L,"B4"):0},"half contract":{(L,"B4"):1.5},"blank mult":{(L,"B5"):None},
 "negative fees":{(L,"B6"):-1},"blank strike":{(L,"B8"):None},"text premium":{(L,"B3"):"abc"},"bad type":{(L,"B7"):"x"}}
for k,e in bad_long.items():
    w=recalc(CALC,"bl"+str(abs(hash(k))),e); l=w[L]
    check(k+" fits",str(l["B16"].value).startswith("Check inputs: "),True)
    for c in ("B11","B12","B13","B17"): check(f"{k} {c} blank",l[c].value in (None,""),True)
    check(k+" errors",errors(w),[])
bad_v={"blank price":{(V,"B6"):None},"zero contracts":{(V,"B7"):0},"blank strikes":{(V,"B4"):None,(V,"B5"):None},
 "reversed debit":{(V,"B4"):505,(V,"B5"):500},"reversed credit":{(V,"B3"):"Bull put (credit)",(V,"B4"):505,(V,"B5"):500},
 "credit over width":{(V,"B3"):"Bear call (credit)",(V,"B6"):6.0},"debit over width":{(V,"B6"):5.0},"bad type":{(V,"B3"):"Condor"},"text strike":{(V,"B4"):"x"}}
for k,e in bad_v.items():
    w=recalc(CALC,"bv"+str(abs(hash(k))),e); v=w[V]
    check("v "+k+" fits",str(v["B19"].value).startswith("Check inputs: "),True)
    for c in ("B14","B15","B16","B18","B20"): check(f"v {k} {c} blank",v[c].value in (None,""),True)
    check("v "+k+" errors",errors(w),[])

# ---- journal: independent Python figures
def pnl(d,en,ex,q,m,f): return round(((en-ex) if d=="Short" else (ex-en))*q*m-f,2)
base=[("Long",1.20,1.85,2,100,2),("Long",2.10,1.40,1,100,1),("Short",1.50,2.30,2,100,2),("Long",0.80,0.55,3,100,3),("Long",1.00,1.90,2,100,2)]
p=[pnl(*t) for t in base]
w=recalc(JRN,"j0"); s=w["Stats"]
check("j trades",s["B3"].value,5); check("j total",s["B7"].value,round(sum(p),2)); check("j streak L",s["B22"].value,3); check("j streak W",s["B21"].value,1)
check("chart 5th",s["F27"].value,round(sum(p),2)); check("chart 6th empty",s["F28"].value,"#N/A"); check("j errors",errors(w),[])
check("month",w["Calendar"]["B17"].value,round(sum(p),2))
w=recalc(JRN,"jmid",{("Calendar","E1"):dt.date(2026,10,15)}); check("mid-month date",w["Calendar"]["B17"].value,round(sum(p),2))
# multiplier is pre-filled, so a new row without it is right; a cleared one is flagged, an open trade is not counted
def row(r,**k): return {(J,f"{c}{r}"):v for c,v in k.items()}
e={}
e.update(row(7,A=dt.date(2026,10,9),C="ORB",D="Long",E=1.0,F=1.5,G=1,I=1,J=100))
e.update(row(8,A=dt.date(2026,10,9),C="ORB",D="Long",E=1.0,G=1,I=1,J=100))
e.update(row(9,A=dt.date(2026,10,9),C="ORB",D="Long",E=1.0,F=1.5,G=1,H=None,I=1,J=100))
w=recalc(JRN,"j1",e); j,s,b=w[J],w["Stats"],w["By Setup"]
check("prefill pnl",j["L7"].value,49); check("open blank",j["L8"].value in (None,""),True); check("open result",j["N8"].value in (None,""),True)
check("cleared mult flagged",j["N9"].value,"Check qty"); check("cleared mult no pnl",j["L9"].value in (None,""),True)
check("count",s["B3"].value,6)
orb=[p[0],p[2],p[4],49]; check("bysetup trades",b["B2"].value,4); check("bysetup winrate",b["C2"].value,sum(x>0 for x in orb)/4); check("bysetup total",b["D2"].value,sum(orb))
check("j1 errors",errors(w),[])
# 75 closed trades: chart shows trades 16..75
e={}; run=[]; 
for i in range(75):
    r=2+i; e.update(row(r,A=dt.date(2026,10,1),B="SPY",C="ORB",D="Long",E=1.0,F=1.0+(0.10 if i%3 else -0.15),G=1,H=100,I=1,J=100))
    run.append(round((run[-1] if run else 0)+pnl("Long",1.0,1.0+(0.10 if i%3 else -0.15),1,100,1),2))
w=recalc(JRN,"j75",e); s=w["Stats"]
check("75 count",s["B3"].value,75); check("chart first #",s["E23"].value,16); check("chart first",s["F23"].value,run[15])
check("chart last #",s["E82"].value,75); check("chart last",s["F82"].value,run[74]); check("75 errors",errors(w),[])
print(f"{n-len(fails)}/{n} checks passed")
for f in fails: print("FAIL",f)
sys.exit(1 if fails else 0)
