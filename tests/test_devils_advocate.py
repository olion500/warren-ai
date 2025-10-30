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


class TestCounterArguments:
    """Test counter-argument generation"""

    def test_strong_company_minimal_concerns(self, config, clean_dqa_output, clean_va_output):
        """Test that strong company gets minimal counter-arguments"""
        agent = DevilsAdvocateAgent(config)

        arguments = agent._generate_counterarguments("GOOD", clean_dqa_output, clean_va_output)

        # Strong company should have few or no serious concerns
        # May have some C-level monitoring points
        a_level = [arg for arg in arguments if arg.severity == "A"]
        b_level = [arg for arg in arguments if arg.severity == "B"]

        assert len(a_level) == 0  # No critical issues
        assert len(b_level) <= 1  # At most 1 significant concern

    def test_weak_profitability_concern(self, config, clean_va_output):
        """Test counter-argument for weak profitability"""
        agent = DevilsAdvocateAgent(config)

        weak_dqa = DataQualityOutput(
            ticker="WEAK",
            roic=0.08,  # Below 12% threshold
            roe=0.10,  # Below 15% threshold
            margin_stability=0.05,
            moat_score=65,  # Good moat
            data_warnings=[],
            beneish_m_score=-2.5,
            cfo_ni_ratio=1.0
        )

        arguments = agent._generate_counterarguments("WEAK", weak_dqa, clean_va_output)

        # Should have concern about profitability
        assert len(arguments) > 0
        profitability_args = [
            arg for arg in arguments
            if "roic" in arg.claim.lower() or "roe" in arg.claim.lower() or "profitability" in arg.claim.lower()
        ]
        assert len(profitability_args) > 0
        # Should be at least B-level concern
        assert any(arg.severity in ["A", "B"] for arg in profitability_args)

    def test_weak_moat_competitive_threat(self, config, clean_va_output):
        """Test counter-argument for weak competitive moat"""
        agent = DevilsAdvocateAgent(config)

        weak_moat_dqa = DataQualityOutput(
            ticker="NOMOAT",
            roic=0.15,
            roe=0.20,
            margin_stability=0.05,
            moat_score=45,  # Weak moat (40-60 range)
            data_warnings=[],
            beneish_m_score=-2.5,
            cfo_ni_ratio=1.0
        )

        arguments = agent._generate_counterarguments("NOMOAT", weak_moat_dqa, clean_va_output)

        # Should have concern about competitive advantage
        assert len(arguments) > 0
        moat_args = [
            arg for arg in arguments
            if "moat" in arg.claim.lower() or "competitive" in arg.claim.lower()
        ]
        assert len(moat_args) > 0
        assert any(arg.severity in ["A", "B"] for arg in moat_args)

    def test_low_mos_valuation_concern(self, config, clean_dqa_output):
        """Test counter-argument for low margin of safety"""
        agent = DevilsAdvocateAgent(config)

        low_mos_va = ValuationOutput(
            ticker="PRICEY",
            owner_earnings=10000000,
            intrinsic_value_base=120,
            intrinsic_value_low=100,
            intrinsic_value_high=140,
            current_price=100,
            margin_of_safety=0.17,  # Only 17% MOS (below 30% watch threshold)
            dcf_assumptions={}
        )

        arguments = agent._generate_counterarguments("PRICEY", clean_dqa_output, low_mos_va)

        # Should have valuation concern
        assert len(arguments) > 0
        valuation_args = [
            arg for arg in arguments
            if "valuation" in arg.claim.lower() or "margin of safety" in arg.claim.lower() or "price" in arg.claim.lower()
        ]
        assert len(valuation_args) > 0

    def test_multiple_issues_multiple_arguments(self, config):
        """Test multiple counter-arguments for problematic company"""
        agent = DevilsAdvocateAgent(config)

        bad_dqa = DataQualityOutput(
            ticker="BAD",
            roic=0.07,  # Low
            roe=0.09,  # Low
            margin_stability=0.15,  # High volatility
            moat_score=48,  # Weak
            data_warnings=[{"severity": "B", "category": "test", "message": "test"}],
            beneish_m_score=-2.3,  # Close to threshold
            cfo_ni_ratio=0.75  # Weak cash conversion
        )

        bad_va = ValuationOutput(
            ticker="BAD",
            owner_earnings=5000000,
            intrinsic_value_base=110,
            intrinsic_value_low=90,
            intrinsic_value_high=130,
            current_price=100,
            margin_of_safety=0.09,  # Very low
            dcf_assumptions={}
        )

        arguments = agent._generate_counterarguments("BAD", bad_dqa, bad_va)

        # Should have multiple concerns
        assert len(arguments) >= 3

        # Should cover multiple categories
        categories = {arg.category for arg in arguments}
        assert len(categories) >= 2

        # Should have mix of severities
        severities = {arg.severity for arg in arguments}
        assert "B" in severities or "A" in severities

    def test_counter_argument_structure(self, config, clean_dqa_output, clean_va_output):
        """Test that counter-arguments have proper structure"""
        agent = DevilsAdvocateAgent(config)

        arguments = agent._generate_counterarguments("TEST", clean_dqa_output, clean_va_output)

        for arg in arguments:
            # Check all required fields are present
            assert hasattr(arg, "severity")
            assert arg.severity in ["A", "B", "C"]
            assert hasattr(arg, "category")
            assert len(arg.category) > 0
            assert hasattr(arg, "claim")
            assert len(arg.claim) > 10  # Meaningful claim
            assert hasattr(arg, "evidence")
            assert len(arg.evidence) > 0
            assert hasattr(arg, "impact")
            assert len(arg.impact) > 0


class TestDAIntegration:
    """Test full DA analysis pipeline"""

    def test_clean_company_proceed(self, config, clean_dqa_output, clean_va_output):
        """Test DA analysis of clean company → PROCEED"""
        agent = DevilsAdvocateAgent(config)

        result = agent.analyze("GOOD", clean_dqa_output, clean_va_output)

        # Should not veto
        assert result.veto is False
        assert result.veto_reason is None

        # Should have minimal concerns
        a_level_args = [arg for arg in result.counterarguments if arg.severity == "A"]
        assert len(a_level_args) == 0

        # Should recommend PROCEED
        assert result.final_recommendation == "PROCEED"

        # Should have complete output
        assert result.ticker == "GOOD"
        assert isinstance(result.counterarguments, list)
        assert isinstance(result.required_adjustments, list)
        assert isinstance(result.stress_test_results, dict)

    def test_veto_triggers_reject(self, config, clean_va_output):
        """Test DA analysis with veto trigger → REJECT"""
        agent = DevilsAdvocateAgent(config)

        bad_dqa = DataQualityOutput(
            ticker="BAD",
            roic=0.15,
            roe=0.20,
            margin_stability=0.05,
            moat_score=30,  # Veto trigger!
            data_warnings=[],
            beneish_m_score=-2.5,
            cfo_ni_ratio=1.0
        )

        result = agent.analyze("BAD", bad_dqa, clean_va_output)

        # Should veto
        assert result.veto is True
        assert result.veto_reason is not None

        # Should recommend REJECT
        assert result.final_recommendation == "REJECT"

    def test_multiple_a_level_concerns_reject(self, config):
        """Test DA analysis with multiple A-level concerns → REJECT"""
        agent = DevilsAdvocateAgent(config)

        bad_dqa = DataQualityOutput(
            ticker="TERRIBLE",
            roic=0.05,  # A-level concern
            roe=0.07,  # A-level concern
            margin_stability=0.05,
            moat_score=65,  # OK
            data_warnings=[],
            beneish_m_score=-2.5,
            cfo_ni_ratio=1.0
        )

        bad_va = ValuationOutput(
            ticker="TERRIBLE",
            owner_earnings=10000000,
            intrinsic_value_base=150,
            intrinsic_value_low=120,
            intrinsic_value_high=180,
            current_price=100,
            margin_of_safety=0.33,  # OK
            dcf_assumptions={}
        )

        result = agent.analyze("TERRIBLE", bad_dqa, bad_va)

        # Should have multiple A-level concerns
        a_level_args = [arg for arg in result.counterarguments if arg.severity == "A"]
        assert len(a_level_args) >= 2

        # Should recommend REJECT (≥2 A-level concerns)
        assert result.final_recommendation == "REJECT"

    def test_multiple_b_level_concerns_reduce(self, config):
        """Test DA analysis with multiple B-level concerns → REDUCE"""
        agent = DevilsAdvocateAgent(config)

        marginal_dqa = DataQualityOutput(
            ticker="MARGINAL",
            roic=0.10,  # B-level concern (< 0.12)
            roe=0.13,  # B-level concern (< 0.15)
            margin_stability=0.12,  # B-level concern (> 0.10)
            moat_score=65,  # OK
            data_warnings=[],
            beneish_m_score=-2.5,
            cfo_ni_ratio=1.0
        )

        marginal_va = ValuationOutput(
            ticker="MARGINAL",
            owner_earnings=10000000,
            intrinsic_value_base=125,
            intrinsic_value_low=110,
            intrinsic_value_high=140,
            current_price=100,
            margin_of_safety=0.20,  # B-level concern (< 0.30)
            dcf_assumptions={}
        )

        result = agent.analyze("MARGINAL", marginal_dqa, marginal_va)

        # Should have multiple B-level concerns
        b_level_args = [arg for arg in result.counterarguments if arg.severity == "B"]
        assert len(b_level_args) >= 3

        # Should recommend REDUCE (≥3 B-level concerns)
        assert result.final_recommendation == "REDUCE"

    def test_recommendation_logic(self, config, clean_dqa_output, clean_va_output):
        """Test recommendation decision logic"""
        agent = DevilsAdvocateAgent(config)

        result = agent.analyze("TEST", clean_dqa_output, clean_va_output)

        # Recommendation should be one of the three
        assert result.final_recommendation in ["REJECT", "REDUCE", "PROCEED"]
