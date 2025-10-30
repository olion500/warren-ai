# Warren AI - Implementation Tasks

**Last Updated**: 2025-10-31 (Session 2 Complete)

## 📊 Progress Overview

- **Agent 1 (DQA)**: ✅ Complete (95% coverage, 17 tests)
- **Agent 2 (VA)**: 🟡 Partial (Owner's Earnings + MOS done, DCF pending)
- **Agent 3 (DA)**: ✅ Complete (86% coverage, 18 tests) 🔥 **CORE FEATURE DONE!**
- **Agent 4 (PA)**: ⏳ Not Started
- **Agent 5 (MAA)**: ⏳ Not Started

**Total Commits**: 9 (all tested and passing)

**Session 2 Achievement**: Devil's Advocate Agent fully implemented - the core differentiator of Warren AI!

---

## ✅ Completed Tasks

### Agent 1: Data Quality Agent (DQA)
- [x] **ROIC calculation** - Return on Invested Capital (NOPAT / Invested Capital)
  - Commit: `92dd8ee` - 3 tests passing
- [x] **ROE calculation** - Return on Equity (NI / Avg Shareholders' Equity)
  - Commit: `92dd8ee` - 3 tests passing
- [x] **Moat score algorithm** - Competitive advantage scoring (0-100)
  - Pricing power (gross margin) - 35 points
  - ROIC persistence - 35 points
  - Revenue growth stability - 30 points
  - Commit: `3a2caa5` - 4 tests passing
- [x] **Data integrity checks** - Earnings quality warnings
  - Beneish M-score (earnings manipulation risk)
  - CFO/NI ratio (cash conversion quality)
  - Missing critical fields detection
  - Negative equity detection
  - Commit: `858ebdb` - 5 tests passing
- [x] **Complete analyze() method** - Full DQA pipeline integration
  - Commit: `858ebdb` - 2 integration tests

**DQA Status**: ✅ Production-ready (95% coverage, 17 tests)

### Agent 2: Valuation Agent (VA) - Partial
- [x] **Owner's Earnings calculation** - CFO - Maintenance CapEx
  - Smart capex estimation with 3-tier fallback
  - Commit: `86b4f18` - 5 tests passing
- [x] **Margin of Safety (MOS)** - (Intrinsic Value - Price) / Intrinsic Value
  - Handles overvalued stocks (negative MOS)
  - Commit: `86b4f18` - 4 tests passing

**VA Status**: 🟡 Core metrics done, DCF pending (9 tests)

### Agent 3: Devil's Advocate (DA) - COMPLETE! 🔥
- [x] **Veto rule checks** - Automatic rejection logic
  - Safe condition parser (no eval for security)
  - Supports all critical metrics (Beneish M, CFO/NI, moat, MOS, owner earnings)
  - Config-driven veto triggers
  - Commit: `fc4480e` - 7 tests passing
- [x] **Counter-argument generation** - Systematic bear case
  - 6 categories: profitability, moat, valuation, cash quality, stability, data quality
  - Severity-based classification (A/B/C)
  - Evidence-backed claims with quantitative data
  - Impact assessment for each concern
  - Commit: `75c3d7a` - 6 tests passing
- [x] **analyze() method integration** - Full pipeline
  - Combines veto rules + counter-arguments
  - Recommendation decision logic (REJECT/REDUCE/PROCEED)
  - Conservative bias (single A-level → REDUCE)
  - Complete DevilsAdvocateOutput
  - Commit: `3277864` - 5 integration tests passing

**DA Status**: ✅ Production-ready! (86% coverage, 18 tests)

**Key Achievement**: Warren AI's core differentiator is complete. Mandatory contrarian oversight now operational.

---

## 🚧 In Progress / Next Steps

**Current Status**: Core agents (DQA, VA partial, DA) complete. Next priority is connecting the pipeline with PA.

### Priority 1: Portfolio Agent (PA) - Connect the Pipeline! 🎯

**Rationale**: With DQA + VA + DA complete, implementing PA will create a working end-to-end pipeline from data → decision. This is more valuable than completing VA's DCF at this stage.

#### 1.1 Decision Rules (BUY/WATCH/REJECT) ⏳
**Priority**: CRITICAL
**Estimated Complexity**: Low

Implement decision tree that consumes DQA + VA + DA outputs:
```python
if DA.veto or DA.recommendation == "REJECT":
    return "REJECT"
elif DA.recommendation == "REDUCE":
    return "WATCH"
elif VA.mos < 0.30 or DQA.moat_score < 60:
    return "WATCH"
else:
    return "BUY"
```

Test cases needed:
- [ ] Clean company → BUY
- [ ] DA veto → REJECT
- [ ] DA REDUCE → WATCH
- [ ] Low MOS → WATCH
- [ ] Weak moat → WATCH
- [ ] Multiple decision factors

**Files to modify**:
- `warren_core/agents/portfolio.py::_apply_decision_rules()`
- `tests/test_portfolio.py::TestDecisionRules`

---

#### 1.2 Position Sizing ⏳
**Priority**: HIGH
**Estimated Complexity**: Medium

Calculate position size based on conviction:
```python
if decision == "BUY":
    base_size = f(MOS, moat_score)
    adjusted_size = base_size * da_penalty
    final_size = min(adjusted_size, max_position_cap)
```

**Files to modify**:
- `warren_core/agents/portfolio.py::_calculate_position_size()`
- `warren_core/agents/portfolio.py::analyze()` (integration)
- `tests/test_portfolio.py::TestPositionSizing`

---

#### 1.3 Complete PA analyze() Method ⏳
**Priority**: HIGH

Integrate decision rules + position sizing into main pipeline.

---

### Priority 2: Complete Valuation Agent (VA)

#### 1.1 DCF Valuation (3 Scenarios) ⏳
**Priority**: HIGH
**Estimated Complexity**: Medium-High
**Dependencies**: Owner's Earnings (done)

Implementation requirements:
- **Bear case**: Conservative growth (50% of base), higher discount rate (+2%)
- **Base case**: Config default growth (5%), base discount rate (10%)
- **Bull case**: Optimistic growth (150% of base), lower discount rate (-1%)

DCF steps:
1. Project free cash flows (5-10 years)
2. Calculate terminal value (perpetuity growth or exit multiple)
3. Discount to present value
4. Sum DCF + terminal value

Test cases needed:
- [ ] Basic 3-scenario DCF calculation
- [ ] Terminal value calculation (perpetuity method)
- [ ] Discount rate sensitivity
- [ ] Negative growth handling

**Files to modify**:
- `warren_core/agents/valuation.py::_run_dcf()`
- `tests/test_valuation.py::TestDCFValuation`

---

#### 1.2 Sensitivity Analysis ⏳
**Priority**: MEDIUM
**Estimated Complexity**: Low

Test impact of varying assumptions:
- Growth rate ±2%
- Discount rate ±1%
- Terminal multiple ±2x
- Operating margin ±5%

Return sensitivity matrix for decision-making.

**Files to modify**:
- `warren_core/agents/valuation.py::_sensitivity_analysis()`
- `tests/test_valuation.py::TestSensitivityAnalysis`

---

#### 1.3 Complete VA analyze() Method ⏳
**Priority**: HIGH
**Dependencies**: DCF, sensitivity analysis

Integrate all VA components into main pipeline.

---

### Priority 2: Devil's Advocate Agent (DA) 😈 **CRITICAL**

#### 2.1 Veto Rule Checks ⏳
**Priority**: CRITICAL
**Estimated Complexity**: Medium

Implement auto-reject logic from `veto_rules.yml`:
- [x] Config loaded (done in orchestrator)
- [ ] Check each veto rule against DQA + VA outputs
- [ ] Return (veto: bool, reason: str)

A-level triggers (auto-reject):
- Beneish M-score > -2.2 (earnings manipulation)
- CFO/NI < 0.5 (poor cash conversion)
- Net Debt/EBITDA > 4.0 (excessive leverage)
- Moat score < 40 (no competitive advantage)
- MOS < 10% (insufficient safety margin)

**Files to modify**:
- `warren_core/agents/devils_advocate.py::_check_veto_rules()`
- `tests/test_devils_advocate.py::TestVetoRules`

---

#### 2.2 Counter-Argument Generation ⏳
**Priority**: HIGH
**Estimated Complexity**: Medium-High

Generate specific bear case arguments across categories:
- Business model vulnerabilities
- Competitive threats
- Cyclicality / macro sensitivity
- Management concerns
- Valuation optimism
- Hidden liabilities / off-balance-sheet risks

Each argument needs:
- Severity (A/B/C)
- Category
- Claim (what's wrong)
- Evidence (from data)
- Impact (on investment thesis)

**Files to modify**:
- `warren_core/agents/devils_advocate.py::_generate_counterarguments()`
- `tests/test_devils_advocate.py::TestCounterArguments`

---

#### 2.3 Stress Tests ⏳
**Priority**: HIGH
**Estimated Complexity**: Medium

Re-run DCF under stressed scenarios:
- Margin compression: operating margin × 0.70 (30% decline)
- Growth slowdown: growth rate × 0.50 (50% reduction)
- CapEx surge: maintenance capex × 1.50 (50% increase)
- Multiple contraction: exit multiple × 0.80 (20% lower)
- **Combined worst case**: All above simultaneously

Return:
- Stressed intrinsic values
- Stressed MOS
- Pass/fail for each scenario

**Files to modify**:
- `warren_core/agents/devils_advocate.py::_run_stress_tests()`
- `tests/test_devils_advocate.py::TestStressTests`

---

#### 2.4 Adjustment Recommendations ⏳
**Priority**: MEDIUM
**Estimated Complexity**: Low

Suggest conservative parameter adjustments based on findings:
- Increase maintenance capex estimate
- Reduce growth assumptions
- Increase discount rate
- Add risk premium

**Files to modify**:
- `warren_core/agents/devils_advocate.py::_suggest_adjustments()`

---

#### 2.5 Final Recommendation Logic ⏳
**Priority**: HIGH
**Estimated Complexity**: Low

Decision logic:
- **REJECT**: Veto OR ≥2 A-level concerns
- **REDUCE**: ≥3 B-level concerns OR stress tests fail
- **PROCEED**: Concerns are manageable

**Files to modify**:
- `warren_core/agents/devils_advocate.py::_make_recommendation()`
- `tests/test_devils_advocate.py::TestRecommendations`

---

### Priority 3: Portfolio Agent (PA)

#### 3.1 Decision Rules (BUY/WATCH/REJECT) ⏳
**Priority**: HIGH
**Estimated Complexity**: Low

Decision tree:
```python
if DA.veto or DQA.data_warning == "A":
    return "REJECT"
elif VA.mos < mos_threshold or DQA.moat_score < 60:
    return "WATCH"
elif DA.recommendation == "REDUCE":
    return "WATCH"  # or reduced BUY
else:
    return "BUY"
```

**Files to modify**:
- `warren_core/agents/portfolio.py::_apply_decision_rules()`
- `tests/test_portfolio.py::TestDecisionRules`

---

#### 3.2 Position Sizing ⏳
**Priority**: HIGH
**Estimated Complexity**: Medium

Calculate position size based on conviction:
- Base size from MOS (higher = larger)
- Adjust for moat score (stronger moat = larger)
- DA penalty (more concerns = smaller)
- Apply constraints:
  - Max position: 25%
  - Max sector: 40%
  - Min cash reserve: 10%

Formula:
```python
base_size = f(MOS, moat_score)
adjusted_size = base_size * da_adjustment
final_size = min(adjusted_size, constraints)
```

**Files to modify**:
- `warren_core/agents/portfolio.py::_calculate_position_size()`
- `warren_core/agents/portfolio.py::_check_portfolio_constraints()`
- `tests/test_portfolio.py::TestPositionSizing`

---

#### 3.3 Monitoring Triggers ⏳
**Priority**: MEDIUM
**Estimated Complexity**: Low

Set alerts:
- Buy more price (lower MOS band)
- Sell price (thesis invalidation)
- Quarterly review flags
- Watch metrics (fundamentals to track)

**Files to modify**:
- `warren_core/agents/portfolio.py::_set_monitoring_triggers()`

---

### Priority 4: Memo & Audit Agent (MAA)

#### 4.1 Memo Generation ⏳
**Priority**: MEDIUM
**Estimated Complexity**: Medium

Create comprehensive investment memo:

Sections:
- 📘 Business summary with moat evidence
- 📊 Quality metrics (ROIC, ROE, moat score)
- 💰 Valuation (Owner's Earnings, intrinsic value range, MOS)
- ✅ Bull case (from DQA/VA positive findings)
- 😈 Bear case (from DA counter-arguments)
- 🎯 Decision rationale
- 🔑 Key assumptions (with DA adjustments)
- ⚠️ Key risks (A/B-level concerns)
- 📈 Monitoring triggers

Output: Markdown file in `output/{ticker}_memo.md`

**Files to modify**:
- `warren_core/agents/memo_audit.py::create_memo()`
- `warren_core/agents/memo_audit.py::to_markdown()`
- `tests/test_memo_audit.py::TestMemoGeneration`

---

## 🎯 Recommended Implementation Order

1. ✅ **DQA complete** (done - 17 tests)
2. ✅ **VA Owner's Earnings + MOS** (done - 9 tests)
3. ✅ **DA veto rules** (done - 7 tests)
4. ✅ **DA counter-arguments** (done - 6 tests)
5. ✅ **DA analyze() integration** (done - 5 tests)
6. ⏳ **PA decision rules** ← **START HERE NEXT SESSION**
7. ⏳ **PA position sizing**
8. ⏳ **PA analyze() integration**
9. ⏳ **MAA memo generation**
10. ⏳ **VA DCF valuation** (optional - can skip for MVP)
11. ⏳ **DA stress tests** (optional enhancement)
12. ⏳ **Integration testing** (full pipeline DQA→VA→DA→PA→MAA)

---

## 📈 Testing Strategy

Each feature must have:
- [ ] Unit tests for core logic
- [ ] Edge case tests (zero, negative, missing data)
- [ ] Integration tests (agent outputs → next agent)
- [ ] Full pipeline test (sample stock → memo)

Coverage target: **≥80%** per agent, **≥90%** for DA

---

## 🚀 Future Enhancements (Post-MVP)

- [ ] Data connectors (Yahoo Finance, SEC EDGAR API)
- [ ] Historical backtester (test DA effectiveness on past data)
- [ ] WebUI dashboard for memo review
- [ ] Macro context sentinel (sector/regulatory risk tagging)
- [ ] Portfolio rebalancing logic
- [ ] Real-time monitoring integration

---

## 📝 Notes

- **Devil's Advocate (DA) is the core differentiator** - implement carefully
- All assumptions must be conservative by default
- DA must always run - no bypassing even if costly
- Every decision must have clear audit trail
- MOS thresholds are configurable in `thresholds.yml`
- Veto rules are configurable in `veto_rules.yml`

---

## 📝 Session Notes

### Session 1 (Initial Setup)
- Created project structure
- Implemented DQA (17 tests)
- Implemented VA partial (9 tests)
- Set up TASKS.md and CLAUDE.md

### Session 2 (Devil's Advocate) ✅
- **Implemented DA veto rules** (7 tests) - Core auto-reject logic
- **Implemented DA counter-arguments** (6 tests) - Systematic bear case generation
- **Integrated DA analyze()** (5 tests) - Full pipeline with recommendation logic
- **Total**: 18 DA tests passing, 86% coverage
- **Achievement**: Core differentiator of Warren AI complete!

**Next session**: Start with PA decision rules to connect the pipeline. With DQA→VA→DA complete, implementing PA creates a working end-to-end system.
