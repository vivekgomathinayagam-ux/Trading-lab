"""Volume-guard impact: desk replays with Features(vol_guard=False) vs True (research/foundry/volguard_REPORT.md).

  python lab/foundry/volguard_impact.py <archive dir> <trade_from YYYY-MM-DD> <out.json>
"""
import sys, json, functools
from pathlib import Path
import numpy as np, pandas as pd
import lab.foundry.batch7 as b7
from strategies.daytrade import core
from strategies.daytrade.core import ORB, EMACross, VolSpike, EMACrossV2
src=Path(sys.argv[1]); trade_from=sys.argv[2]; out=sys.argv[3]
rules={"orb_vol":ORB(),"ema_vol":EMACross(),"volspike":VolSpike(),"ema_vol_v2":EMACrossV2(),
       "orb_plain":ORB(None),"ema_plain":EMACross(None),"volspike_2x":VolSpike(2.0)}
data=b7.load_all(src)
res={}; tabs={}
orig=core.Features
for g in (False, True):
    b7.Features=functools.partial(orig, vol_guard=g)
    s=b7.signal_table(data,rules,trade_from)
    tabs[g]={k:b7.pick(s[s.rule==k]) for k in rules}
for k in rules:
    a,b=tabs[False][k],tabs[True][k]
    ka=set(zip(a.day,a.sym,a.t.astype(str))); kb=set(zip(b.day,b.sym,b.t.astype(str)))
    res[k]={"n_off":len(a),"n_on":len(b),"mean_off":round(float(a.pnl.mean()),4) if len(a) else None,
            "mean_on":round(float(b.pnl.mean()),4) if len(b) else None,"only_off":len(ka-kb),"only_on":len(kb-ka),
            "sum_off":round(float(a.pnl.sum()),3),"sum_on":round(float(b.pnl.sum()),3),
            "changed_days":sorted({d for d,_,_ in (ka^kb)})[:40]}
json.dump(res,open(out,'w'),indent=1)
for k,v in res.items(): print(k,{x:y for x,y in v.items() if x!='changed_days'})
