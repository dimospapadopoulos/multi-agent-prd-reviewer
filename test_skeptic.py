"""
Test the Skeptic Agent
"""
# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()  # This loads .env file

from agents.validator_agent import ValidatorAgent
from agents.skeptic_agent import SkepticAgent

# Load sample PRD
with open('examples/sample_prd.md', 'r', encoding='utf-8') as f:
    prd_text = f.read()

# Agent 1: Validate
print("🔍 Running Validator Agent...")
validator = ValidatorAgent('templates/prd_template.yaml')
results, score = validator.validate(prd_text)
validation_report = validator.format_report(results, score)

print(f"✅ Validation Complete: {score}/100\n")

# Agent 2: Challenge
print("🤔 Running Skeptic Agent...")
skeptic = SkepticAgent()
critique = skeptic.challenge(prd_text, validation_report)

# Display results
print("=" * 80)
print("TECHNICAL CRITIQUE FROM SKEPTICAL TECH LEAD")
print("=" * 80)
print(critique['critique'])
print("\n" + "=" * 80)
print(f"📊 Tokens Used: {critique['total_tokens']} (Input: {critique['prompt_tokens']}, Output: {critique['completion_tokens']})")
print(f"🤖 Model: {critique['model']}")
print("=" * 80)