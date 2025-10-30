"""Tests for Data Quality Agent"""

import pytest
from warren_core.agents.data_quality import DataQualityAgent, DataQualityOutput


@pytest.fixture
def config():
    """Sample configuration"""
    return {
        "quality_metrics": {
            "roic_min": 0.12,
            "roe_min": 0.15,
            "margin_volatility_max": 0.20,
            "moat_score_min": 60
        }
    }


@pytest.fixture
def sample_financial_data():
    """Sample financial data for testing"""
    return {
        "ticker": "TEST",
        "operating_income": 10000000,  # $10M
        "tax_rate": 0.25,
        "total_assets": 50000000,  # $50M
        "current_liabilities": 10000000,  # $10M
        "cash": 5000000,  # $5M
        "net_income": 7500000,  # $7.5M
        "shareholders_equity": 30000000,  # $30M
        "shareholders_equity_prev": 28000000,  # Previous year
        "gross_margin": [0.40, 0.42, 0.41, 0.43, 0.42],  # 5 years
        "roic_history": [0.15, 0.16, 0.14, 0.15, 0.16],  # 5 years
        "revenue_growth": [0.08, 0.10, 0.09, 0.11, 0.10],  # 5 years
        "cfo": 8000000,  # Operating cash flow
        "beneish_m_score": -2.5,  # Good (< -2.2)
    }


class TestROICCalculation:
    """Test ROIC calculation"""

    def test_roic_basic_calculation(self, config, sample_financial_data):
        """Test basic ROIC calculation"""
        agent = DataQualityAgent(config)

        # Expected: NOPAT = 10M * (1 - 0.25) = 7.5M
        # Invested Capital = 50M - 10M - 5M = 35M
        # ROIC = 7.5M / 35M = 0.214 (21.4%)

        roic = agent._calculate_roic(sample_financial_data)
        assert roic == pytest.approx(0.214, rel=0.01)

    def test_roic_with_zero_invested_capital(self, config):
        """Test ROIC when invested capital is zero or negative"""
        agent = DataQualityAgent(config)

        data = {
            "operating_income": 10000000,
            "tax_rate": 0.25,
            "total_assets": 15000000,
            "current_liabilities": 10000000,
            "cash": 10000000,  # Assets = Liabilities + Cash
        }

        roic = agent._calculate_roic(data)
        assert roic == 0.0  # Should return 0 for invalid capital

    def test_roic_with_negative_operating_income(self, config):
        """Test ROIC with negative operating income"""
        agent = DataQualityAgent(config)

        data = {
            "operating_income": -5000000,
            "tax_rate": 0.25,
            "total_assets": 50000000,
            "current_liabilities": 10000000,
            "cash": 5000000,
        }

        roic = agent._calculate_roic(data)
        assert roic < 0  # Negative ROIC


class TestROECalculation:
    """Test ROE calculation"""

    def test_roe_basic_calculation(self, config, sample_financial_data):
        """Test basic ROE calculation"""
        agent = DataQualityAgent(config)

        # Expected: ROE = 7.5M / avg(30M, 28M) = 7.5M / 29M = 0.259 (25.9%)

        roe = agent._calculate_roe(sample_financial_data)
        assert roe == pytest.approx(0.259, rel=0.01)

    def test_roe_with_zero_equity(self, config):
        """Test ROE when equity is zero"""
        agent = DataQualityAgent(config)

        data = {
            "net_income": 5000000,
            "shareholders_equity": 0,
            "shareholders_equity_prev": 0,
        }

        roe = agent._calculate_roe(data)
        assert roe == 0.0  # Should return 0 for invalid equity

    def test_roe_only_current_equity(self, config):
        """Test ROE when only current equity available"""
        agent = DataQualityAgent(config)

        data = {
            "net_income": 7500000,
            "shareholders_equity": 30000000,
        }

        roe = agent._calculate_roe(data)
        assert roe == pytest.approx(0.25, rel=0.01)  # Use current equity only


class TestMoatScore:
    """Test moat score calculation"""

    def test_moat_score_strong_moat(self, config, sample_financial_data):
        """Test moat score for company with strong competitive advantages"""
        agent = DataQualityAgent(config)

        # Strong moat characteristics:
        # - Stable high gross margins
        # - Consistent high ROIC
        # - Stable revenue growth
        data = sample_financial_data.copy()

        moat_score = agent._compute_moat_score(data)

        # Should be >= 60 (threshold for consideration)
        assert moat_score >= 60
        assert moat_score <= 100

    def test_moat_score_weak_moat(self, config):
        """Test moat score for company with weak competitive advantages"""
        agent = DataQualityAgent(config)

        data = {
            "gross_margin": [0.10, 0.08, 0.12, 0.09, 0.11],  # Low, volatile
            "roic_history": [0.05, 0.03, 0.06, 0.04, 0.05],  # Low ROIC
            "revenue_growth": [0.02, -0.01, 0.03, 0.01, 0.02],  # Volatile growth
        }

        moat_score = agent._compute_moat_score(data)

        # Should be < 60 (below consideration threshold)
        assert moat_score < 60
        assert moat_score >= 0

    def test_moat_score_components(self, config):
        """Test that moat score considers all components"""
        agent = DataQualityAgent(config)

        # Perfect on all dimensions
        perfect_data = {
            "gross_margin": [0.50, 0.50, 0.50, 0.50, 0.50],  # Stable high margin
            "roic_history": [0.20, 0.20, 0.20, 0.20, 0.20],  # Consistent high ROIC
            "revenue_growth": [0.10, 0.10, 0.10, 0.10, 0.10],  # Stable growth
        }

        score_perfect = agent._compute_moat_score(perfect_data)

        # Near-perfect should score very high
        assert score_perfect >= 85

    def test_moat_score_missing_data(self, config):
        """Test moat score with incomplete data"""
        agent = DataQualityAgent(config)

        data = {
            "gross_margin": [0.40, 0.42],  # Only 2 years
            "roic_history": [0.15],  # Only 1 year
        }

        moat_score = agent._compute_moat_score(data)

        # Should still return a valid score (conservative estimate)
        assert 0 <= moat_score <= 100


class TestDataIntegrity:
    """Test data integrity checks"""

    def test_data_integrity_clean_data(self, config, sample_financial_data):
        """Test data integrity with clean financial data"""
        agent = DataQualityAgent(config)

        warnings = agent._check_data_integrity(sample_financial_data)

        # Clean data should have no warnings
        assert len(warnings) == 0

    def test_data_integrity_beneish_warning(self, config):
        """Test earnings manipulation warning (Beneish M-score)"""
        agent = DataQualityAgent(config)

        data = {
            "ticker": "TEST",
            "beneish_m_score": -1.5,  # > -2.2 threshold (bad)
            "cfo": 8000000,
            "net_income": 7500000,
        }

        warnings = agent._check_data_integrity(data)

        # Should have A-level warning for earnings manipulation risk
        assert len(warnings) > 0
        assert any(w["severity"] == "A" for w in warnings)
        assert any("earnings" in w["message"].lower() for w in warnings)

    def test_data_integrity_cfo_ni_warning(self, config):
        """Test poor cash conversion warning"""
        agent = DataQualityAgent(config)

        data = {
            "ticker": "TEST",
            "beneish_m_score": -2.5,  # Good
            "cfo": 3000000,  # CFO
            "net_income": 10000000,  # NI
            # CFO/NI = 0.3 < 0.8 threshold
        }

        warnings = agent._check_data_integrity(data)

        # Should have warning for poor cash conversion
        assert len(warnings) > 0
        assert any("cash" in w["message"].lower() for w in warnings)

    def test_data_integrity_missing_fields(self, config):
        """Test warnings for missing critical fields"""
        agent = DataQualityAgent(config)

        data = {
            "ticker": "TEST",
            # Missing many fields
        }

        warnings = agent._check_data_integrity(data)

        # Should have warnings for missing data
        assert len(warnings) > 0
        assert any(w["severity"] in ["B", "C"] for w in warnings)

    def test_data_integrity_multiple_issues(self, config):
        """Test handling of multiple data quality issues"""
        agent = DataQualityAgent(config)

        data = {
            "ticker": "TEST",
            "beneish_m_score": -1.0,  # Bad (> -2.2)
            "cfo": 2000000,
            "net_income": 10000000,  # Bad ratio
            # Missing other fields
        }

        warnings = agent._check_data_integrity(data)

        # Should have multiple warnings
        assert len(warnings) >= 2


class TestDQAIntegration:
    """Test full DQA analysis pipeline"""

    def test_full_analysis(self, config, sample_financial_data):
        """Test complete DQA analysis pipeline"""
        agent = DataQualityAgent(config)

        result = agent.analyze("TEST", sample_financial_data)

        # Verify all outputs are present
        assert result.ticker == "TEST"
        assert result.roic > 0
        assert result.roe > 0
        assert result.moat_score >= 0
        assert result.moat_score <= 100
        assert result.beneish_m_score < -2.2  # Good
        assert result.cfo_ni_ratio > 0.8  # Good
        assert len(result.data_warnings) == 0  # Clean data

    def test_analysis_with_warnings(self, config):
        """Test DQA analysis with problematic data"""
        agent = DataQualityAgent(config)

        bad_data = {
            "ticker": "BAD",
            "operating_income": 5000000,
            "tax_rate": 0.25,
            "total_assets": 20000000,
            "current_liabilities": 5000000,
            "cash": 2000000,
            "net_income": 10000000,
            "shareholders_equity": 15000000,
            "gross_margin": [0.20, 0.18, 0.22],
            "roic_history": [0.08, 0.07, 0.09],
            "revenue_growth": [0.03, -0.01, 0.02],
            "cfo": 3000000,  # Poor cash conversion
            "beneish_m_score": -1.5,  # Manipulation risk
        }

        result = agent.analyze("BAD", bad_data)

        # Should have warnings
        assert len(result.data_warnings) > 0
        # Should have lower moat score
        assert result.moat_score < 60
        # Should flag cash quality issues
        assert any(w["severity"] == "A" for w in result.data_warnings)
