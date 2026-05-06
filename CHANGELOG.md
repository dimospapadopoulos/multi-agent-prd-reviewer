# Changelog

All notable changes to the Multi-Agent PRD Reviewer are documented here.

---

## [v5.1] — 2026-05-06

### Fixed
- **Triple-firing of Slack pipeline** — `file_shared` dispatches once per channel the file appears in; if the bot is present in multiple channels, or if Slack retries after a slow ACK, the same `file_id` could arrive several times and spawn parallel pipeline runs. Fixed with a thread-safe file-ID deduplication registry (`_claim_file`) with a 120-second TTL window.

### Added
- **Word document support (.docx)** — PMs can now upload Word PRDs directly; text is extracted via `python-docx`.
- **Google Docs guidance** — when a Google Doc is shared via Slack's Drive integration, the bot detects the `gdoc` filetype and replies with clear export instructions (export as PDF or paste via `/review-prd`). Google Docs require Google Workspace auth and cannot be downloaded with a bot token.
- **Legacy .doc guidance** — `.doc` (old binary Word format) requires system-level tooling outside the scope of this bot; the bot detects it and prompts the PM to save as `.docx` or export as PDF.

---

## [v5.0] — 2026-05-05

### Added
- **Slack bot** (`slack_bot.py`) — Socket Mode app with two submission paths:
  - `/review-prd` slash command opens a two-field modal (PRD name + text)
  - `file_shared` event listener auto-reviews `.md` and `.pdf` uploads
- **Slack Block Kit formatter** (`utils/slack_formatter.py`) — converts review dict into rich four-section Block Kit message with per-agent token breakdown in the footer
- **PDF support** (`utils/file_reader.py`) — PMs can upload PDF PRDs directly

---

## [v4.0] — 2026-05-05

### Added
- **Agent 3: UX and Design Reviewer** — surfaces missing UI states (loading, error, empty, success, offline), WCAG 2.1 AA gaps, design system consistency risks, and conversion drop-off points
- **Agent 4: Legal and Compliance Reviewer** — covers GDPR, PCI DSS, SCA/PSD2, consumer protection law, FCA/AML/KYC, accessibility legislation, and audit trail obligations
- **Four-agent sequential orchestration** — each agent receives the accumulated context from all prior agents so critiques are additive, not redundant

---

## [v3.0] — Initial release

### Added
- **Agent 1: Validator** — rules-based completeness checker scoring PRDs 0–100 against 12 quality standards across critical, high, and medium severity sections
- **Agent 2: Skeptical Tech Lead** — AI-driven technical challenger using Claude Sonnet; probes assumptions, feasibility, scale, edge cases, and operational concerns
- **Orchestrator** — sequential pipeline, JSON output, CLI interface
- **Sample PRD** and YAML template for customisation
