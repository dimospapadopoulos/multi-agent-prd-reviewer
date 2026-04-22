"""
Slack Block Kit formatter for PRD review results
Converts the orchestrator's review dict into Slack blocks ready to post
"""

from typing import List, Dict

# Slack's hard limit per section text block is 3000 chars; keep a safety margin
_BLOCK_CHAR_LIMIT = 2900


def format_review_blocks(review: dict) -> List[Dict]:
    """
    Convert a complete PRD review dict into a list of Slack Block Kit blocks.

    Handles long critique text by splitting across multiple section blocks so
    nothing is silently truncated by the Slack API.

    Args:
        review: Review dict produced by PRDReviewOrchestrator.review_prd()

    Returns:
        List of Slack Block Kit block dicts
    """
    blocks: List[Dict] = []

    summary = review["summary"]
    validation = review["validation"]
    meta = review["metadata"]

    status = summary["overall_status"]
    status_emoji = "✅" if "READY" in status else ("⚠️" if "NEEDS" in status else "❌")

    # ── Header ──────────────────────────────────────────────────────────────
    blocks.append({
        "type": "header",
        "text": {"type": "plain_text", "text": f"PRD Review: {review['prd_name']}"}
    })

    # ── At-a-glance summary ─────────────────────────────────────────────────
    blocks.append({
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*Overall Status*\n{status_emoji}  {status}"
            },
            {
                "type": "mrkdwn",
                "text": (
                    f"*Completeness*\n"
                    f"{validation['score']}/100  {validation['status_emoji']}"
                )
            },
            {
                "type": "mrkdwn",
                "text": f"*Critical Gaps*\n{summary['critical_gaps']}"
            },
            {
                "type": "mrkdwn",
                "text": f"*High Priority Gaps*\n{summary['high_priority_gaps']}"
            },
        ]
    })

    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f":memo:  *Recommendation:* {summary['recommendation']}"
        }
    })

    blocks.append({"type": "divider"})

    # ── Agent 1: Validation detail ──────────────────────────────────────────
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                f":clipboard:  *Validation  ·  {validation['score']}/100 "
                f"{validation['status_emoji']}*\n"
                f"Found {validation['found_count']}/{validation['total_sections']} sections"
            )
        }
    })

    if validation["missing_critical"]:
        lines = "\n".join(f"• {s}" for s in validation["missing_critical"])
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":red_circle:  *Critical Missing ({len(validation['missing_critical'])})* \n{lines}"
            }
        })

    if validation["missing_high"]:
        lines = "\n".join(f"• {s}" for s in validation["missing_high"])
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":large_yellow_circle:  *High Priority Missing ({len(validation['missing_high'])})* \n{lines}"
            }
        })

    blocks.append({"type": "divider"})

    # ── Agent 2: Technical critique ─────────────────────────────────────────
    blocks.append(_label_block(":thinking_face:  *Technical Critique  ·  Agent 2*"))
    blocks.extend(_text_blocks(review["technical_critique"]))
    blocks.append({"type": "divider"})

    # ── Agent 3: UX critique ────────────────────────────────────────────────
    blocks.append(_label_block(":art:  *UX & Design Critique  ·  Agent 3*"))
    blocks.extend(_text_blocks(review["ux_critique"]))
    blocks.append({"type": "divider"})

    # ── Agent 4: Legal critique ─────────────────────────────────────────────
    blocks.append(_label_block(":scales:  *Legal & Compliance Critique  ·  Agent 4*"))
    blocks.extend(_text_blocks(review["legal_critique"]))
    blocks.append({"type": "divider"})

    # ── Footer / metadata ───────────────────────────────────────────────────
    timestamp = review["timestamp"][:19].replace("T", " ")
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": (
                    f":robot_face:  *Multi-Agent PRD Reviewer*  ·  "
                    f"Model: `{meta['model_used']}`  ·  "
                    f"Tokens: {meta['total_tokens']:,} "
                    f"(tech: {meta['skeptic_tokens']:,}  "
                    f"ux: {meta['ux_tokens']:,}  "
                    f"legal: {meta['legal_tokens']:,})  ·  "
                    f"{timestamp}"
                )
            }
        ]
    })

    return blocks


# ── Internal helpers ─────────────────────────────────────────────────────────

def _label_block(text: str) -> Dict:
    """Section block used as a section heading."""
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def _text_blocks(text: str) -> List[Dict]:
    """
    Split a critique string into one or more section blocks so no single block
    exceeds Slack's 3000-char limit.  Splits at newline boundaries where possible.
    """
    if not text:
        return [_label_block("_No content generated._")]

    blocks: List[Dict] = []
    remaining = text.strip()

    while remaining:
        if len(remaining) <= _BLOCK_CHAR_LIMIT:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": remaining}
            })
            break

        # Try to break at the last newline within the limit
        chunk = remaining[:_BLOCK_CHAR_LIMIT]
        split_at = chunk.rfind("\n")
        if split_at > _BLOCK_CHAR_LIMIT // 2:
            chunk = remaining[:split_at]
            remaining = remaining[split_at:].lstrip()
        else:
            remaining = remaining[_BLOCK_CHAR_LIMIT:]

        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": chunk}
        })

    return blocks
