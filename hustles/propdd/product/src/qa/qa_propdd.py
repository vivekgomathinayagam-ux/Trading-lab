"""Recalculates the Drawdown Tracker in LibreOffice and checks it: bad inputs must never read "OK",
and random logs must match an independent Python model.
Run: python3 qa_propdd.py   (needs openpyxl and soffice). Exits 1 on any failure."""
import datetime as dt, os, random, subprocess, sys, tempfile
import openpyxl
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(HERE,"..","..","Funded Account Drawdown Tracker.xlsx")
R,D="Rules","Daily log"; TRAIL="Trailing (end of day)"
TMP=tempfile.mkdtemp(); fails=[]; n=0; cases=[]
def check(name,ok,info=""):
    global n; n+=1
    if not ok: fails.append(f"{name}: {info}")
def log(vals,start=5,dates=True):
    """edits that replace the sample rows with vals (list of P&L values)"""
    e={}
    for r in range(5,13):
        for c in "ABI": e[(D,f"{c}{r}")]=None
    for i,v in enumerate(vals):
        r=start+i
        if dates: e[(D,f"A{r}")]=dt.date(2026,1,1)+dt.timedelta(days=i)
        e[(D,f"B{r}")]=v
    return e
def rules(start=50000,target=3000,daily=1000,dd=2000,kind=TRAIL,lock="Yes"):
    return {(R,"B3"):start,(R,"B4"):target,(R,"B5"):daily,(R,"B6"):dd,(R,"B7"):kind,(R,"B8"):lock}
def add(name,edits,fn): cases.append((name,edits,fn))
def run():
    files=[]
    for i,(name,edits,fn) in enumerate(cases):
        wb=openpyxl.load_workbook(SRC)
        for (sh,cell),v in edits.items(): wb[sh][cell].value=v
        f=os.path.join(TMP,f"c{i}.xlsx"); wb.save(f); files.append(f)
    out=os.path.join(TMP,"out")
    subprocess.run(["soffice","--headless","--convert-to","xlsx","--outdir",out]+files,check=True,capture_output=True)
    for i,(name,edits,fn) in enumerate(cases):
        wb=openpyxl.load_workbook(os.path.join(out,f"c{i}.xlsx"),data_only=True)
        bad=[(ws.title,c.coordinate,c.value) for ws in wb.worksheets for row in ws.iter_rows() for c in row
             if isinstance(c.value,str) and c.value.startswith(("#","Err:"))]
        check(name+" no formula errors",not bad,bad[:3])
        fn(name,wb)

def status(wb): return str(wb[R]["B22"].value)
def never_ok(name,wb): check(name+" status",status(wb).startswith("CHECK"),status(wb))
def breached(name,wb): check(name+" status",status(wb).startswith("BREACHED"),status(wb))
def is_status(want):
    return lambda name,wb: check(name+" status",status(wb).startswith(want),status(wb))

# ---- independent model
def model(start,target,daily,dd,kind,lock,pnl):
    bal=start; high=start; rows=[]; any_breach=False
    for p in pnl:
        bal=round(bal+p,2); high=max(high,bal)
        floor=start-dd if kind=="Static" else (min(start,high-dd) if lock=="Yes" else high-dd)
        cush=round(bal-floor,2)
        if cush<=0: flag="BREACH: floor"
        elif daily and p<0 and round(-p-daily,2)>=0: flag="BREACH: daily limit"
        elif cush<dd*0.25: flag="Caution"
        else: flag="OK"
        any_breach |= flag.startswith("BREACH")
        rows.append((bal,high,round(floor,2),cush,flag))
    if any_breach: st="BREACHED"
    elif not pnl: st="No days logged"
    elif target and round(bal-start-target,2)>=0: st="Target reached"
    elif rows[-1][3]<dd*0.25: st="CAUTION"
    else: st="OK"
    return rows,st
def match(rl,pnl):
    rows,st=model(*rl,pnl)
    def fn(name,wb):
        d,r=wb[D],wb[R]
        for i,(bal,high,floor,cush,flag) in enumerate(rows):
            x=5+i
            got=tuple(d[f"{c}{x}"].value for c in "CDEFJ")
            ok=all(isinstance(g,(int,float)) and abs(g-w)<0.006 for g,w in zip(got[:4],(bal,high,floor,cush))) and got[4]==flag
            check(f"{name} row {x}",ok,f"got {got} want {(bal,high,floor,cush,flag)}")
        check(name+" status",status(wb).startswith(st),f"got {status(wb)} want {st}")
        if rows:
            for cell,w in (("B12",rows[-1][0]),("B13",rows[-1][1]),("B14",rows[-1][2]),("B15",rows[-1][3]),("B17",pnl[-1])):
                g=r[cell].value; check(f"{name} {cell}",isinstance(g,(int,float)) and abs(g-w)<0.006,f"got {g} want {w}")
    return fn

sample=[420,-310,880,-850,650,1200,-450,300]
add("sample file",{},match((50000,3000,1000,2000,TRAIL,"Yes"),sample))
rng=random.Random(7)
for k in range(60):
    st=rng.choice([10000,25000,50000]); dd=rng.choice([500,1000,2500]); daily=rng.choice([0,250,600,1100])
    target=rng.choice([0,800,3000]); kind=rng.choice([TRAIL,"Static"]); lock=rng.choice(["Yes","No"])
    pnl=[rng.choice([-1,1])*round(rng.uniform(0,dd*0.5),2) if rng.random()<0.9 else 0 for _ in range(rng.randint(0,14))]
    add(f"random {k}",{**rules(st,target,daily,dd,kind,lock),**log(pnl)},match((st,target,daily,dd,kind,lock),pnl))
# exact boundaries with cents
p=[-666.67,-666.66,-666.67]
add("floor hit exactly, cents",{**rules(daily=0),**log(p)},match((50000,3000,0,2000,TRAIL,"Yes"),p))
add("daily limit exactly",{**rules(),**log([-1000])},match((50000,3000,1000,2000,TRAIL,"Yes"),[-1000]))
# bad rules: never OK, no numbers shown
for name,cell,val in [("blank start","B3",None),("zero start","B3",0),("text start","B3","50k"),("blank target","B4",None),("negative target","B4",-1),
    ("blank daily","B5",None),("negative daily","B5",-1000),("text daily","B5","none"),("blank drawdown","B6",None),("zero drawdown","B6",0),
    ("negative drawdown","B6",-2000),("bad type","B7","Intraday"),("blank type","B7",None),("bad lock","B8","Maybe")]:
    def fn(nm,wb):
        never_ok(nm,wb)
        shown=[wb[R][c].value for c in ("B12","B14","B15")]+[wb[D]["E8"].value]
        check(nm+" numbers hidden",all(v in (None,"") for v in shown),shown)
    add(name,{(R,cell):val},fn)
# bad log entries
add("loss typed as text",{**log([100,"-1500"])},never_ok)
add("text only",{**log(["abc"])},never_ok)
e=log([-600,-600]); e[(D,"A6")]=e[(D,"A5")]
add("same date twice",e,never_ok)
e=log([100,-100]); e[(D,"A6")]=dt.date(2025,12,1)
add("date out of order",e,never_ok)
e=log([100,-100]); e[(D,"A6")]=None
add("date missing",e,never_ok)
e=log([100,-100]); e[(D,"A6")]="yesterday"
add("date as text",e,never_ok)
add("breach not hidden by a bad row",{**log([-1500,"x"])},breached)
e=log([100]); e[(D,"A205")]=dt.date(2026,3,1); e[(D,"B205")]=-5000
add("entry below last formula row",e,never_ok)
e=log([100,-1500]);
for c in "CDEFGHJK": e[(D,f"{c}6")]=None
add("row without formulas",e,never_ok)
def gap(name,wb):
    check(name+" last day",wb[R]["B17"].value==-250,wb[R]["B17"].value)
    check(name+" daily used",abs((wb[R]["B18"].value or 0)-0.25)<1e-9,wb[R]["B18"].value)
e=log([100]); e[(D,"A8")]=dt.date(2026,1,9); e[(D,"B8")]=-250
add("blank row in the middle",e,gap)
e=log([100]); e[(D,"A6")]=dt.date(2026,1,2)
add("date typed ahead of its P&L",e,is_status("OK"))
add("empty log",log([]),is_status("No days logged"))
full=[10]*200
add("200 rows",{**rules(target=0),**log(full)},match((50000,0,1000,2000,TRAIL,"Yes"),full))
run()
print(f"{n-len(fails)}/{n} checks passed")
for f in fails[:60]: print("FAIL",f)
sys.exit(1 if fails else 0)
