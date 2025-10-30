"""
Memo & Audit Agent (MAA)
Creates investment memos and logs decision reasoning
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class InvestmentMemo:
    """Complete investment memo"""
    ticker: str
    analysis_date: str
    decision: str
    position_size: float

    # Business summary
    business_description: str
    competitive_moat: str

    # Financial metrics
    quality_metrics: Dict[str, Any]
    valuation_summary: Dict[str, Any]

    # Bull vs Bear
    bull_case: List[str]
    bear_case: List[str]  # From Devil's Advocate

    # Decision rationale
    reasoning: str
    key_assumptions: Dict[str, Any]
    risks: List[str]
    monitoring_triggers: Dict[str, Any]

    # Audit trail
    agent_outputs: Dict[str, Any]


class MemoAuditAgent:
    """
    Agent 5: Memo & Audit Trail

    Responsibilities:
    - Compile all agent outputs into coherent memo
    - Create transparent reasoning chain
    - Document bull case vs bear case
    - List key assumptions and sensitivities
    - Provide audit trail for review
    - Generate human-readable report
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def create_memo(
        self,
        ticker: str,
        dqa_output: Any,
        va_output: Any,
        da_output: Any,
        pa_output: Any,
        business_context: Dict[str, Any] | None = None
    ) -> InvestmentMemo:
        """
        Create comprehensive investment memo

        Args:
            ticker: Stock symbol
            dqa_output: Data Quality Agent results
            va_output: Valuation Agent results
            da_output: Devil's Advocate results
            pa_output: Portfolio Agent decision
            business_context: Optional business description

        Returns:
            InvestmentMemo with complete analysis
        """
        # TODO: Compile agent outputs
        # TODO: Generate memo sections
        # TODO: Create audit trail

        raise NotImplementedError("Memo creation not yet implemented")

    def _compile_quality_metrics(self, dqa_output: Any) -> Dict[str, Any]:
        """Extract and format quality metrics"""
        return {
            "roic": dqa_output.roic,
            "roe": dqa_output.roe,
            "moat_score": dqa_output.moat_score,
            "margin_stability": dqa_output.margin_stability,
            "earnings_quality": {
                "beneish_m_score": dqa_output.beneish_m_score,
                "cfo_ni_ratio": dqa_output.cfo_ni_ratio
            }
        }

    def _compile_valuation_summary(self, va_output: Any) -> Dict[str, Any]:
        """Extract and format valuation metrics"""
        return {
            "owner_earnings": va_output.owner_earnings,
            "intrinsic_value": {
                "low": va_output.intrinsic_value_low,
                "base": va_output.intrinsic_value_base,
                "high": va_output.intrinsic_value_high
            },
            "current_price": va_output.current_price,
            "margin_of_safety": va_output.margin_of_safety,
            "assumptions": va_output.dcf_assumptions
        }

    def _extract_bull_case(
        self,
        dqa_output: Any,
        va_output: Any
    ) -> List[str]:
        """
        Construct bull case arguments

        Based on:
        - Strong moat indicators
        - High ROIC/ROE
        - Attractive valuation (high MOS)
        - Stable margins
        """
        bull_points = []

        # TODO: Generate bull case from positive metrics
        # High moat score
        # Strong profitability
        # Good margin of safety
        # Stable business

        return bull_points

    def _extract_bear_case(self, da_output: Any) -> List[str]:
        """
        Extract bear case from Devil's Advocate

        Returns counter-arguments as list of concerns
        """
        return [
            f"[{arg.severity}] {arg.category}: {arg.claim}"
            for arg in da_output.counterarguments
        ]

    def _format_assumptions(
        self,
        va_output: Any,
        da_output: Any
    ) -> Dict[str, Any]:
        """
        Document key assumptions and adjustments

        Includes:
        - Original assumptions
        - DA-recommended adjustments
        - Final assumptions used
        """
        assumptions = va_output.dcf_assumptions.copy()

        # Add DA adjustments
        if da_output.required_adjustments:
            assumptions["da_adjustments"] = da_output.required_adjustments

        return assumptions

    def _compile_risks(self, da_output: Any) -> List[str]:
        """Extract key risks from Devil's Advocate analysis"""
        return [
            arg.claim
            for arg in da_output.counterarguments
            if arg.severity in ["A", "B"]
        ]

    def to_markdown(self, memo: InvestmentMemo) -> str:
        """
        Generate markdown-formatted memo

        Returns:
            Markdown string suitable for file output
        """
        md = f"""# Investment Memo: {memo.ticker}

**Analysis Date:** {memo.analysis_date}
**Decision:** {memo.decision}
**Position Size:** {memo.position_size:.1%}

---

## 📘 Business Summary

{memo.business_description}

### Competitive Moat
{memo.competitive_moat}

---

## 📊 Quality Metrics

- **ROIC:** {memo.quality_metrics.get('roic', 0):.1%}
- **ROE:** {memo.quality_metrics.get('roe', 0):.1%}
- **Moat Score:** {memo.quality_metrics.get('moat_score', 0)}/100
- **Margin Stability:** {memo.quality_metrics.get('margin_stability', 0):.2f}

---

## 💰 Valuation

### Owner's Earnings
${memo.valuation_summary.get('owner_earnings', 0):,.0f}

### Intrinsic Value Range
- **Bear:** ${memo.valuation_summary['intrinsic_value']['low']:,.0f}
- **Base:** ${memo.valuation_summary['intrinsic_value']['base']:,.0f}
- **Bull:** ${memo.valuation_summary['intrinsic_value']['high']:,.0f}

**Current Price:** ${memo.valuation_summary.get('current_price', 0):,.2f}
**Margin of Safety:** {memo.valuation_summary.get('margin_of_safety', 0):.1%}

---

## ✅ Bull Case

"""
        for point in memo.bull_case:
            md += f"- {point}\n"

        md += "\n---\n\n## 😈 Bear Case (Devil's Advocate)\n\n"
        for point in memo.bear_case:
            md += f"- {point}\n"

        md += f"\n---\n\n## 🎯 Decision Rationale\n\n{memo.reasoning}\n"

        md += "\n---\n\n## 🔑 Key Assumptions\n\n```yaml\n"
        # TODO: Format assumptions as YAML
        md += "# Assumptions here\n```\n"

        md += "\n---\n\n## ⚠️ Key Risks\n\n"
        for risk in memo.risks:
            md += f"- {risk}\n"

        md += "\n---\n\n## 📈 Monitoring Triggers\n\n"
        # TODO: Format triggers

        md += "\n---\n\n*Generated by Warren AI*\n"

        return md
