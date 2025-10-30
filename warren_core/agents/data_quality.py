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
        # Calculate profitability metrics
        roic = self._calculate_roic(financial_data)
        roe = self._calculate_roe(financial_data)

        # Assess margin stability
        gross_margins = financial_data.get("gross_margin", [])
        if gross_margins and len(gross_margins) >= 2:
            margin_stability = statistics.stdev(gross_margins)
        else:
            margin_stability = 0.0

        # Compute competitive moat score
        moat_score = self._compute_moat_score(financial_data)

        # Get earnings quality metrics
        beneish_m_score = financial_data.get("beneish_m_score", -3.0)  # Default good

        cfo = financial_data.get("cfo", 0)
        net_income = financial_data.get("net_income", 1)
        cfo_ni_ratio = cfo / net_income if net_income > 0 else 0.0

        # Check data integrity
        data_warnings = self._check_data_integrity(financial_data)

        return DataQualityOutput(
            ticker=ticker,
            roic=roic,
            roe=roe,
            margin_stability=margin_stability,
            moat_score=moat_score,
            data_warnings=data_warnings,
            beneish_m_score=beneish_m_score,
            cfo_ni_ratio=cfo_ni_ratio
        )

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

        Returns list of warnings with severity (A/B/C):
        - A: Critical issues (auto-reject candidates)
        - B: Significant concerns (reduce position size)
        - C: Minor issues (monitor closely)
        """
        warnings = []

        # Check 1: Beneish M-score (earnings manipulation risk)
        beneish_m = data.get("beneish_m_score")
        if beneish_m is not None and beneish_m > -2.2:
            warnings.append({
                "severity": "A",
                "category": "earnings_quality",
                "message": f"High earnings manipulation risk (Beneish M-score: {beneish_m:.2f} > -2.2)"
            })

        # Check 2: CFO/NI ratio (cash conversion quality)
        cfo = data.get("cfo")
        net_income = data.get("net_income")

        if cfo is not None and net_income is not None and net_income > 0:
            cfo_ni_ratio = cfo / net_income

            if cfo_ni_ratio < 0.5:
                warnings.append({
                    "severity": "A",
                    "category": "cash_quality",
                    "message": f"Poor cash conversion (CFO/NI: {cfo_ni_ratio:.2f} < 0.5)"
                })
            elif cfo_ni_ratio < 0.8:
                warnings.append({
                    "severity": "B",
                    "category": "cash_quality",
                    "message": f"Weak cash conversion (CFO/NI: {cfo_ni_ratio:.2f} < 0.8)"
                })

        # Check 3: Missing critical fields
        critical_fields = [
            "operating_income", "net_income", "total_assets",
            "shareholders_equity", "cfo"
        ]

        missing_fields = [
            field for field in critical_fields
            if data.get(field) is None
        ]

        if missing_fields:
            warnings.append({
                "severity": "B" if len(missing_fields) <= 2 else "C",
                "category": "missing_data",
                "message": f"Missing critical fields: {', '.join(missing_fields)}"
            })

        # Check 4: Negative equity (balance sheet issue)
        equity = data.get("shareholders_equity")
        if equity is not None and equity < 0:
            warnings.append({
                "severity": "A",
                "category": "balance_sheet",
                "message": "Negative shareholders' equity (balance sheet distress)"
            })

        return warnings
