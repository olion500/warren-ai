"""
Data Quality Agent (DQA)
Gathers and validates financial data, computes quality metrics
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import statistics


@dataclass
class DataQualityOutput:
    """Output structure from Data Quality Agent"""
    ticker: str
    roic: float
    roe: float
    margin_stability: float
    moat_score: int
    data_warnings: List[Dict[str, str]]
    beneish_m_score: float
    cfo_ni_ratio: float


class DataQualityAgent:
    """
    Agent 1: Data Quality & Moat Analysis

    Responsibilities:
    - Gather and validate financial data (10-K, 10-Q)
    - Calculate profitability metrics (ROIC, ROE)
    - Assess margin stability
    - Compute competitive moat proxy score
    - Flag data integrity issues
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quality_thresholds = config.get("quality_metrics", {})

    def analyze(self, ticker: str, financial_data: Dict[str, Any]) -> DataQualityOutput:
        """
        Main analysis method

        Args:
            ticker: Stock symbol
            financial_data: Raw financial statements and metadata

        Returns:
            DataQualityOutput with metrics and warnings
        """
        # TODO: Implement data gathering and validation
        # TODO: Calculate ROIC = NOPAT / Invested Capital
        # TODO: Calculate ROE = Net Income / Shareholders' Equity
        # TODO: Assess margin volatility over time
        # TODO: Compute moat score (pricing power, returns, growth stability)
        # TODO: Calculate Beneish M-score for earnings quality
        # TODO: Check CFO/NI ratio

        raise NotImplementedError("DQA analysis pipeline not yet implemented")

    def _calculate_roic(self, data: Dict[str, Any]) -> float:
        """
        Calculate Return on Invested Capital

        ROIC = NOPAT / Invested Capital
        where:
        - NOPAT = Operating Income * (1 - Tax Rate)
        - Invested Capital = Total Assets - Current Liabilities - Cash
        """
        operating_income = data.get("operating_income", 0)
        tax_rate = data.get("tax_rate", 0.25)  # Default 25%

        # Calculate NOPAT
        nopat = operating_income * (1 - tax_rate)

        # Calculate Invested Capital
        total_assets = data.get("total_assets", 0)
        current_liabilities = data.get("current_liabilities", 0)
        cash = data.get("cash", 0)

        invested_capital = total_assets - current_liabilities - cash

        # Handle edge cases
        if invested_capital <= 0:
            return 0.0

        return nopat / invested_capital

    def _calculate_roe(self, data: Dict[str, Any]) -> float:
        """
        Calculate Return on Equity

        ROE = Net Income / Average Shareholders' Equity

        Uses average of current and previous year equity if available,
        otherwise uses current equity only.
        """
        net_income = data.get("net_income", 0)

        current_equity = data.get("shareholders_equity", 0)
        prev_equity = data.get("shareholders_equity_prev")

        # Calculate average equity if previous year available
        if prev_equity is not None and prev_equity > 0:
            avg_equity = (current_equity + prev_equity) / 2
        else:
            avg_equity = current_equity

        # Handle edge cases
        if avg_equity <= 0:
            return 0.0

        return net_income / avg_equity

    def _compute_moat_score(self, data: Dict[str, Any]) -> int:
        """
        Compute competitive moat score (0-100)

        Factors:
        - Pricing power (gross margin trends) - 35 points
        - ROIC persistence - 35 points
        - Revenue growth stability - 30 points

        Each factor scores based on:
        1. Absolute level (high is good)
        2. Stability (low volatility is good)
        """
        score = 0

        # Factor 1: Pricing Power (Gross Margin) - 35 points
        gross_margins = data.get("gross_margin", [])
        if gross_margins and len(gross_margins) >= 1:
            avg_margin = statistics.mean(gross_margins)

            # Level score (0-20): Scale 0-50% margin to 0-20 points
            level_score = min(20, avg_margin * 40)

            # Stability score (0-15): Lower std dev is better
            if len(gross_margins) >= 2:
                margin_volatility = statistics.stdev(gross_margins)
                # 0% volatility = 15 points, 20%+ volatility = 0 points
                stability_score = max(0, 15 - (margin_volatility * 75))
            else:
                stability_score = 7.5  # Half points for insufficient data

            score += level_score + stability_score

        # Factor 2: ROIC Persistence - 35 points
        roic_history = data.get("roic_history", [])
        if roic_history and len(roic_history) >= 1:
            avg_roic = statistics.mean(roic_history)

            # Level score (0-20): Scale 0-25% ROIC to 0-20 points
            level_score = min(20, avg_roic * 80)

            # Consistency score (0-15): Lower std dev is better
            if len(roic_history) >= 2:
                roic_volatility = statistics.stdev(roic_history)
                # 0% volatility = 15 points, 10%+ volatility = 0 points
                consistency_score = max(0, 15 - (roic_volatility * 150))
            else:
                consistency_score = 7.5

            score += level_score + consistency_score

        # Factor 3: Revenue Growth Stability - 30 points
        revenue_growth = data.get("revenue_growth", [])
        if revenue_growth and len(revenue_growth) >= 1:
            avg_growth = statistics.mean(revenue_growth)

            # Level score (0-15): Scale 0-15% growth to 0-15 points
            # Negative growth scores 0
            level_score = max(0, min(15, avg_growth * 100))

            # Stability score (0-15): Lower volatility is better
            if len(revenue_growth) >= 2:
                growth_volatility = statistics.stdev(revenue_growth)
                # 0% volatility = 15 points, 10%+ volatility = 0 points
                stability_score = max(0, 15 - (growth_volatility * 150))
            else:
                stability_score = 7.5

            score += level_score + stability_score

        # Cap at 100
        return min(100, int(round(score)))

    def _check_data_integrity(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Check for data quality issues

        Returns list of warnings with severity (A/B/C)
        """
        warnings = []
        # TODO: Check for missing data
        # TODO: Check for restatements
        # TODO: Validate consistency across periods
        return warnings
