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
