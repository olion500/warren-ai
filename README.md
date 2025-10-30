# Warren AI

**Buffett-style AI Investment Framework with 5-Agent Core Architecture**

Warren AI is a multi-agent system for fundamental stock analysis, implementing Warren Buffett's investment principles with a mandatory Devil's Advocate agent that challenges every investment thesis.

## 🎯 Core Philosophy

- **Conservative by design**: Margin of safety over speculation
- **Quality first**: Strong competitive moats required (60+ score)
- **Cash flow focus**: Owner's Earnings (CFO - Maintenance CapEx)
- **Contrarian oversight**: Devil's Advocate mandatory for all decisions
- **Explainable AI**: Complete audit trail in investment memos

## 🧠 5-Agent Architecture

```
DQA → VA → DA → PA → MAA
```

### Agent 1: Data Quality Agent (DQA)
Validates financials and computes quality metrics:
- ROIC, ROE, margin stability
- Competitive moat score (0-100)
- Earnings quality checks (Beneish M-score, CFO/NI)

### Agent 2: Valuation Agent (VA)
Calculates intrinsic value:
- Owner's Earnings = CFO - Maintenance CapEx
- 3-scenario DCF (bear/base/bull)
- Margin of Safety calculation

### Agent 3: Devil's Advocate Agent (DA) 😈
**Core differentiator** - mandatory contrarian review:
- Auto-veto on fatal flaws (earnings manipulation, excessive debt)
- Generate counter-arguments
- Stress test assumptions (margin compression, growth slowdown)
- Require conservative adjustments

### Agent 4: Portfolio Agent (PA)
Makes buy/watch/reject decisions:
- Apply quality + valuation + DA filters
- Position sizing: f(MOS, moat_score, DA_concerns)
- Enforce diversification constraints

### Agent 5: Memo & Audit Agent (MAA)
Creates transparent investment memos:
- Bull case vs Bear case
- Key assumptions and sensitivities
- Complete reasoning chain for audit

## 🚀 Quick Start

### Installation
```bash
make install
```

### Run Analysis
```bash
make analyze TICKER=AAPL
```

This runs the full 5-agent pipeline and generates an investment memo in `output/AAPL_memo.md`.

## 📊 Decision Criteria

### BUY Triggers
- Margin of Safety ≥ 50%
- Moat Score ≥ 60
- No Devil's Advocate veto
- ROIC ≥ 12%, ROE ≥ 15%

### WATCH List
- MOS 30-50% (wait for better price)
- Moat Score 40-60 (marginal advantage)
- DA issued "REDUCE" recommendation

### REJECT
- DA veto (fatal flaws)
- MOS < 30%
- Moat Score < 40
- Earnings manipulation risk (Beneish M > -2.2)

## 🛠️ Development

```bash
make test       # Run pytest suite
make lint       # Run ruff + mypy
make format     # Black + isort
```

## 📁 Project Structure

```
warren_core/
├── orchestrator.py          # Pipeline coordinator
├── agents/
│   ├── data_quality.py      # DQA
│   ├── valuation.py         # VA
│   ├── devils_advocate.py   # DA (core)
│   ├── portfolio.py         # PA
│   └── memo_audit.py        # MAA
└── configs/
    ├── thresholds.yml       # Investment criteria
    └── veto_rules.yml       # DA veto triggers
```

## 📈 Example Output

Investment memos include:
- Business summary with moat analysis
- Quality metrics (ROIC, ROE, moat score)
- Valuation range with MOS
- Bull case (from DQA/VA)
- Bear case (from Devil's Advocate)
- Decision rationale with assumptions
- Monitoring triggers

## ⚠️ Current Status

**Skeleton architecture complete** - agents not yet fully implemented.

Priority implementation order:
1. DQA: Basic profitability calculations
2. VA: Owner's Earnings and simple DCF
3. DA: Veto rules and stress tests (critical)
4. PA: Decision tree and sizing
5. MAA: Memo generation

## 🧩 Key Differentiators

1. **Devil's Advocate as first-class citizen**: Not a post-hoc check, but a mandatory pipeline stage with veto power
2. **Conservative by default**: All assumptions require DA approval
3. **Explainable decisions**: Complete audit trail from data → decision
4. **Quality over timing**: Will reject overpriced quality (wait-then-pounce)
5. **Cash flow truth**: Owner's Earnings, not GAAP net income

## 📚 Philosophy References

Based on Warren Buffett's principles:
- Focus on economic moats (competitive advantages)
- Margin of safety (Benjamin Graham)
- Owner's Earnings > Reported Earnings
- "Wait for the fat pitch" (patience discipline)
- Price is what you pay, value is what you get

## 🔮 Roadmap (TODO)

- [ ] Implement core DQA metrics
- [ ] Build DCF valuation engine
- [ ] Complete DA veto logic and stress tests
- [ ] Add data connectors (Yahoo Finance, SEC EDGAR)
- [ ] Historical backtester with DA effectiveness metrics
- [ ] WebUI dashboard for memo review
- [ ] Macro context sentinel (sector/regulatory risks)

## 📄 License

MIT License - See LICENSE file

---

**🧮 Generated with discipline. Buffett would approve (maybe).**
