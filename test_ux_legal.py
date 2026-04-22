"""
Integration test for Agent 3 (UXAgent) and Agent 4 (LegalAgent)
Runs the full four-agent pipeline against the sample PRD
"""

from dotenv import load_dotenv
load_dotenv()

from agents.validator_agent import ValidatorAgent
from agents.skeptic_agent import SkepticAgent
from agents.ux_agent import UXAgent
from agents.legal_agent import LegalAgent

with open('examples/sample_prd.md', 'r', encoding='utf-8') as f:
    prd_text = f.read()

# Agent 1: Validate
print("Step 1/4: Running Validator Agent...")
validator = ValidatorAgent('templates/prd_template.yaml')
results, score = validator.validate(prd_text)
validation_report = validator.format_report(results, score)
print(f"   Validation complete: {score}/100\n")

# Agent 2: Technical critique
print("Step 2/4: Running Skeptic Agent...")
skeptic = SkepticAgent()
skeptic_result = skeptic.challenge(prd_text, validation_report)
print(f"   Technical critique complete ({skeptic_result['total_tokens']} tokens)\n")

# Agent 3: UX critique
print("Step 3/4: Running UX and Design Reviewer Agent...")
ux_agent = UXAgent()
ux_result = ux_agent.review(prd_text, validation_report, skeptic_result['critique'])
print(f"   UX critique complete ({ux_result['total_tokens']} tokens)\n")

# Agent 4: Legal critique
print("Step 4/4: Running Legal and Compliance Reviewer Agent...")
legal_agent = LegalAgent()
legal_result = legal_agent.review(
    prd_text,
    validation_report,
    skeptic_result['critique'],
    ux_result['critique']
)
print(f"   Legal critique complete ({legal_result['total_tokens']} tokens)\n")

# Print results
print("=" * 80)
print("UX AND DESIGN CRITIQUE (Agent 3)")
print("=" * 80)
print(ux_result['critique'])

print("\n" + "=" * 80)
print("LEGAL AND COMPLIANCE CRITIQUE (Agent 4)")
print("=" * 80)
print(legal_result['critique'])

total = skeptic_result['total_tokens'] + ux_result['total_tokens'] + legal_result['total_tokens']
print(f"\n{'='*80}")
print(f"Total tokens across all AI agents: {total}")
print(f"Model: {ux_result['model']}")
print("=" * 80)
