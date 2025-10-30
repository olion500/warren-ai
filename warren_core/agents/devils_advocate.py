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
        # TODO: Check veto rules
        # TODO: Generate counter-arguments
        # TODO: Run stress tests
        # TODO: Recommend assumption adjustments
        # TODO: Make final recommendation

        raise NotImplementedError("Devil's Advocate analysis not yet implemented")

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
        # TODO: Check each veto rule from config
        # TODO: Return True and reason if any A-level trigger hits
        return False, None

    def _generate_counterarguments(
        self,
        ticker: str,
        dqa_output: Any,
        va_output: Any
    ) -> List[CounterArgument]:
        """
        Generate specific counter-arguments to the bull case

        Categories:
        - Business model vulnerabilities
        - Competitive threats
        - Cyclicality and macro sensitivity
        - Management concerns
        - Valuation optimism
        - Hidden liabilities
        """
        arguments = []

        # TODO: Analyze business model risks
        # TODO: Check for competitive threats
        # TODO: Assess cyclicality
        # TODO: Review management track record
        # TODO: Challenge valuation assumptions
        # TODO: Look for off-balance-sheet risks

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
        - REJECT: Veto triggered or >2 A-level concerns
        - REDUCE: Multiple B-level concerns or stress tests fail
        - PROCEED: Concerns are manageable
        """
        if veto:
            return "REJECT"

        a_level_count = sum(1 for arg in counterarguments if arg.severity == "A")
        if a_level_count >= 2:
            return "REJECT"

        b_level_count = sum(1 for arg in counterarguments if arg.severity == "B")
        if b_level_count >= 3:
            return "REDUCE"

        # TODO: Check stress test results
        # TODO: Apply decision logic

        return "PROCEED"
