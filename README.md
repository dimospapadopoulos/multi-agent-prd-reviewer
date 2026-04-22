# Multi-Agent PRD Reviewer

AI-powered system that uses four specialised agents to review Product Requirement Documents, combining rule-based validation with AI-driven technical, UX, and legal critique.

## The Problem

PRD quality varies wildly across teams. Manual reviews are:
- Time-consuming (30+ minutes per PRD)
- Inconsistent (depends on reviewer's expertise)
- Often miss edge cases, UX gaps, or compliance risks
- Don't scale across 10+ product managers

## The Solution

A multi-agent AI system where specialised agents collaborate to review PRDs in sequence, each building on the context of the agents before it:

**Agent 1: Validator** - Rules-based completeness checker
- Validates PRD against 12 quality standards
- Scores 0-100 based on weighted sections
- Flags missing critical, high, and medium sections

**Agent 2: Skeptical Tech Lead** - AI-driven technical challenger
- Challenges assumptions with domain expertise
- Identifies hidden complexity and feasibility risks
- Probes edge cases, scale, and operational concerns
- Asks tough questions PMs often miss

**Agent 3: UX and Design Reviewer** - AI-driven experience critic
- Reviews user flows and identifies missing UI states (loading, error, empty, success, offline)
- Flags accessibility gaps (WCAG 2.1 AA)
- Challenges design system consistency and mobile experience
- Surfaces conversion and usability risks

**Agent 4: Legal and Compliance Reviewer** - AI-driven compliance auditor
- Surfaces GDPR, PCI DSS, and SCA obligations
- Flags consumer protection and market-specific regulatory gaps
- Identifies missing audit trail and data retention requirements
- Recommends legal sign-off needed before build

**Orchestrator** - Coordinates agents and synthesises results
- Runs agents sequentially, passing accumulated context forward
- Combines findings into a comprehensive multi-layer review
- Provides overall recommendation and saves structured output

## Real-World Impact

**Before:**
- 30-minute manual PRD review
- Inconsistent quality across the team
- Technical, UX, and legal gaps discovered during build (costly)

**After:**
- ~60-second automated four-layer review
- Consistent quality standards across all PRDs
- Risks surfaced before engineering (savings: 2+ weeks rework per issue caught)

**Example finding:**
> PRD assumed "Apple Pay is trusted" without a contingency plan. Skeptic agent asked: "What happens when Apple deprecates this API? What's our migration path?" Caught critical gap pre-engineering.

## Architecture
```
User submits PRD
    ↓
Agent 1: Validator
    - Validates completeness (12 sections)
    - Scores 0-100
    - Identifies missing sections by severity
    ↓
Agent 2: Skeptical Tech Lead
    - Reviews PRD + validation results
    - Challenges assumptions and feasibility
    - Identifies technical risks and edge cases
    ↓
Agent 3: UX and Design Reviewer
    - Reviews PRD + validation + technical critique
    - Surfaces missing UI states and flow gaps
    - Flags accessibility and design system risks
    ↓
Agent 4: Legal and Compliance Reviewer
    - Reviews PRD + all prior critiques
    - Identifies GDPR, PCI DSS, and regulatory gaps
    - Recommends legal sign-off requirements
    ↓
Orchestrator
    - Synthesises findings from all four agents
    - Generates overall recommendation
    - Saves structured output (JSON + console)
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
# Edit .env — add ANTHROPIC_API_KEY and (optionally) Slack tokens
```

## Usage

### Option A: CLI
```bash
# Review a PRD file directly
python orchestrator.py examples/sample_prd.md

# Review your own PRD
python orchestrator.py path/to/your_prd.md
```

**Console:** Pretty-printed review with all four critiques  
**File:** JSON saved to `output/` with complete structured data and per-agent token usage

---

### Option B: Slack Bot

The Slack bot runs the same four-agent pipeline and posts the results as formatted Block Kit messages directly into the channel.

**Two ways to submit a PRD:**
1. **Slash command** — type `/review-prd` in any channel → paste PRD name and text into the modal → submit
2. **File upload** — share any `.md` file in a channel where the bot is present → review runs automatically

**Setup:**

#### 1. Create a Slack App
1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Name it `PRD Reviewer` and pick your workspace

#### 2. Configure OAuth scopes
In **OAuth & Permissions → Scopes → Bot Token Scopes**, add:
| Scope | Purpose |
|---|---|
| `chat:write` | Post review results |
| `commands` | Register `/review-prd` |
| `files:read` | Download uploaded `.md` files |

#### 3. Enable Socket Mode
In **Socket Mode**, toggle it on and create an **App-Level Token** with `connections:write` scope.  
Copy the `xapp-...` token → `SLACK_APP_TOKEN` in your `.env`.

#### 4. Add the slash command
In **Slash Commands** → **Create New Command**:
- Command: `/review-prd`
- Request URL: *(any placeholder — Socket Mode ignores this)*
- Description: `Run 4-agent PRD review`

#### 5. Subscribe to events
In **Event Subscriptions**, enable events and subscribe to **Bot Events**:
- `file_shared`

#### 6. Install the app and copy tokens
**Install App** → copy the `xoxb-...` **Bot User OAuth Token** → `SLACK_BOT_TOKEN` in your `.env`.

#### 7. Run the bot
```bash
python slack_bot.py
```

The bot connects over a persistent WebSocket — no public URL required.

### Example Output
```
================================================================================
MULTI-AGENT PRD REVIEW: Apple Pay Integration
================================================================================

Step 1/4: Running Validator Agent...
   Validation complete: 79/100 ⚠️

Step 2/4: Running Skeptical Tech Lead Agent...
   Technical critique complete (1247 tokens)

Step 3/4: Running UX and Design Reviewer Agent...
   UX critique complete (1183 tokens)

Step 4/4: Running Legal and Compliance Reviewer Agent...
   Legal critique complete (1091 tokens)

================================================================================
FINAL REVIEW: Apple Pay Integration
================================================================================

**OVERALL STATUS:** NEEDS ITERATION
**COMPLETENESS:** 79/100
**RECOMMENDATION:** Address missing sections and resolve technical, UX, and
compliance concerns before engineering review.

────────────────────────────────────────────────────────────────────────────────
VALIDATION RESULTS
────────────────────────────────────────────────────────────────────────────────
Score: 79/100 ⚠️
Status: NEEDS IMPROVEMENT

High Priority Missing (1):
   - Open Questions

Found: 11/12 sections

────────────────────────────────────────────────────────────────────────────────
TECHNICAL CRITIQUE (Agent 2)
────────────────────────────────────────────────────────────────────────────────
[Detailed AI-generated critique challenging assumptions, identifying risks...]

────────────────────────────────────────────────────────────────────────────────
UX AND DESIGN CRITIQUE (Agent 3)
────────────────────────────────────────────────────────────────────────────────
[Missing UI states, accessibility gaps, flow issues...]

────────────────────────────────────────────────────────────────────────────────
LEGAL AND COMPLIANCE CRITIQUE (Agent 4)
────────────────────────────────────────────────────────────────────────────────
[GDPR, PCI DSS, SCA, consumer protection obligations...]
```

## Project Structure
```
multi-agent-prd-reviewer/
├── orchestrator.py               # Main CLI and coordination logic
├── slack_bot.py                  # Slack bot (slash command + file upload)
├── agents/
│   ├── validator_agent.py        # Rule-based completeness validator
│   ├── skeptic_agent.py          # AI-powered technical challenger
│   ├── ux_agent.py               # AI-powered UX and design reviewer
│   └── legal_agent.py            # AI-powered legal and compliance reviewer
├── prompts/
│   ├── skeptic_system.txt        # System prompt: tech lead expertise
│   ├── ux_system.txt             # System prompt: UX designer expertise
│   └── legal_system.txt          # System prompt: legal and compliance expertise
├── utils/
│   └── slack_formatter.py        # Converts review dict → Slack Block Kit blocks
├── templates/
│   └── prd_template.yaml         # Quality standards and scoring weights
├── examples/
│   └── sample_prd.md             # Example PRD for testing
├── output/                       # Review results (JSON)
├── requirements.txt
└── README.md
```

## Customization

### Modify Quality Standards

Edit `templates/prd_template.yaml` to customise:
- Required sections
- Severity levels (critical, high, medium)
- Keyword detection rules
- Scoring weights

### Adjust Agent Personas

Each agent has a dedicated system prompt in `prompts/`:
- `skeptic_system.txt` — domain expertise, question focus areas, critique tone
- `ux_system.txt` — UX principles, design system conventions, accessibility standards
- `legal_system.txt` — applicable regulations, markets, compliance thresholds

### Add More Agents

Extend `orchestrator.py` to add further specialists:
- Agent 5: Competitive Analyst (market positioning)
- Agent 6: Data and Analytics Reviewer (instrumentation gaps)
- Agent 7: Accessibility Auditor (deep WCAG review)

## What I Learned

**Multi-Agent Architecture:**
- Agent specialisation vs generalisation tradeoffs
- Passing accumulated context between agents without redundancy
- Prompt engineering to make agents complement rather than repeat each other
- Orchestration patterns for sequential vs parallel agents

**Prompt Engineering:**
- System prompts that encode deep domain expertise
- Context management across a four-agent chain
- Output formatting for structured, layered critique
- Balancing specificity with flexibility across different PRD types

**Production Considerations:**
- Token usage optimisation (avg ~3,500 tokens per full review)
- Error handling for API calls
- Structured output for downstream use (Slack, Confluence)
- CLI design for team adoption

**Business Impact:**
- Encoding PM, tech lead, UX, and legal judgment into autonomous agents
- Scaling multi-disciplinary expertise across teams
- Catching issues pre-build (10x cost savings vs post-build rework)
- Creating institutional knowledge that survives team turnover

## Future Enhancements

- [ ] Batch processing (review 10+ PRDs at once)
- [ ] Historical tracking (how has PRD quality improved over time?)
- [ ] Team leaderboard (gamify quality standards)
- [ ] Custom agent personalities per team/domain
- [ ] Integration with Confluence/Notion
- [ ] PDF report generation
- [ ] Agent 5: Competitive Analyst

## Related Projects

- **[PRD Validator CLI](https://github.com/dimospapadopoulos/prd-completeness-validator)** - V1 of validation logic
- **[PRD Validator Slack Bot](https://github.com/dimospapadopoulos/prd-validator-slack)** - V2 with Slack integration
- **[Voice of Customer Synthesizer](https://github.com/dimospapadopoulos/voc-portfolio-clean)** - Customer feedback automation
- **[Custom PM Skills](https://github.com/dimospapadopoulos/custom-pm-skills)** - Claude AI skills library

## Tech Stack

- **Python 3.11**
- **Anthropic Claude API** (Claude Sonnet 4.6)
- **YAML** for template configuration
- **JSON** for structured output

---

**Built by:** Dimos Papadopoulos  
**Role:** Product Leader  
**Why:** To scale PM expertise through autonomous AI agents  
**License:** BSD-3
