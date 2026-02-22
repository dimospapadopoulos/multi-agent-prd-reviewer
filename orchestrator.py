"""
Multi-Agent PRD Reviewer Orchestrator
Coordinates Validator and Skeptic agents to produce comprehensive PRD review
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

from agents.validator_agent import ValidatorAgent
from agents.skeptic_agent import SkepticAgent

# Load environment variables
load_dotenv()


class PRDReviewOrchestrator:
    """
    Orchestrates multi-agent PRD review process
    
    Coordinates:
    1. Validator Agent - checks completeness
    2. Skeptic Agent - challenges assumptions and feasibility
    3. Synthesizes results into comprehensive review
    """
    
    def __init__(self, template_path: str = "templates/prd_template.yaml"):
        """
        Initialize orchestrator with agents
        
        Args:
            template_path: Path to PRD validation template
        """
        self.validator = ValidatorAgent(template_path)
        self.skeptic = SkepticAgent()
        
    def review_prd(self, prd_text: str, prd_name: str = "Untitled PRD") -> dict:
        """
        Run complete multi-agent review of PRD
        
        Args:
            prd_text: Full PRD text to review
            prd_name: Name/title of the PRD
            
        Returns:
            Dictionary with complete review results
        """
        print(f"\n{'='*80}")
        print(f"🤖 MULTI-AGENT PRD REVIEW: {prd_name}")
        print(f"{'='*80}\n")
        
        # Step 1: Validation Agent
        print("📋 Step 1/2: Running Validator Agent...")
        validation_results, score = self.validator.validate(prd_text)
        validation_report = self.validator.format_report(validation_results, score)
        print(f"   ✅ Validation Complete: {score}/100 {validation_report['status_emoji']}")
        
        # Step 2: Skeptic Agent
        print("\n🤔 Step 2/2: Running Skeptical Tech Lead Agent...")
        critique = self.skeptic.challenge(prd_text, validation_report)
        print(f"   ✅ Critique Complete ({critique['total_tokens']} tokens)")
        
        # Compile final review
        review = {
            "prd_name": prd_name,
            "timestamp": datetime.now().isoformat(),
            "validation": validation_report,
            "technical_critique": critique['critique'],
            "summary": self._generate_summary(validation_report, critique),
            "metadata": {
                "validator_score": score,
                "validator_status": validation_report['status'],
                "skeptic_tokens": critique['total_tokens'],
                "model_used": critique['model']
            }
        }
        
        return review
    
    def _generate_summary(self, validation_report: dict, critique: dict) -> dict:
        """
        Generate executive summary combining both agents' findings
        
        Args:
            validation_report: Results from validator
            critique: Results from skeptic
            
        Returns:
            Dictionary with summary insights
        """
        score = validation_report['score']
        missing_critical = len(validation_report['missing_critical'])
        missing_high = len(validation_report['missing_high'])
        
        # Determine overall readiness
        if score >= 90 and missing_critical == 0:
            overall_status = "READY FOR ENGINEERING REVIEW"
            recommendation = "PRD meets quality standards. Address technical questions before kickoff."
        elif score >= 70:
            overall_status = "NEEDS ITERATION"
            recommendation = "Address missing sections and technical concerns before engineering review."
        else:
            overall_status = "NOT READY"
            recommendation = "Significant gaps in completeness and technical clarity. Requires substantial work."
        
        return {
            "overall_status": overall_status,
            "recommendation": recommendation,
            "completeness_score": score,
            "critical_gaps": missing_critical,
            "high_priority_gaps": missing_high,
            "key_insight": "Multi-agent review complete. See detailed validation and technical critique below."
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
            # Auto-generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = review['prd_name'].replace(' ', '_').replace('/', '-')
            output_path = f"output/{safe_name}_{timestamp}.json"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(review, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def print_review(self, review: dict):
        """
        Pretty print review to console
        
        Args:
            review: Review dictionary
        """
        print(f"\n{'='*80}")
        print(f"📊 FINAL REVIEW: {review['prd_name']}")
        print(f"{'='*80}\n")
        
        # Summary
        summary = review['summary']
        print(f"**OVERALL STATUS:** {summary['overall_status']}")
        print(f"**COMPLETENESS:** {summary['completeness_score']}/100")
        print(f"**RECOMMENDATION:** {summary['recommendation']}\n")
        
        # Validation results
        validation = review['validation']
        print(f"{'─'*80}")
        print("📋 VALIDATION RESULTS")
        print(f"{'─'*80}")
        print(f"Score: {validation['score']}/100 {validation['status_emoji']}")
        print(f"Status: {validation['status']}\n")
        
        if validation['missing_critical']:
            print(f"🔴 Critical Missing ({len(validation['missing_critical'])}):")
            for section in validation['missing_critical']:
                print(f"   • {section}")
            print()
        
        if validation['missing_high']:
            print(f"🟡 High Priority Missing ({len(validation['missing_high'])}):")
            for section in validation['missing_high']:
                print(f"   • {section}")
            print()
        
        print(f"✅ Found: {validation['found_count']}/{validation['total_sections']} sections\n")
        
        # Technical critique
        print(f"{'─'*80}")
        print("🤔 TECHNICAL CRITIQUE")
        print(f"{'─'*80}")
        print(review['technical_critique'])
        print()
        
        # Metadata
        print(f"{'─'*80}")
        print(f"📊 Review Metadata")
        print(f"{'─'*80}")
        print(f"Timestamp: {review['timestamp']}")
        print(f"Model: {review['metadata']['model_used']}")
        print(f"Tokens: {review['metadata']['skeptic_tokens']}")
        print(f"{'='*80}\n")


def main():
    """
    Main CLI interface for multi-agent PRD reviewer
    """
    import sys
    
    # Check for PRD file argument
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <prd_file.md>")
        print("\nExample:")
        print("  python orchestrator.py examples/sample_prd.md")
        sys.exit(1)
    
    prd_file = sys.argv[1]
    
    # Load PRD
    try:
        with open(prd_file, 'r', encoding='utf-8') as f:
            prd_text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {prd_file}")
        sys.exit(1)
    
    # Extract PRD name from first heading
    first_line = prd_text.split('\n')[0].strip()
    if first_line.startswith('#'):
        prd_name = first_line.lstrip('#').strip()
    else:
        prd_name = os.path.basename(prd_file).replace('.md', '')
    
    # Run review
    orchestrator = PRDReviewOrchestrator()
    review = orchestrator.review_prd(prd_text, prd_name)
    
    # Display results
    orchestrator.print_review(review)
    
    # Save to file
    output_path = orchestrator.save_review(review)
    print(f"💾 Review saved to: {output_path}\n")


if __name__ == "__main__":
    main()