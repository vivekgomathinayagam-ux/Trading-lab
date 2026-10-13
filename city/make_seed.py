"""Writes the Compound City seed documents (city/seed/*.json).

REAL (sample: false): bot/Depot, Treasury, Watchtower, City Hall tasks,
decision timeline, real ticker events.
SAMPLE (sample: true): residents' activity, setup metrics/equity, hustle
stalls, trade log, newsstand note. Residents overwrite these with real
state once they run (Phase 0 step 6+).

Run:  python3 city/make_seed.py
"""
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT = Path(__file__).parent / "seed"
OUT.mkdir(exist_ok=True)
GH = "https://github.com/vivekgomathinayagam-ux/Trading-lab/blob/main/"
NOW = datetime(2026, 10, 13, 22, 15, tzinfo=timezone.utc)


def iso(dt):
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ago(**kw):
    return iso(NOW - timedelta(**kw))


def write(name, data):
    (OUT / f"{name}.json").write_text(json.dumps(data, indent=2))


SAMPLE_NOTE = ("Characters' activity, setup numbers and the trade log are SAMPLE until the residents start "
               "(step 6) and setups trade (step 7). The bot, Treasury, Watchtower, City Hall, hustles and "
               "decision timeline are real.")

# ---------------- city/state (mostly real) ----------------
state = {
    "as_of": iso(NOW),
    "sample_note": SAMPLE_NOTE,
    "bot": {
        "sample": False, "status": "running", "mode": "paper",
        "last_heartbeat": "2026-10-13T21:58:15Z",
        "deploy_status": "SUCCESS", "deployed_at": "2026-10-13T21:58:14Z",
        "commit": "296886a", "region": "us-east4",
        "checks": "5 of 5 Tradier sandbox checks passed. Ledger restored from the data branch (3 files). Paper account set to $1,000; baseline locks at the next open.",
        "as_of": "2026-10-13T21:58:15Z", "source": "Railway deploy logs · data/ledger/heartbeat.json",
    },
    "treasury": {
        "sample": False, "as_of": iso(NOW), "source": "STATE.md (capital rules set by Vivek, Oct 13) · ledger/money.csv (no rows yet)",
        "live_fund": {"base": 1000, "deposited": False, "hustle_added": 0, "trading_pnl": 0},
        "ops_fund": {"budget": 50, "deposited": False, "spent": 0,
                     "costs_month": [{"label": "Claude Pro", "amount": 20},
                                     {"label": "Railway", "amount": 0, "note": "paid by your existing subscription"}]},
        "hustle_income": 0, "income_month": 0,
    },
    "watchtower": {
        "sample": False, "as_of": "2026-10-13T21:58:15Z", "source": "engine/risk · ledger/risk_state.json",
        "mode": "paper", "caps": {"per_trade": 5, "daily": 10, "drawdown": 30},
        "used": {"per_trade_max": 0, "daily_loss": 0, "drawdown": 0},
        "kill_switch_on": False, "paper_equity": 1000, "live_equity_assumed": 1000,
    },
    "newsstand": {
        "sample": True, "as_of": ago(hours=9),
        "regime": "SAMPLE · Range-bound open expected",
        "note": "SAMPLE. The Newsie starts in step 6 and will post a real pre-market note here each weekday around 6:00 AM PT: calendar, news, regime, and which setups should sit out.",
        "events": [{"time": "5:30 AM PT", "text": "SAMPLE · Economic data release"}],
        "sit_out": [],
    },
    "ticker": [
        {"t": "2026-10-13T22:40:00Z", "text": "Claude posted 4 hustle one-pagers and an income question to City Hall", "sample": False},
        {"t": "2026-10-13T22:38:00Z", "text": "Capital set by Vivek: $1,000 live fund, $50 operations fund", "sample": False},
        {"t": "2026-10-13T21:58:15Z", "text": "Bot redeployed: $1,000 paper account, ledger restore, sticky kill switch", "sample": False},
        {"t": "2026-10-13T21:30:00Z", "text": "Pull request #1 merged by Vivek", "sample": False},
        {"t": "2026-10-13T21:10:45Z", "text": "Data branch created, first ledger snapshot pushed", "sample": False},
        {"t": "2026-10-13T21:10:42Z", "text": "Tradier sandbox: 5 of 5 connectivity checks passed", "sample": False},
        {"t": ago(minutes=12), "text": "Researcher started ORB SPY 15-minute range backtest", "sample": True},
        {"t": ago(minutes=40), "text": "Accountant reconciled 12 paper fills", "sample": True},
    ],
    "decisions": [
        {"date": "Oct 13", "text": "Capital set by Vivek: $1,000 for live trading only, $50 for running costs; Railway paid separately; hustle income goes to the live fund."},
        {"date": "Oct 13", "text": "Paper trading runs on its own with no trade confirmations; every fill is logged in the Ledger."},
        {"date": "Oct 13", "text": "Project owner is Vivek Gomathinayagam; his name is on every file and write-up."},
        {"date": "Oct 13", "text": "Live sizing assumes about $1,000 at go-live; the $50 cap on your own money is unchanged."},
        {"date": "Oct 13", "text": "Ledger and risk state restored from GitHub on restart; the kill switch stays on until you reset it."},
        {"date": "Oct 13", "text": "Paper trades run on a virtual $1,000 account with whole shares."},
        {"date": "Oct 13", "text": "Bot moved to a US East region; first deploy passed 5 of 5 Tradier checks."},
        {"date": "Oct 9", "text": "Shadow fills priced from a real-time last price plus 2 bps slippage."},
        {"date": "Oct 9", "text": "Risk engine built: 5% per trade, 10% daily stop, 30% drawdown kill switch, no margin, no naked shorts."},
        {"date": "Oct 9", "text": "Fresh start: repo built from zero."},
    ],
}
write("city__state", state)

# ---------------- agents ----------------
def hist(*items):
    return [{"t": ago(minutes=m), "text": f"SAMPLE · {txt}"} for m, txt in items]


residents = [
    dict(id="mayor", name="Mayor", short="Mayor", kind="resident", role="Weekly plan, Sundays", icon="flag",
         home="cityhall", district="core", status="asleep", action="SAMPLE · Posted the weekly plan to STATE.md",
         action_at=ago(days=2), progress=None, queue=["Sunday: weekly plan and district review"],
         history=hist((2880, "Posted the weekly plan"), (2900, "Reviewed every district")),
         links=[{"label": "STATE.md", "url": GH + "STATE.md"}]),
    dict(id="newsie", name="Newsie", short="Newsie", kind="resident", role="Pre-market note, weekdays 6 AM", icon="news",
         home="newsstand", district="trading", status="asleep", action="SAMPLE · Filed today's pre-market note",
         action_at=ago(hours=9), progress=None, queue=["Tomorrow 6:00 AM PT: pre-market note"],
         history=hist((540, "Filed the pre-market note"), (545, "Checked the bot heartbeat"))),
    dict(id="risk", name="Risk Officer", short="Risk", kind="resident", role="Daily risk check, 10 AM", icon="shield",
         home="watchtower", district="trading", status="waiting", action="SAMPLE · Waiting on the Railway deploy status",
         action_at=ago(minutes=3), progress=None, queue=["Check caps after deploy"],
         history=hist((3, "Asked Railway for deploy status"), (300, "All caps within limits"))),
    dict(id="accountant", name="Accountant", short="Accountant", kind="resident", role="Daily close, 1:30 PM", icon="coin",
         home="treasury", district="core", status="working", action="SAMPLE · Reconciling paper fills against Tradier",
         action_at=ago(minutes=6), progress=60, queue=["Update the Treasury", "Write the journal entry"],
         history=hist((6, "Started reconciling paper fills"), (40, "Reconciled 12 fills"))),
    dict(id="researcher", name="Researcher", short="Researcher", kind="resident", role="Backtests, Saturdays", icon="flask",
         home="lab", district="trading", status="working", action="SAMPLE · Backtesting ORB on SPY, 15-minute range (2 of 6 variants)",
         action_at=ago(minutes=12), progress=35,
         queue=["SAMPLE · CVD turn, 3-minute backtest", "SAMPLE · ORB TQQQ variants"],
         history=hist((12, "Started ORB SPY 15-minute backtest"), (90, "Downloaded 2 years of SPY minute bars"))),
]
for r in residents:
    r["sample"] = True
    r["real_note"] = "Not scheduled yet. Real activity starts in Phase 0 step 6."
residents.append(dict(
    id="scout", name="Hustle Scout", short="Scout", kind="resident", role="Hustle ideas, Wednesdays", icon="mega",
    home="market", district="hustles", status="needs_me", sample=False,
    action="4 hustle one-pagers and an income question are waiting for you at City Hall",
    action_at="2026-10-13T22:40:00Z", progress=None, handoff={"to": "cityhall", "active": True},
    queue=["Start whichever hustles you approve", "Wednesday: next round of ideas"],
    history=[{"t": "2026-10-13T22:40:00Z", "text": "Posted 4 one-pagers to City Hall"},
             {"t": "2026-10-13T22:30:00Z", "text": "Checked Gumroad, Etsy, Fiverr and TradingView fees and rules"}],
    links=[{"label": "hustles folder", "url": GH.replace("/blob/", "/tree/") + "hustles"}]))


def equity(seed, drift, vol, n=20):
    rnd = random.Random(seed)
    v, out = 0.0, []
    start = datetime(2026, 9, 15, 20, 0, tzinfo=timezone.utc)
    for i in range(n):
        if i:
            v += drift + rnd.gauss(0, vol)
        out.append({"t": iso(start + timedelta(days=i * 1.45)), "v": round(v, 2)})
    return out


metrics_src = "SAMPLE · no trades yet"
setups = [
    dict(id="orb", name="ORB · SPY and TQQQ", short="ORB", desk=0, stage="paper", symbols=["SPY", "TQQQ"], status="working",
         action="SAMPLE · Watching the opening range for a breakout", progress=None,
         metrics=dict(trades=34, win_rate=.53, expectancy_r=.18, pf=1.31, max_dd=6.2, sharpe=1.1),
         equity=equity(3, .28, .7), tradeable=dict(live_equity=1000, ok=True, why="1 SPY share fits a $50 risk cap with a stop under $50 away")),
    dict(id="cvd", name="CVD turn · 3-min", short="CVD", desk=1, stage="backtest", symbols=["SPY"], status="waiting",
         action="SAMPLE · Waiting on the Lab's backtest", progress=None,
         metrics=dict(trades=0), equity=[], tradeable=dict(live_equity=1000, ok=True, why="Same sizing as ORB on SPY")),
    dict(id="gex", name="GEX verticals · SPY/SPX", short="GEX", desk=2, stage="idea", symbols=["SPY", "SPX"], status="error",
         action="SAMPLE · Blocked: no GEX data source connected", progress=None,
         metrics=dict(trades=0), equity=[], tradeable=dict(live_equity=1000, ok=False, why="A $1-wide SPY spread can lose about $60-100; the cap at $1,000 is $50")),
    dict(id="ctl-spy", name="SPY buy and hold", short="SPY hold", desk=3, stage="paper", symbols=["SPY"], status="asleep",
         action="SAMPLE · Holding; nothing to do until rebalance", progress=None,
         metrics=dict(trades=1, win_rate=None, expectancy_r=None, pf=None, max_dd=3.4, sharpe=1.4),
         equity=equity(5, .22, .45), tradeable=dict(live_equity=1000, ok=True, why="1 share of SPY fits")),
    dict(id="ctl-ema", name="EMA 9/21 cross", short="EMA", desk=4, stage="paper", symbols=["SPY"], status="working",
         action="SAMPLE · Checking the 9/21 cross on the 5-minute chart", progress=None,
         metrics=dict(trades=22, win_rate=.41, expectancy_r=-.04, pf=.94, max_dd=7.8, sharpe=-.2),
         equity=equity(9, -.05, .6), tradeable=dict(live_equity=1000, ok=True, why="1 SPY share fits")),
]
for s in setups:
    s.update(kind="setup", icon="chart", district="trading", sample=True, action_at=ago(minutes=8),
             real_note="Real stage today: Spec (GEX: Idea). No trades yet; these numbers are examples.",
             links=[{"label": "spec.md", "url": GH + f"strategies/{dict(orb='orb', cvd='cvd_turn', gex='gex_spreads').get(s['id'], 'controls')}/spec.md"}],
             history=hist((8, s["action"].replace("SAMPLE · ", "")), (60, "Logged a heartbeat")), queue=[])
    s["metrics"].update(sample=True, as_of=ago(minutes=8), source=metrics_src)

HUSTLES = [
    ("h-templates", "Trader spreadsheet templates", "Templates", 0, "templates",
     "Google Sheets trade journal plus options risk and position-size calculator, sold for $12 on Gumroad (no monthly fee; about $9.65 kept per sale). Claude builds and maintains it; you create the account, connect payout and approve listings.",
     "$0 to $150 (low confidence)", "High once set up", "About 2 hours setup, then 30 min a week"),
    ("h-pine", "Pine Script commissions", "Pine work", 1, "pine",
     "Custom TradingView indicators coded to a buyer's rules on Fiverr (Fiverr keeps 20%). Claude writes and tests the code and drafts replies; you own the account, message clients and check deliveries.",
     "$0 to $300 (low to medium confidence)", "Medium", "3 to 5 hours a week while orders are active"),
    ("h-discord", "Discord bots for trading servers", "Discord bots", 2, "discord",
     "Alert-relay and recap bots for small trading Discords, around $150 a setup plus optional monthly upkeep. Claude builds the bots; you handle clients and permissions.",
     "$0 to $450 (low confidence)", "Medium", "3 to 4 hours a week per active client"),
    ("h-buildlog", "Build-in-public posts", "Build log", 3, "buildlog",
     "Posts every two weeks on LinkedIn about building Compound City, with honest results. Little direct money, strong resume value, and an audience for the other hustles. Claude drafts; you approve and post.",
     "$0 to $25 direct (high confidence it stays small)", "High for drafting", "About 1 hour a week"),
]
hustles = []
for hid, name, short, stall, folder, summary, rng90, auto, hrs in HUSTLES:
    hustles.append(dict(id=hid, name=name, short=short, stall=stall, stage="proposed", status="needs_me",
                        action="Waiting for your yes or no at City Hall", revenue=0, costs=0, hours=0,
                        one_pager=summary, range_90d=rng90, autonomy=auto, your_hours=hrs))
for h in hustles:
    folder = dict((x[0], x[4]) for x in HUSTLES)[h["id"]]
    h.update(kind="hustle", icon="mega", district="hustles", sample=False, action_at="2026-10-13T22:40:00Z",
             money_as_of="2026-10-13T22:40:00Z", source="ledger/money.csv (no rows yet)",
             history=[{"t": "2026-10-13T22:40:00Z", "text": "Proposed at City Hall"}], queue=["Your yes or no"],
             links=[{"label": "one-pager", "url": GH + f"hustles/{folder}/one-pager.md"}])

for a in residents + setups + hustles:
    write("agents__" + a["id"], a)

# ---------------- City Hall ----------------
hall = [
    dict(id="t-webhook", title="Add ALERT_WEBHOOK_URL in Railway (optional)", kind="task", status="pending", sample=False,
         from_label="Claude", created_at="2026-10-13T21:20:00Z",
         detail="A Discord channel webhook so the bot can ping your phone about problems and, later, Robinhood trade tickets. Railway > compound-city > bot > Variables."),
    dict(id="t-alphav", title="Connect the Alpha Vantage connector", kind="task", status="pending", sample=False,
         from_label="Claude", created_at="2026-10-13T21:19:00Z",
         detail="Free key from alphavantage.co, then claude.ai > Settings > Connectors. The Newsie uses it for prices and news."),
]
for n, (hid, name, short, stall, folder, summary, rng90, auto, hrs) in enumerate(HUSTLES):
    hall.append(dict(id="d-" + folder, title=f"Start: {name}?", kind="decision", status="pending",
                     sample=False, from_label="Hustle Scout", created_at=f"2026-10-13T22:4{n}:00Z",
                     detail=f"{summary} Realistic first 90 days: {rng90}. Your time: {hrs}.",
                     link=GH + f"hustles/{folder}/one-pager.md"))
hall.append(dict(id="d-routing", title="Should hustle income top up the $50 operations fund first?", kind="decision",
                 status="pending", sample=False, from_label="Claude", created_at="2026-10-13T22:45:00Z",
                 detail="Claude Pro costs $20 a month, so the $50 lasts about 2.5 months. Yes: hustle income keeps one month of running costs in reserve, and everything above that goes to the live fund. No: all hustle income goes straight to the live fund, and you'd top up running costs yourself."))
for h in hall:
    write("cityhall__" + h["id"], h)

# ---------------- ledger/trades (sample) ----------------
rnd = random.Random(42)
rows = []
for i in range(12):
    t = NOW - timedelta(hours=3 + i * 5)
    setup = ["ORB · SPY and TQQQ", "EMA 9/21 cross"][i % 2]
    px = round(774 + rnd.uniform(-6, 6), 2)
    rows.append(dict(t=iso(t), setup=setup, symbol="SPY", side=["buy", "sell"][i % 2], qty=1, price=px,
                     shadow_price=round(px + rnd.uniform(-.4, .4), 2), pnl_r=round(rnd.uniform(-1, 1.6), 2),
                     ref=f"trades.csv row {40 - i}"))
write("ledger__trades", dict(sample=True, as_of=iso(NOW), source="SAMPLE · ledger/trades.csv", rows=rows))
print("wrote", len(list(OUT.glob("*.json"))), "files")
