# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ IMPORTANT: Check TASKS.md First

**Before starting any work**, always read `TASKS.md` to see:
- ✅ What's already been completed (don't redo!)
- 🚧 What's currently in progress
- ⏳ What needs to be done next
- 📊 Current test coverage and commit status

The task list is kept up-to-date with implementation status, test results, and git commit references.

## Project Overview

**Warren AI** is a Buffett-style investment analysis framework built on a 5-agent architecture. It analyzes stocks through multiple lenses with a mandatory Devil's Advocate agent that challenges every investment thesis.

### Core Philosophy

- **Conservative by design**: Prioritize margin of safety over growth speculation
- **Contrarian oversight**: Devil's Advocate agent mandatory for all decisions
- **Quality over price**: Strong competitive moats required
- **Cash flow focus**: Owner's Earnings (Buffett's preferred metric) drives valuation
- **Explainable decisions**: Complete audit trail in investment memos

## Commands

### Development
```bash
make install      # Install dependencies
make test         # Run pytest suite
make lint         # Run ruff and mypy
make format       # Format with black and isort
```

### Analysis
```bash
make analyze TICKER=AAPL    # Analyze a stock (full 5-agent pipeline)
```

### Manual Execution
```bash
python -m warren_core.orchestrator --ticker AAPL
```

## Architecture

### 5-Agent Pipeline

The analysis flows through 5 specialized agents in strict order:

```
DQA → VA → DA → PA → MAA
```

#### 1. **Data Quality Agent (DQA)**
- **File**: `warren_core/agents/data_quality.py`
- **Input**: Raw financial data, 10-K/10-Q filings
- **Output**: ROIC, ROE, margin stability, moat score, data warnings
- **Key Methods**:
  - `analyze()`: Main entry point
  - `_calculate_roic()`: Return on Invested Capital
  - `_calculate_roe()`: Return on Equity
  - `_compute_moat_score()`: Competitive advantage scoring (0-100)
  - `_check_data_integrity()`: Flag restatements, missing data

#### 2. **Valuation Agent (VA)**
- **File**: `warren_core/agents/valuation.py`
- **Input**: DQA output, current price
- **Output**: Owner's Earnings, intrinsic value (bear/base/bull), margin of safety
- **Key Methods**:
  - `_calculate_owner_earnings()`: CFO - Maintenance CapEx
  - `_run_dcf()`: 3-scenario DCF model
  - `_calculate_mos()`: (Intrinsic Value - Price) / Intrinsic Value
  - `_sensitivity_analysis()`: Test assumption variations

#### 3. **Devil's Advocate Agent (DA)** ⚠️ **Core Differentiator**
- **File**: `warren_core/agents/devils_advocate.py`
- **Input**: DQA + VA outputs
- **Output**: Veto decision, counter-arguments, stress test results, adjustments
- **Key Methods**:
  - `_check_veto_rules()`: Auto-reject on fatal flaws (see `veto_rules.yml`)
  - `_generate_counterarguments()`: Specific bear case arguments
  - `_run_stress_tests()`: Margin/growth/capex/multiple stress scenarios
  - `_suggest_adjustments()`: Conservative parameter corrections
  - `_make_recommendation()`: REJECT / REDUCE / PROCEED

**Veto triggers** (see `warren_core/configs/veto_rules.yml`):
- Beneish M-score > -2.2 (earnings manipulation risk)
- CFO/NI < 0.5 (poor cash conversion)
- Net Debt/EBITDA > 4.0 (excessive leverage)
- Moat score < 40 (no competitive advantage)
- MOS < 10% (insufficient safety margin)

#### 4. **Portfolio Agent (PA)**
- **File**: `warren_core/agents/portfolio.py`
- **Input**: DQA + VA + DA outputs, current portfolio
- **Output**: BUY / WATCH / REJECT decision, position sizing, triggers
- **Key Methods**:
  - `_apply_decision_rules()`: Decision tree logic
  - `_calculate_position_size()`: f(MOS, moat_score, DA_concerns)
  - `_check_portfolio_constraints()`: Enforce diversification limits
  - `_set_monitoring_triggers()`: Price/fundamental alerts

**Decision logic**:
```python
if DA.veto or DQA.data_warning == "A":
    decision = "REJECT"
elif VA.mos < mos_threshold or DQA.moat_score < 60:
    decision = "WATCH"
else:
    decision = "BUY"
```

#### 5. **Memo & Audit Agent (MAA)**
- **File**: `warren_core/agents/memo_audit.py`
- **Input**: All agent outputs
- **Output**: Investment memo (markdown), audit trail
- **Key Methods**:
  - `create_memo()`: Compile complete analysis
  - `_extract_bull_case()`: Positive thesis from DQA/VA
  - `_extract_bear_case()`: Counter-arguments from DA
  - `to_markdown()`: Generate readable report

### Configuration Files

#### `warren_core/configs/thresholds.yml`
Defines investment criteria:
- **Quality**: ROIC ≥ 12%, ROE ≥ 15%, moat_score ≥ 60
- **Valuation**: MOS ≥ 30-50% (buy threshold)
- **Leverage**: Net Debt/EBITDA < 2.5×, Interest Coverage > 5×
- **Portfolio**: Max position 25%, max sector 40%, min cash 10%

#### `warren_core/configs/veto_rules.yml`
Devil's Advocate veto triggers and stress test scenarios:
- **A-level** (auto-reject): Earnings manipulation, excessive debt, no moat
- **B-level** (reduce size): Dilution, inconsistent profitability
- **Stress tests**: Margin compression, growth slowdown, capex surge

### Orchestrator

**File**: `warren_core/orchestrator.py`

Coordinates agent pipeline. Key flow:
1. Load configurations
2. Initialize all 5 agents
3. Run `DQA → VA → DA → PA → MAA` in sequence
4. Generate markdown memo in `output/{ticker}_memo.md`

## Code Structure

```
warren-ai/
├── warren_core/
│   ├── __init__.py
│   ├── orchestrator.py          # Main pipeline coordinator
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── data_quality.py      # Agent 1: DQA
│   │   ├── valuation.py         # Agent 2: VA
│   │   ├── devils_advocate.py   # Agent 3: DA (core differentiator)
│   │   ├── portfolio.py         # Agent 4: PA
│   │   └── memo_audit.py        # Agent 5: MAA
│   └── configs/
│       ├── thresholds.yml       # Investment criteria
│       └── veto_rules.yml       # DA veto triggers
├── tests/
├── output/                      # Generated memos
├── pyproject.toml
├── Makefile
└── README.md
```

## Key Metrics

### Quality Metrics (DQA)
- **ROIC** = NOPAT / Invested Capital
- **ROE** = Net Income / Shareholders' Equity
- **Moat Score** (0-100): Composite of pricing power, ROIC persistence, market share
- **Beneish M-score**: Earnings quality (> -2.2 = red flag)
- **CFO/NI ratio**: Cash conversion quality (< 0.8 = warning)

### Valuation Metrics (VA)
- **Owner's Earnings** = Operating Cash Flow - Maintenance CapEx
- **Intrinsic Value**: 3-scenario DCF (bear/base/bull)
- **Margin of Safety** = (Intrinsic - Price) / Intrinsic

### Decision Thresholds
- **BUY**: MOS ≥ 50%, Moat ≥ 60, no DA veto
- **WATCH**: MOS 30-50% OR Moat 40-60
- **REJECT**: MOS < 30% OR Moat < 40 OR DA veto

## Implementation Status

**Last Updated**: 2025-10-31 | **Total Commits**: 5

### ✅ Agent 1: Data Quality Agent (DQA) - COMPLETE
- ✅ ROIC calculation (commit: `92dd8ee`)
- ✅ ROE calculation (commit: `92dd8ee`)
- ✅ Moat score algorithm (commit: `3a2caa5`)
- ✅ Data integrity checks (commit: `858ebdb`)
- ✅ Full analyze() pipeline (commit: `858ebdb`)
- **Status**: Production-ready | 95% coverage | 17 tests passing

### 🟡 Agent 2: Valuation Agent (VA) - PARTIAL
- ✅ Owner's Earnings calculation (commit: `86b4f18`)
- ✅ Margin of Safety (MOS) calculation (commit: `86b4f18`)
- ⏳ DCF valuation (3 scenarios) - **IN PROGRESS**
- ⏳ Sensitivity analysis
- **Status**: Core metrics done | 9 tests passing | DCF needed

### ⏳ Agent 3: Devil's Advocate (DA) - NOT STARTED
- ⏳ Veto rule checks - **HIGH PRIORITY**
- ⏳ Counter-argument generation
- ⏳ Stress tests
- **Status**: Critical path blocker

### ⏳ Agent 4: Portfolio Agent (PA) - NOT STARTED
- ⏳ Decision rules (BUY/WATCH/REJECT)
- ⏳ Position sizing

### ⏳ Agent 5: Memo & Audit Agent (MAA) - NOT STARTED
- ⏳ Memo generation

**See TASKS.md for detailed task breakdown and next steps.**

## Development Notes

### When implementing agents:
- Return proper dataclass outputs (e.g., `DataQualityOutput`, `ValuationOutput`)
- Use config values from `self.config` for thresholds
- Handle missing data gracefully (DQA should flag, not fail)
- DA must always run - no bypassing even if costly

### When modifying configs:
- All thresholds in `thresholds.yml` should be conservative
- New veto rules in `veto_rules.yml` require severity level (A/B/C)
- Test DA behavior with new rules before deploying

### Testing philosophy:
- Unit test each agent independently with mock inputs
- Integration tests should verify full pipeline with sample data
- Test DA veto triggers explicitly (critical path)

### Data sources (future):
- Financial statements: Yahoo Finance API, SEC EDGAR, or similar
- Current prices: Real-time quote services
- For now: Accept dict inputs to decouple from data provider
