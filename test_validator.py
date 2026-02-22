"""
Test the Validator Agent
"""

from agents.validator_agent import ValidatorAgent

# Load sample PRD
with open('examples/sample_prd.md', 'r', encoding='utf-8') as f:
    prd_text = f.read()

# Initialize agent
agent = ValidatorAgent('templates/prd_template.yaml')

# Run validation
results, score = agent.validate(prd_text)

# Format report
report = agent.format_report(results, score)

# Print results
print("=" * 60)
print("VALIDATOR AGENT TEST")
print("=" * 60)
print(f"\nOverall Score: {report['score']}/100 {report['status_emoji']}")
print(f"Status: {report['status']}")
print(f"\nSections Found: {report['found_count']}/{report['total_sections']}")

if report['missing_critical']:
    print(f"\n🔴 Critical Missing ({len(report['missing_critical'])}):")
    for section in report['missing_critical']:
        print(f"  • {section}")

if report['missing_high']:
    print(f"\n🟡 High Priority Missing ({len(report['missing_high'])}):")
    for section in report['missing_high']:
        print(f"  • {section}")

if report['found_sections']:
    print(f"\n✅ Found Sections:")
    for section in report['found_sections'][:5]:
        print(f"  • {section}")
    if len(report['found_sections']) > 5:
        print(f"  ... and {len(report['found_sections']) - 5} more")

print("\n" + "=" * 60)
print("✅ Validator Agent Working!")
print("=" * 60)