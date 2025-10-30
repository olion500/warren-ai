"""
Devil's Advocate Agent (DA)
Mandatory contrarian analysis and stress testing
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class CounterArgument:
    """Individual counter-argument"""
    severity: str  # A, B, or C
    category: str
    claim: str
    evidence: str
    impact: str


@dataclass
class DevilsAdvocateOutput:
    """Output structure from Devil's Advocate Agent"""
    ticker: str
    veto: bool
    veto_reason: str | None
    counterarguments: List[CounterArgument]
    required_adjustments: List[Dict[str, Any]]
    stress_test_results: Dict[str, Any]
    final_recommendation: str  # "REJECT", "REDUCE", "PROCEED"


class DevilsAdvocateAgent:
    """
    Agent 3: Devil's Advocate (Critical Review)

    Responsibilities:
    - Generate counter-arguments to bull thesis
    - Stress-test valuation assumptions
    - Check for historical failure patterns
    - Issue veto on fatal flaws
    - Require assumption adjustments
    - Provide "steel man" contrarian case
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.veto_rules = config.get("veto_rules", [])

    def analyze(
        self,
        ticker: str,
        dqa_output: Any,
        va_output: Any
    ) -> DevilsAdvocateOutput:
        """
        Main contrarian analysis

        Args:
            ticker: Stock symbol
            dqa_output: Results from Data Quality Agent
            va_output: Results from Valuation Agent

        Returns:
            DevilsAdvocateOutput with veto decision and counter-arguments
        """
        # Step 1: Check veto rules
        veto, veto_reason = self._check_veto_rules(dqa_output, va_output)

        # Step 2: Generate counter-arguments
        counterarguments = self._generate_counterarguments(ticker, dqa_output, va_output)

        # Step 3: Run stress tests (TODO: implement full stress testing)
        stress_test_results = {}  # Placeholder for now

        # Step 4: Recommend assumption adjustments (TODO: implement)
        required_adjustments = []  # Placeholder for now

        # Step 5: Make final recommendation
        final_recommendation = self._make_recommendation(veto, counterarguments, stress_test_results)

        return DevilsAdvocateOutput(
            ticker=ticker,
            veto=veto,
            veto_reason=veto_reason,
            counterarguments=counterarguments,
            required_adjustments=required_adjustments,
            stress_test_results=stress_test_results,
            final_recommendation=final_recommendation
        )

    def _check_veto_rules(
        self,
        dqa_output: Any,
        va_output: Any
    ) -> tuple[bool, str | None]:
        """
        Check if any automatic veto rules are triggered

        Returns:
            (veto_triggered, reason)
        """
        veto_rules = self.config.get("veto_rules", [])

        for rule in veto_rules:
            # Only check A-level (automatic veto) rules
            if rule.get("severity") != "A":
                continue

            condition = rule.get("condition", "")
            description = rule.get("description", "")

            # Evaluate condition
            triggered = self._evaluate_condition(condition, dqa_output, va_output)

            if triggered:
                return True, description

        return False, None

    def _evaluate_condition(
        self,
        condition: str,
        dqa_output: Any,
        va_output: Any
    ) -> bool:
        """
        Evaluate a veto rule condition

        Supported conditions:
        - beneish_m_score > -2.2
        - cfo_ni_ratio < 0.5
        - moat_score < 40
        - mos < 0.10
        - owner_earnings < 0
        """
        # Parse condition: "metric operator value"
        parts = condition.split()
        if len(parts) != 3:
            return False  # Invalid condition format

        metric, operator, threshold_str = parts

        try:
            threshold = float(threshold_str)
        except ValueError:
            return False  # Invalid threshold

        # Get metric value from outputs
        if hasattr(dqa_output, metric):
            value = getattr(dqa_output, metric)
        elif hasattr(va_output, metric):
            value = getattr(va_output, metric)
        elif metric == "mos":  # Alias for margin_of_safety
            value = getattr(va_output, "margin_of_safety", 0)
        else:
            return False  # Unknown metric

        # Evaluate condition
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        else:
            return False  # Unknown operator

    def _generate_counterarguments(
        self,
        ticker: str,
        dqa_output: Any,
        va_output: Any
    ) -> List[CounterArgument]:
        """
        Generate specific counter-arguments to the bull case

        Categories:
        - Profitability concerns
        - Competitive threats
        - Valuation concerns
        - Cash quality concerns
        - Business stability concerns
        """
        arguments = []

        # 1. Profitability Concerns
        if dqa_output.roic < 0.12:  # Below 12% threshold
            severity = "B" if dqa_output.roic >= 0.08 else "A"
            arguments.append(CounterArgument(
                severity=severity,
                category="profitability",
                claim=f"Below-average ROIC ({dqa_output.roic:.1%}) indicates weak capital efficiency",
                evidence=f"ROIC of {dqa_output.roic:.1%} is below the 12% quality threshold, suggesting the company struggles to generate returns on invested capital",
                impact="Lower ROIC reduces intrinsic value and indicates potential competitive disadvantages or capital allocation issues"
            ))

        if dqa_output.roe < 0.15:  # Below 15% threshold
            severity = "B" if dqa_output.roe >= 0.10 else "A"
            arguments.append(CounterArgument(
                severity=severity,
                category="profitability",
                claim=f"Subpar ROE ({dqa_output.roe:.1%}) suggests inefficient use of shareholder equity",
                evidence=f"ROE of {dqa_output.roe:.1%} falls short of the 15% quality threshold",
                impact="Mediocre returns on equity may indicate management inefficiency or structural business challenges"
            ))

        # 2. Competitive Moat Concerns
        if dqa_output.moat_score < 60:
            if dqa_output.moat_score < 40:
                severity = "A"
                claim = f"No durable competitive advantage (moat score: {dqa_output.moat_score}/100)"
                impact = "Without a moat, the company is vulnerable to competition and unlikely to sustain above-average returns"
            else:
                severity = "B"
                claim = f"Weak competitive moat (moat score: {dqa_output.moat_score}/100)"
                impact = "Marginal competitive advantages may erode under competitive pressure or market changes"

            arguments.append(CounterArgument(
                severity=severity,
                category="competitive_moat",
                claim=claim,
                evidence=f"Moat score of {dqa_output.moat_score}/100 indicates limited pricing power, inconsistent ROIC, or unstable growth",
                impact=impact
            ))

        # 3. Valuation Concerns
        if va_output.margin_of_safety < 0.30:  # Below 30% watch threshold
            if va_output.margin_of_safety < 0.10:
                severity = "A"
                claim = f"Minimal margin of safety ({va_output.margin_of_safety:.0%}) provides no downside protection"
            elif va_output.margin_of_safety < 0.20:
                severity = "B"
                claim = f"Thin margin of safety ({va_output.margin_of_safety:.0%}) offers limited downside protection"
            else:
                severity = "C"
                claim = f"Modest margin of safety ({va_output.margin_of_safety:.0%}) leaves little room for error"

            arguments.append(CounterArgument(
                severity=severity,
                category="valuation",
                claim=claim,
                evidence=f"At {va_output.margin_of_safety:.0%} MOS, current price is {100 - va_output.margin_of_safety * 100:.0f}% of intrinsic value",
                impact="Limited margin of safety increases risk if growth disappoints or assumptions prove optimistic"
            ))

        # 4. Cash Quality Concerns
        if dqa_output.cfo_ni_ratio < 0.8:  # Below threshold (already checked in veto for < 0.5)
            if dqa_output.cfo_ni_ratio >= 0.5:
                severity = "B"
                arguments.append(CounterArgument(
                    severity=severity,
                    category="cash_quality",
                    claim=f"Weak cash conversion (CFO/NI: {dqa_output.cfo_ni_ratio:.2f}) raises earnings quality concerns",
                    evidence=f"Operating cash flow of {dqa_output.cfo_ni_ratio:.2f}x net income suggests potential accounting aggressiveness",
                    impact="Lower cash conversion may indicate earnings quality issues or working capital deterioration"
                ))

        # 5. Margin Stability Concerns
        if dqa_output.margin_stability > 0.10:  # High volatility
            severity = "B" if dqa_output.margin_stability < 0.15 else "A"
            arguments.append(CounterArgument(
                severity=severity,
                category="business_stability",
                claim=f"High margin volatility ({dqa_output.margin_stability:.1%} std dev) indicates business instability",
                evidence=f"Gross margin standard deviation of {dqa_output.margin_stability:.1%} suggests inconsistent pricing power or cost control",
                impact="Margin instability makes future cash flows unpredictable and increases valuation uncertainty"
            ))

        # 6. Data Quality Red Flags
        for warning in dqa_output.data_warnings:
            if warning["severity"] in ["A", "B"]:
                arguments.append(CounterArgument(
                    severity=warning["severity"],
                    category="data_quality",
                    claim=f"Data quality issue: {warning['category']}",
                    evidence=warning["message"],
                    impact="Data integrity concerns undermine confidence in financial analysis"
                ))

        return arguments

    def _run_stress_tests(
        self,
        va_output: Any
    ) -> Dict[str, Any]:
        """
        Run stress test scenarios from config

        Scenarios:
        - Margin compression (30% decline)
        - Growth slowdown (50% reduction)
        - CapEx surge (50% increase)
        - Multiple contraction (20% lower)
        - Combined worst case
        """
        results = {}

        # TODO: Re-run DCF with stressed assumptions
        # TODO: Calculate stressed MOS
        # TODO: Determine if investment still viable under stress

        return results

    def _suggest_adjustments(
        self,
        dqa_output: Any,
        va_output: Any,
        stress_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Suggest parameter adjustments based on findings

        Examples:
        - Increase maintenance CapEx estimate
        - Reduce growth assumptions
        - Increase discount rate
        - Add risk premium
        """
        adjustments = []

        # TODO: Analyze if assumptions are too optimistic
        # TODO: Recommend conservative adjustments

        return adjustments

    def _make_recommendation(
        self,
        veto: bool,
        counterarguments: List[CounterArgument],
        stress_results: Dict[str, Any]
    ) -> str:
        """
        Final recommendation: REJECT, REDUCE, or PROCEED

        Logic:
        - REJECT: Veto triggered OR ≥2 A-level concerns
        - REDUCE: ≥3 B-level concerns OR stress tests fail significantly
        - PROCEED: Concerns are manageable
        """
        # Rule 1: Veto triggers automatic rejection
        if veto:
            return "REJECT"

        # Rule 2: Multiple A-level concerns = REJECT
        a_level_count = sum(1 for arg in counterarguments if arg.severity == "A")
        if a_level_count >= 2:
            return "REJECT"

        # Rule 3: Multiple B-level concerns = REDUCE
        b_level_count = sum(1 for arg in counterarguments if arg.severity == "B")
        if b_level_count >= 3:
            return "REDUCE"

        # Rule 4: Stress test failures (TODO: implement when stress tests ready)
        # For now, if stress_results has 'failed' key, consider it
        if stress_results.get("failed", False):
            return "REDUCE"

        # Rule 5: Single A-level concern = REDUCE (to be conservative)
        if a_level_count == 1:
            return "REDUCE"

        # Otherwise: Concerns are manageable
        return "PROCEED"
