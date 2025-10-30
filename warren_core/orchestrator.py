"""
Warren AI Orchestrator
Coordinates the 5-agent analysis pipeline
"""

import argparse
import yaml
from pathlib import Path
from typing import Dict, Any

from warren_core.agents import (
    DataQualityAgent,
    ValuationAgent,
    DevilsAdvocateAgent,
    PortfolioAgent,
    MemoAuditAgent,
)


class WarrenOrchestrator:
    """
    Main orchestrator for Warren AI analysis pipeline

    Agent Flow:
    DQA → VA → DA → PA → MAA

    Each agent processes outputs from previous agents and
    passes results forward through the pipeline.
    """

    def __init__(self, config_dir: Path | None = None):
        """
        Initialize orchestrator with configuration

        Args:
            config_dir: Path to config directory (defaults to warren_core/configs)
        """
        if config_dir is None:
            config_dir = Path(__file__).parent / "configs"

        self.config = self._load_config(config_dir)
        self._initialize_agents()

    def _load_config(self, config_dir: Path) -> Dict[str, Any]:
        """Load configuration files"""
        thresholds_path = config_dir / "thresholds.yml"
        veto_rules_path = config_dir / "veto_rules.yml"

        with open(thresholds_path) as f:
            thresholds = yaml.safe_load(f)

        with open(veto_rules_path) as f:
            veto_rules = yaml.safe_load(f)

        return {
            **thresholds,
            "veto_rules": veto_rules.get("veto_rules", []),
            "stress_test_scenarios": veto_rules.get("stress_test_scenarios", []),
            "warning_levels": veto_rules.get("warning_levels", {})
        }

    def _initialize_agents(self):
        """Initialize all agents with configuration"""
        self.dqa = DataQualityAgent(self.config)
        self.va = ValuationAgent(self.config)
        self.da = DevilsAdvocateAgent(self.config)
        self.pa = PortfolioAgent(self.config)
        self.maa = MemoAuditAgent(self.config)

    def analyze_stock(
        self,
        ticker: str,
        financial_data: Dict[str, Any] | None = None,
        current_price: float | None = None,
        current_portfolio: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Run complete analysis pipeline for a stock

        Args:
            ticker: Stock symbol
            financial_data: Financial statements (or None to fetch)
            current_price: Current market price (or None to fetch)
            current_portfolio: Current portfolio holdings

        Returns:
            Complete analysis results including final memo
        """
        print(f"🧠 Warren AI Analysis: {ticker}")
        print("=" * 60)

        # TODO: If financial_data is None, fetch from data source
        # TODO: If current_price is None, fetch current quote

        # Step 1: Data Quality Agent
        print("\n📊 Step 1: Data Quality & Moat Analysis...")
        try:
            dqa_output = self.dqa.analyze(ticker, financial_data)
            print(f"  ✓ ROIC: {dqa_output.roic:.1%}")
            print(f"  ✓ ROE: {dqa_output.roe:.1%}")
            print(f"  ✓ Moat Score: {dqa_output.moat_score}/100")
        except NotImplementedError:
            print("  ⚠️  DQA not yet implemented")
            return {"error": "DQA not implemented"}

        # Step 2: Valuation Agent
        print("\n💰 Step 2: Valuation Analysis...")
        try:
            va_output = self.va.analyze(ticker, financial_data, current_price)
            print(f"  ✓ Owner's Earnings: ${va_output.owner_earnings:,.0f}")
            print(f"  ✓ Intrinsic Value: ${va_output.intrinsic_value_base:,.0f}")
            print(f"  ✓ Margin of Safety: {va_output.margin_of_safety:.1%}")
        except NotImplementedError:
            print("  ⚠️  VA not yet implemented")
            return {"error": "VA not implemented"}

        # Step 3: Devil's Advocate
        print("\n😈 Step 3: Devil's Advocate Review...")
        try:
            da_output = self.da.analyze(ticker, dqa_output, va_output)
            if da_output.veto:
                print(f"  🚫 VETO: {da_output.veto_reason}")
            else:
                print(f"  ✓ No veto issued")
            print(f"  ✓ Counter-arguments: {len(da_output.counterarguments)}")
            print(f"  ✓ Recommendation: {da_output.final_recommendation}")
        except NotImplementedError:
            print("  ⚠️  DA not yet implemented")
            return {"error": "DA not implemented"}

        # Step 4: Portfolio Agent
        print("\n📈 Step 4: Portfolio Decision...")
        try:
            pa_output = self.pa.analyze(
                ticker, dqa_output, va_output, da_output, current_portfolio
            )
            print(f"  ✓ Decision: {pa_output.decision}")
            if pa_output.decision == "BUY":
                print(f"  ✓ Position Size: {pa_output.position_size:.1%}")
        except NotImplementedError:
            print("  ⚠️  PA not yet implemented")
            return {"error": "PA not implemented"}

        # Step 5: Memo & Audit
        print("\n📝 Step 5: Investment Memo Generation...")
        try:
            memo = self.maa.create_memo(
                ticker, dqa_output, va_output, da_output, pa_output
            )
            print(f"  ✓ Memo created")

            # Save memo to file
            output_path = Path("output") / f"{ticker}_memo.md"
            output_path.parent.mkdir(exist_ok=True)
            output_path.write_text(self.maa.to_markdown(memo))
            print(f"  ✓ Saved to: {output_path}")

        except NotImplementedError:
            print("  ⚠️  MAA not yet implemented")
            return {"error": "MAA not implemented"}

        print("\n" + "=" * 60)
        print(f"🎯 Final Decision: {pa_output.decision}")
        print("=" * 60)

        return {
            "ticker": ticker,
            "dqa": dqa_output,
            "va": va_output,
            "da": da_output,
            "pa": pa_output,
            "memo": memo
        }


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Warren AI - Buffett-style Investment Analysis"
    )
    parser.add_argument(
        "--ticker",
        type=str,
        required=True,
        help="Stock ticker symbol (e.g., AAPL)"
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        help="Path to configuration directory"
    )

    args = parser.parse_args()

    orchestrator = WarrenOrchestrator(config_dir=args.config_dir)

    # TODO: Fetch financial data for ticker
    # For now, using placeholder
    financial_data = {}
    current_price = 0.0

    results = orchestrator.analyze_stock(
        ticker=args.ticker,
        financial_data=financial_data,
        current_price=current_price
    )

    if "error" in results:
        print(f"\n❌ Analysis incomplete: {results['error']}")
        print("\n💡 Next steps: Implement agent analysis methods")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
