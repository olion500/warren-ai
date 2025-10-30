"""Tests for Devil's Advocate Agent"""

import pytest
from warren_core.agents.devils_advocate import (
    DevilsAdvocateAgent,
    DevilsAdvocateOutput,
    CounterArgument
)
from warren_core.agents.data_quality import DataQualityOutput
from warren_core.agents.valuation import ValuationOutput


@pytest.fixture
def config():
    """Sample configuration with veto rules"""
    return {
        "veto_rules": [
            {
                "name": "earnings_manipulation_risk",
                "severity": "A",
                "condition": "beneish_m_score > -2.2",
                "description": "High probability of earnings manipulation"
            },
            {
                "name": "poor_cash_conversion",
                "severity": "A",
                "condition": "cfo_ni_ratio < 0.5",
                "description": "Operating cash flow significantly below net income"
            },
            {
                "name": "no_competitive_moat",
                "severity": "A",
                "condition": "moat_score < 40",
                "description": "Weak or non-existent competitive advantages"
            },
            {
                "name": "no_margin_of_safety",
                "severity": "A",
                "condition": "mos < 0.10",
                "description": "Insufficient margin of safety"
            },
            {
                "name": "negative_owner_earnings",
                "severity": "A",
                "condition": "owner_earnings < 0",
                "description": "Company consuming cash rather than generating it"
            }
        ],
        "stress_test_scenarios": [
            {"name": "margin_compression", "adjustment": "operating_margin * 0.70"},
            {"name": "growth_slowdown", "adjustment": "growth_rate * 0.50"}
        ]
    }


@pytest.fixture
def clean_dqa_output():
    """Clean DQA output with no red flags"""
    return DataQualityOutput(
        ticker="GOOD",
        roic=0.18,
        roe=0.22,
        margin_stability=0.05,
        moat_score=75,
        data_warnings=[],
        beneish_m_score=-2.8,  # Good (< -2.2)
        cfo_ni_ratio=1.1  # Good (> 0.8)
    )


@pytest.fixture
def clean_va_output():
    """Clean VA output with good margin of safety"""
    return ValuationOutput(
        ticker="GOOD",
        owner_earnings=100000000,
        intrinsic_value_base=150,
        intrinsic_value_low=120,
        intrinsic_value_high=180,
        current_price=100,
        margin_of_safety=0.33,  # 33% MOS
        dcf_assumptions={"growth_rate": 0.05, "discount_rate": 0.10}
    )


class TestVetoRuleChecks:
    """Test veto rule checking logic"""

    def test_no_veto_clean_company(self, config, clean_dqa_output, clean_va_output):
        """Test that clean company passes all veto checks"""
        agent = DevilsAdvocateAgent(config)

        veto, reason = agent._check_veto_rules(clean_dqa_output, clean_va_output)

        assert veto is False
        assert reason is None

    def test_veto_earnings_manipulation(self, config, clean_va_output):
        """Test veto for earnings manipulation risk"""
        agent = DevilsAdvocateAgent(config)

        bad_dqa = DataQualityOutput(
            ticker="BAD",
            roic=0.15,
            roe=0.20,
            margin_stability=0.05,
            moat_score=70,
            data_warnings=[],
            beneish_m_score=-1.5,  # Bad! (> -2.2)
            cfo_ni_ratio=1.0
        )

        veto, reason = agent._check_veto_rules(bad_dqa, clean_va_output)

        assert veto is True
        assert "earnings manipulation" in reason.lower() or "beneish" in reason.lower()

    def test_veto_poor_cash_conversion(self, config, clean_dqa_output):
        """Test veto for poor cash conversion"""
        agent = DevilsAdvocateAgent(config)

        bad_va = ValuationOutput(
            ticker="BAD",
            owner_earnings=10000000,
            intrinsic_value_base=150,
            intrinsic_value_low=120,
            intrinsic_value_high=180,
            current_price=100,
            margin_of_safety=0.33,
            dcf_assumptions={}
        )

        bad_dqa = DataQualityOutput(
            ticker="BAD",
            roic=0.15,
            roe=0.20,
            margin_stability=0.05,
            moat_score=70,
            data_warnings=[],
            beneish_m_score=-2.5,  # Good
            cfo_ni_ratio=0.3  # Bad! (< 0.5)
        )

        veto, reason = agent._check_veto_rules(bad_dqa, bad_va)

        assert veto is True
        assert "cash" in reason.lower() or "cfo" in reason.lower()

    def test_veto_no_moat(self, config, clean_va_output):
        """Test veto for weak competitive moat"""
        agent = DevilsAdvocateAgent(config)

        bad_dqa = DataQualityOutput(
            ticker="BAD",
            roic=0.15,
            roe=0.20,
            margin_stability=0.05,
            moat_score=30,  # Bad! (< 40)
            data_warnings=[],
            beneish_m_score=-2.5,
            cfo_ni_ratio=1.0
        )

        veto, reason = agent._check_veto_rules(bad_dqa, clean_va_output)

        assert veto is True
        assert "moat" in reason.lower() or "competitive" in reason.lower()

    def test_veto_no_margin_of_safety(self, config, clean_dqa_output):
        """Test veto for insufficient margin of safety"""
        agent = DevilsAdvocateAgent(config)

        bad_va = ValuationOutput(
            ticker="BAD",
            owner_earnings=10000000,
            intrinsic_value_base=105,
            intrinsic_value_low=100,
            intrinsic_value_high=110,
            current_price=100,
            margin_of_safety=0.05,  # Bad! (< 0.10, only 5%)
            dcf_assumptions={}
        )

        veto, reason = agent._check_veto_rules(clean_dqa_output, bad_va)

        assert veto is True
        assert "margin of safety" in reason.lower() or "mos" in reason.lower()

    def test_veto_negative_owner_earnings(self, config, clean_dqa_output):
        """Test veto for negative owner earnings"""
        agent = DevilsAdvocateAgent(config)

        bad_va = ValuationOutput(
            ticker="BAD",
            owner_earnings=-5000000,  # Negative!
            intrinsic_value_base=150,
            intrinsic_value_low=120,
            intrinsic_value_high=180,
            current_price=100,
            margin_of_safety=0.33,  # MOS is OK, but owner_earnings is negative
            dcf_assumptions={}
        )

        veto, reason = agent._check_veto_rules(clean_dqa_output, bad_va)

        assert veto is True
        assert "owner" in reason.lower() or "earnings" in reason.lower() or "cash" in reason.lower()

    def test_multiple_veto_triggers(self, config):
        """Test company with multiple veto triggers"""
        agent = DevilsAdvocateAgent(config)

        bad_dqa = DataQualityOutput(
            ticker="TERRIBLE",
            roic=0.05,
            roe=0.08,
            margin_stability=0.15,
            moat_score=25,  # Veto trigger 1
            data_warnings=[],
            beneish_m_score=-1.0,  # Veto trigger 2
            cfo_ni_ratio=0.3  # Veto trigger 3
        )

        bad_va = ValuationOutput(
            ticker="TERRIBLE",
            owner_earnings=-1000000,  # Veto trigger 4
            intrinsic_value_base=50,
            intrinsic_value_low=40,
            intrinsic_value_high=60,
            current_price=100,
            margin_of_safety=-1.0,  # Veto trigger 5
            dcf_assumptions={}
        )

        veto, reason = agent._check_veto_rules(bad_dqa, bad_va)

        assert veto is True
        assert reason is not None
        # Should mention at least one of the issues
        assert len(reason) > 10
