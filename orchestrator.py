"""
Multi-Agent PRD Reviewer Orchestrator
Coordinates four specialised agents to produce a comprehensive PRD review
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

from agents.validator_agent import ValidatorAgent
from agents.skeptic_agent import SkepticAgent
from agents.ux_agent import UXAgent
from agents.legal_agent import LegalAgent

load_dotenv()


class PRDReviewOrchestrator:
    """
    Orchestrates the four-agent PRD review pipeline

    Sequential pipeline:
    1. Validator Agent      - rules-based completeness check
    2. Skeptic Agent        - technical assumptions and feasibility challenge
    3. UX Agent             - UX flows, states, and design system review
    4. Legal Agent          - compliance, data privacy, and regulatory gaps
    5. Synthesises results  - overall recommendation and structured output
    """

    def __init__(self, template_path: str = "templates/prd_template.yaml"):
        self.validator = ValidatorAgent(template_path)
        self.skeptic = SkepticAgent()
        self.ux_reviewer = UXAgent()
        self.legal_reviewer = LegalAgent()

    def review_prd(self, prd_text: str, prd_name: str = "Untitled PRD") -> dict:
        """
        Run complete four-agent review of a PRD

        Args:
            prd_text: Full PRD text to review
            prd_name: Name/title of the PRD

        Returns:
            Dictionary with complete review results from all agents
        """
        print(f"\n{'='*80}")
        print(f"MULTI-AGENT PRD REVIEW: {prd_name}")
        print(f"{'='*80}\n")

        # Step 1: Validator Agent
        print("Step 1/4: Running Validator Agent...")
        validation_results, score = self.validator.validate(prd_text)
        validation_report = self.validator.format_report(validation_results, score)
        print(f"   Validation complete: {score}/100 {validation_report['status_emoji']}")

        # Step 2: Skeptic Agent
        print("\nStep 2/4: Running Skeptical Tech Lead Agent...")
        skeptic_result = self.skeptic.challenge(prd_text, validation_report)
        print(f"   Technical critique complete ({skeptic_result['total_tokens']} tokens)")

        # Step 3: UX Agent
        print("\nStep 3/4: Running UX and Design Reviewer Agent...")
        ux_result = self.ux_reviewer.review(
            prd_text,
            validation_report,
            skeptic_result['critique']
        )
        print(f"   UX critique complete ({ux_result['total_tokens']} tokens)")

        # Step 4: Legal Agent
        print("\nStep 4/4: Running Legal and Compliance Reviewer Agent...")
        legal_result = self.legal_reviewer.review(
            prd_text,
            validation_report,
            skeptic_result['critique'],
            ux_result['critique']
        )
        print(f"   Legal critique complete ({legal_result['total_tokens']} tokens)")

        # Compile final review
        total_tokens = (
            skeptic_result['total_tokens']
            + ux_result['total_tokens']
            + legal_result['total_tokens']
        )

        review = {
            "prd_name": prd_name,
            "timestamp": datetime.now().isoformat(),
            "validation": validation_report,
            "technical_critique": skeptic_result['critique'],
            "ux_critique": ux_result['critique'],
            "legal_critique": legal_result['critique'],
            "summary": self._generate_summary(validation_report, skeptic_result),
            "metadata": {
                "validator_score": score,
                "validator_status": validation_report['status'],
                "total_tokens": total_tokens,
                "skeptic_tokens": skeptic_result['total_tokens'],
                "ux_tokens": ux_result['total_tokens'],
                "legal_tokens": legal_result['total_tokens'],
                "model_used": skeptic_result['model'],
                "agents_run": 4
            }
        }

        return review

    def _generate_summary(self, validation_report: dict, critique: dict) -> dict:
        """
        Generate executive summary combining all agents' findings

        Args:
            validation_report: Results from ValidatorAgent
            critique: Results from SkepticAgent

        Returns:
            Dictionary with summary insights
        """
        score = validation_report['score']
        missing_critical = len(validation_report['missing_critical'])
        missing_high = len(validation_report['missing_high'])

        if score >= 90 and missing_critical == 0:
            overall_status = "READY FOR ENGINEERING REVIEW"
            recommendation = (
                "PRD meets quality standards. Address open technical, UX, "
                "and compliance questions before kickoff."
            )
        elif score >= 70:
            overall_status = "NEEDS ITERATION"
            recommendation = (
                "Address missing sections and resolve technical, UX, and compliance "
                "concerns before engineering review."
            )
        else:
            overall_status = "NOT READY"
            recommendation = (
                "Significant gaps in completeness, technical clarity, UX, and/or "
                "compliance. Requires substantial work before engineering review."
            )

        return {
            "overall_status": overall_status,
            "recommendation": recommendation,
            "completeness_score": score,
            "critical_gaps": missing_critical,
            "high_priority_gaps": missing_high,
            "key_insight": (
                "Four-agent review complete. See detailed validation, technical, "
                "UX, and legal critiques below."
            )
        }

    def save_review(self, review: dict, output_path: str = None) -> str:
        """
        Save review to file

        Args:
            review: Review dictionary
            output_path: Where to save (auto-generated if not provided)

        Returns:
            Path where review was saved
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = review['prd_name'].replace(' ', '_').replace('/', '-')
            output_path = f"output/{safe_name}_{timestamp}.json"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(review, f, indent=2, ensure_ascii=False)

        return output_path

    def print_review(self, review: dict):
        """
        Pretty-print review to console

        Args:
            review: Review dictionary
        """
        print(f"\n{'='*80}")
        print(f"FINAL REVIEW: {review['prd_name']}")
        print(f"{'='*80}\n")

        summary = review['summary']
        print(f"**OVERALL STATUS:** {summary['overall_status']}")
        print(f"**COMPLETENESS:** {summary['completeness_score']}/100")
        print(f"**RECOMMENDATION:** {summary['recommendation']}\n")

        # Validation results
        validation = review['validation']
        print(f"{'─'*80}")
        print("VALIDATION RESULTS")
        print(f"{'─'*80}")
        print(f"Score: {validation['score']}/100 {validation['status_emoji']}")
        print(f"Status: {validation['status']}\n")

        if validation['missing_critical']:
            print(f"Critical Missing ({len(validation['missing_critical'])}):")
            for section in validation['missing_critical']:
                print(f"   - {section}")
            print()

        if validation['missing_high']:
            print(f"High Priority Missing ({len(validation['missing_high'])}):")
            for section in validation['missing_high']:
                print(f"   - {section}")
            print()

        print(f"Found: {validation['found_count']}/{validation['total_sections']} sections\n")

        # Technical critique
        print(f"{'─'*80}")
        print("TECHNICAL CRITIQUE (Agent 2)")
        print(f"{'─'*80}")
        print(review['technical_critique'])
        print()

        # UX critique
        print(f"{'─'*80}")
        print("UX AND DESIGN CRITIQUE (Agent 3)")
        print(f"{'─'*80}")
        print(review['ux_critique'])
        print()

        # Legal critique
        print(f"{'─'*80}")
        print("LEGAL AND COMPLIANCE CRITIQUE (Agent 4)")
        print(f"{'─'*80}")
        print(review['legal_critique'])
        print()

        # Metadata
        meta = review['metadata']
        print(f"{'─'*80}")
        print("Review Metadata")
        print(f"{'─'*80}")
        print(f"Timestamp:    {review['timestamp']}")
        print(f"Model:        {meta['model_used']}")
        print(f"Agents run:   {meta['agents_run']}")
        print(f"Total tokens: {meta['total_tokens']} "
              f"(tech: {meta['skeptic_tokens']}, "
              f"ux: {meta['ux_tokens']}, "
              f"legal: {meta['legal_tokens']})")
        print(f"{'='*80}\n")


def main():
    """
    Main CLI interface for multi-agent PRD reviewer
    """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <prd_file.md>")
        print("\nExample:")
        print("  python orchestrator.py examples/sample_prd.md")
        sys.exit(1)

    prd_file = sys.argv[1]

    try:
        with open(prd_file, 'r', encoding='utf-8') as f:
            prd_text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {prd_file}")
        sys.exit(1)

    first_line = prd_text.split('\n')[0].strip()
    if first_line.startswith('#'):
        prd_name = first_line.lstrip('#').strip()
    else:
        prd_name = os.path.basename(prd_file).replace('.md', '')

    orchestrator = PRDReviewOrchestrator()
    review = orchestrator.review_prd(prd_text, prd_name)

    orchestrator.print_review(review)

    output_path = orchestrator.save_review(review)
    print(f"Review saved to: {output_path}\n")


if __name__ == "__main__":
    main()
