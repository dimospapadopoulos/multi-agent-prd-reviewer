# Multi-Agent PRD Reviewer

AI-powered system that uses multiple specialized agents to review Product Requirement Documents, combining rule-based validation with AI-driven technical critique.

## The Problem

PRD quality varies wildly across teams. Manual reviews are:
- Time-consuming (30+ minutes per PRD)
- Inconsistent (depends on reviewer's expertise)
- Often miss edge cases or technical risks
- Don't scale across 10+ product managers

## The Solution

A multi-agent AI system where specialized agents collaborate to review PRDs:

**Agent 1: Validator** - Rules-based completeness checker
- Validates PRD against 12 quality standards
- Scores 0-100 based on weighted sections
- Flags missing critical sections

**Agent 2: Skeptical Tech Lead** - AI-driven technical challenger  
- Challenges assumptions with domain expertise
- Identifies hidden complexity and risks
- Probes feasibility and edge cases
- Asks tough questions PMs often miss

**Orchestrator** - Coordinates agents and synthesizes results
- Runs agents in sequence
- Combines findings into comprehensive review
- Provides overall recommendation
- Saves structured output

## Real-World Impact

**Before:**
- 30-minute manual PRD review
- Inconsistent quality across team
- Technical gaps discovered during build (costly)

**After:**
- 30-second automated review
- Consistent quality standards
- Risks surfaced before engineering (savings: 2+ weeks rework per issue)

**Example finding:**
> PRD assumed "Apple Pay is trusted" without contingency plan. Skeptic agent asked: "What happens when Apple deprecates this API? What's our migration path?" Caught critical gap pre-engineering.

## Architecture
```
User submits PRD
    ↓
Agent 1: Validator
    - Validates completeness (12 sections)
    - Scores 0-100
    - Identifies gaps
    ↓
Agent 2: Skeptical Tech Lead
    - Reviews PRD + validation results
    - Challenges assumptions
    - Questions feasibility
    - Identifies risks
    ↓
Orchestrator
    - Synthesizes findings
    - Generates recommendation
    - Saves structured output
    ↓
Final Review (JSON + Console)
```

## Installation
```bash
# Clone repository
git clone https://github.com/dimospapadopoulos/multi-agent-prd-reviewer.git
cd multi-agent-prd-reviewer

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

### CLI Interface
```bash
# Review a PRD
python orchestrator.py examples/sample_prd.md

# Review your own PRD
python orchestrator.py path/to/your_prd.md
```

### Output

**Console:** Pretty-printed review with validation results and technical critique

**File:** JSON saved to `output/` with complete structured data

### Example Output
```
================================================================================
🤖 MULTI-AGENT PRD REVIEW: Apple Pay Integration
================================================================================

📋 Step 1/2: Running Validator Agent...
   ✅ Validation Complete: 79/100 ⚠️

🤔 Step 2/2: Running Skeptical Tech Lead Agent...
   ✅ Critique Complete (1247 tokens)

================================================================================
📊 FINAL REVIEW: Apple Pay Integration
================================================================================

**OVERALL STATUS:** NEEDS ITERATION
**COMPLETENESS:** 79/100
**RECOMMENDATION:** Address missing sections and technical concerns before engineering review.

────────────────────────────────────────────────────────────────────────────────
📋 VALIDATION RESULTS
────────────────────────────────────────────────────────────────────────────────
Score: 79/100 ⚠️
Status: NEEDS IMPROVEMENT

🟡 High Priority Missing (1):
   • Open Questions

✅ Found: 11/12 sections

────────────────────────────────────────────────────────────────────────────────
🤔 TECHNICAL CRITIQUE
────────────────────────────────────────────────────────────────────────────────
[Detailed AI-generated critique challenging assumptions, identifying risks, etc.]
```

## Project Structure
```
multi-agent-prd-reviewer/
├── orchestrator.py           # Main CLI and coordination logic
├── agents/
│   ├── validator_agent.py    # Rule-based completeness validator
│   └── skeptic_agent.py      # AI-powered technical challenger
├── prompts/
│   └── skeptic_system.txt    # System prompt encoding tech lead expertise
├── templates/
│   └── prd_template.yaml     # Quality standards and scoring weights
├── examples/
│   └── sample_prd.md         # Example PRD for testing
├── output/                   # Review results (JSON)
├── requirements.txt
└── README.md
```

## Customization

### Modify Quality Standards

Edit `templates/prd_template.yaml` to customize:
- Required sections
- Severity levels (critical, high, medium)
- Keyword detection rules
- Scoring weights

### Adjust Tech Lead Persona

Edit `prompts/skeptic_system.txt` to change:
- Domain expertise (payments, infrastructure, etc.)
- Question focus areas
- Critique style and tone
- Output format

### Add More Agents

Extend `orchestrator.py` to add:
- Agent 3: Design Reviewer (UX considerations)
- Agent 4: Compliance Checker (GDPR, PCI, etc.)
- Agent 5: Competitive Analyst (market positioning)

## What I Learned

**Multi-Agent Architecture:**
- Agent specialization vs generalization tradeoffs
- Passing context between agents (structured data)
- Prompt engineering for different agent personas
- Orchestration patterns for sequential vs parallel agents

**Prompt Engineering:**
- System prompts that encode domain expertise
- Context management (PRD + validation results)
- Output formatting for structured critique
- Balancing specificity vs flexibility

**Production Considerations:**
- Token usage optimization (avg 1200 tokens/review)
- Error handling for API calls
- Structured output for downstream use
- CLI design for team adoption

**Business Impact:**
- Encoding PM judgment into autonomous systems
- Scaling expertise across teams
- Catching issues pre-build (10x cost savings)
- Creating institutional knowledge that survives turnover

## Future Enhancements

- [ ] Slack bot integration (like PRD Validator v2)
- [ ] Batch processing (review 10+ PRDs at once)
- [ ] Historical tracking (how has quality improved over time?)
- [ ] Team leaderboard (gamify quality)
- [ ] Custom agent personalities per team/domain
- [ ] Integration with Confluence/Notion
- [ ] PDF report generation
- [ ] Agent 3: Design reviewer for UX considerations

## Related Projects

- **[PRD Validator CLI](https://github.com/dimospapadopoulos/prd-completeness-validator)** - V1 of validation logic
- **[PRD Validator Slack Bot](https://github.com/dimospapadopoulos/prd-validator-slack)** - V2 with Slack integration
- **[Voice of Customer Synthesizer](https://github.com/dimospapadopoulos/voc-portfolio-clean)** - Customer feedback automation
- **[Custom PM Skills](https://github.com/dimospapadopoulos/custom-pm-skills)** - Claude AI skills library

## Tech Stack

- **Python 3.11**
- **Anthropic Claude API** (Sonnet 4.5 / until 4.6 becomes available for pulling through the API)
- **YAML** for template configuration
- **JSON** for structured output

---

**Built by:** Dimos Papadopoulos  
**Role:** Product Leader 
**Why:** To scale PM expertise through autonomous AI agents  
**License:** BSD-3