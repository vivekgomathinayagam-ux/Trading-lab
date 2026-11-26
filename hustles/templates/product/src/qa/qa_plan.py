"""Recalculates the Plan & Checklist Pack in LibreOffice and checks it, including bad inputs.
Run: python3 qa_plan.py   (needs openpyxl and soffice). Exits 1 on any failure."""
import itertools, os, subprocess, sys, tempfile
import openpyxl
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(HERE,"..","..","Options Trading Plan and Checklist Pack.xlsx")
C,P,W="Pre-Trade Checklist","Daily Plan","Weekly Review"
TMP=tempfile.mkdtemp(); fails=[]; n=0; cases=[]
def check(name,ok,info=""):
    global n; n+=1
    if not ok: fails.append(f"{name}: {info}")
def add(name,edits,fn): cases.append((name,edits,fn))
def find(ws,label,col):
    for row in ws.iter_rows():
        for c in row:
            if c.value==label: return ws[f"{col}{c.row}"]
    raise KeyError(label)
def result(want):
    def fn(nm,wb):
        got=find(wb[C],"Result","C").value
        check(nm,got==want if want!="NOT GO" else got!="GO",f"got {got!r} want {want!r}")
    return fn
base=[r for r in openpyxl.load_workbook(SRC)[C].iter_rows(min_row=4,max_row=13,values_only=True)]
req=[4+i for i,r in enumerate(base) if r[3]=="Y"]; opt=[4+i for i,r in enumerate(base) if r[3]!="Y"]
ally={(C,f"C{r}"):"Y" for r in range(4,14)}
add("untouched",{},result("INCOMPLETE"))
add("all yes",ally,result("GO"))
add("optional blank",{k:v for k,v in ally.items() if int(k[1][1:]) not in opt},result("GO"))
for r in req:
    add(f"required row {r} = N",{**ally,(C,f"C{r}"):"N"},result("WAIT"))
    add(f"required row {r} blank",{**ally,(C,f"C{r}"):None},result("INCOMPLETE"))
add("answer 'maybe'",{**ally,(C,"C4"):"maybe"},result("NOT GO"))
add("no required rules",{(C,f"D{r}"):"N" for r in range(4,14)},result("NOT GO"))
add("required column cleared",{(C,f"D{r}"):None for r in range(4,14)},result("NOT GO"))
add("required typed as Yes",{**ally,(C,"D4"):"Yes",(C,"C4"):"N"},result("NOT GO"))
add("rule with no required flag",{**ally,(C,"D4"):None,(C,"C4"):"N"},result("NOT GO"))
add("own 11th rule unanswered",{**ally,(C,"B14"):"My extra rule",(C,"D14"):"Y"},result("INCOMPLETE"))
add("own 11th rule = N",{**ally,(C,"B14"):"My extra rule",(C,"D14"):"Y",(C,"C14"):"N"},result("WAIT"))
add("own 20th rule unanswered",{**ally,(C,"B23"):"My extra rule",(C,"D23"):"Y"},result("INCOMPLETE"))
def money(want_t,want_d):
    def fn(nm,wb):
        got=(wb[P]["B6"].value,wb[P]["B8"].value)
        for g,w in zip(got,(want_t,want_d)):
            check(nm,(isinstance(g,(int,float)) and abs(g-w)<1e-6) if w is not None else (isinstance(g,str) and g.startswith("Check")),f"got {got}")
    return fn
add("plan defaults",{},money(250,500))
for name,cell,val in [("blank account","B4",None),("zero account","B4",0),("negative account","B4",-5000),("text account","B4","5k")]:
    add(name,{(P,cell):val},money(None,None))
for name,val in [("blank",None),("zero",0),("5 meaning 500%",5),("negative",-0.05),("text","five")]:
    add(f"per-trade pct {name}",{(P,"B5"):val},money(None,500))
    add(f"daily pct {name}",{(P,"B7"):val},money(250,None))
def totals(t,b,p,good,days):
    def fn(nm,wb):
        ws=wb[W]; got=[find(ws,"Totals",c).value for c in "BCD"]+[find(ws,"Days with zero rule breaks","B").value,find(ws,"Days traded","B").value]
        check(nm,got==[t,b,p,good,days],f"got {got} want {[t,b,p,good,days]}")
    return fn
add("week sample",{},totals(6,1,-5,2,3))
add("six trading rows",{**{(W,f"A{r}"):f"d{r}" for r in range(4,10)},**{(W,f"B{r}"):1 for r in range(4,10)},**{(W,f"C{r}"):0 for r in range(4,10)},**{(W,f"D{r}"):10 for r in range(4,10)}},totals(6,0,60,6,6))
for i,(name,edits,fn) in enumerate(cases): pass
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
         if isinstance(c.value,str) and c.value.startswith(("#VALUE","#REF","#DIV","#NAME","#N/A","#NUM","Err:"))]
    check(name+" no formula errors",not bad,bad[:3])
    fn(name,wb)
print(f"{n-len(fails)}/{n} checks passed")
for f in fails: print("FAIL",f)
sys.exit(1 if fails else 0)
