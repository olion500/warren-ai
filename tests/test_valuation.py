"""Tests for Valuation Agent"""

import pytest
from warren_core.agents.valuation import ValuationAgent, ValuationOutput


@pytest.fixture
def config():
    """Sample configuration"""
    return {
        "valuation": {
            "mos_buy_threshold": 0.50,
            "mos_watch_threshold": 0.30,
            "default_growth_rate": 0.05,
            "max_growth_rate": 0.15,
            "base_discount_rate": 0.10,
            "risk_premium_range": [0.02, 0.05]
        }
    }


@pytest.fixture
def sample_financial_data():
    """Sample financial data for testing"""
    return {
        "ticker": "TEST",
        "cfo": 10000000,  # $10M operating cash flow
        "total_capex": 4000000,  # $4M total capex
        "growth_capex_ratio": 0.50,  # 50% is growth capex
        # Maintenance capex = 4M * 0.5 = 2M
        # Owner's Earnings = 10M - 2M = 8M
    }


class TestOwnersEarningsCalculation:
    """Test Owner's Earnings calculation"""

    def test_owners_earnings_basic(self, config, sample_financial_data):
        """Test basic Owner's Earnings calculation"""
        agent = ValuationAgent(config)

        # Expected: CFO (10M) - Maintenance CapEx (2M) = 8M
        owner_earnings = agent._calculate_owner_earnings(sample_financial_data)
        assert owner_earnings == 8000000

    def test_owners_earnings_no_growth_capex(self, config):
        """Test when all capex is maintenance"""
        agent = ValuationAgent(config)

        data = {
            "cfo": 10000000,
            "total_capex": 3000000,
            "growth_capex_ratio": 0.0,  # All maintenance
        }

        owner_earnings = agent._calculate_owner_earnings(data)
        assert owner_earnings == 7000000  # 10M - 3M

    def test_owners_earnings_high_growth_capex(self, config):
        """Test with high growth capex"""
        agent = ValuationAgent(config)

        data = {
            "cfo": 15000000,
            "total_capex": 8000000,
            "growth_capex_ratio": 0.75,  # 75% growth, 25% maintenance
        }

        # Maintenance = 8M * 0.25 = 2M
        # Owner's Earnings = 15M - 2M = 13M
        owner_earnings = agent._calculate_owner_earnings(data)
        assert owner_earnings == 13000000

    def test_owners_earnings_negative_cfo(self, config):
        """Test with negative operating cash flow"""
        agent = ValuationAgent(config)

        data = {
            "cfo": -2000000,  # Negative CFO
            "total_capex": 1000000,
            "growth_capex_ratio": 0.5,
        }

        owner_earnings = agent._calculate_owner_earnings(data)
        assert owner_earnings < 0  # Should return negative

    def test_owners_earnings_missing_capex_data(self, config):
        """Test when capex data is missing"""
        agent = ValuationAgent(config)

        data = {
            "cfo": 10000000,
            # Missing capex data - should estimate conservatively
        }

        owner_earnings = agent._calculate_owner_earnings(data)
        # Should use conservative default (e.g., 30% of CFO for maintenance)
        assert owner_earnings == pytest.approx(7000000, rel=0.1)


class TestMarginOfSafety:
    """Test Margin of Safety calculation"""

    def test_mos_positive(self, config):
        """Test MOS with undervalued stock"""
        agent = ValuationAgent(config)

        # Intrinsic = $100, Price = $50
        # MOS = (100 - 50) / 100 = 0.50 (50%)
        mos = agent._calculate_mos(100, 50)
        assert mos == 0.50

    def test_mos_overvalued(self, config):
        """Test MOS with overvalued stock"""
        agent = ValuationAgent(config)

        # Intrinsic = $50, Price = $100
        # MOS = (50 - 100) / 50 = -1.0 (negative)
        mos = agent._calculate_mos(50, 100)
        assert mos == -1.0

    def test_mos_fair_value(self, config):
        """Test MOS at fair value"""
        agent = ValuationAgent(config)

        mos = agent._calculate_mos(100, 100)
        assert mos == 0.0

    def test_mos_zero_intrinsic_value(self, config):
        """Test MOS with zero intrinsic value"""
        agent = ValuationAgent(config)

        mos = agent._calculate_mos(0, 50)
        assert mos == -1.0  # Invalid case
