"""
Multi-Agent PRD Reviewer — Slack Bot
Listens for /review-prd slash commands and .md file uploads,
runs the four-agent pipeline, and posts Block Kit results back to Slack.

Requires Socket Mode (no public URL needed):
    SLACK_BOT_TOKEN  — xoxb-... Bot User OAuth Token
    SLACK_APP_TOKEN  — xapp-... App-Level Token (connections:write scope)
    ANTHROPIC_API_KEY — used by the agent pipeline
"""

import os
import threading
import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from orchestrator import PRDReviewOrchestrator
from utils.slack_formatter import format_review_blocks

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


# ── /review-prd slash command ────────────────────────────────────────────────

@app.command("/review-prd")
def handle_review_command(ack, body, client):
    """
    Open a modal where the user can paste a PRD name and full PRD text.
    Slack requires acknowledgement within 3 seconds — the review itself
    runs asynchronously after modal submission.
    """
    ack()

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "prd_review_modal",
            "title": {"type": "plain_text", "text": "Review PRD"},
            "submit": {"type": "plain_text", "text": "Run Review"},
            "close": {"type": "plain_text", "text": "Cancel"},
            # Store the originating channel so we can post results there
            "private_metadata": body["channel_id"],
            "blocks": [
                {
                    "type": "input",
                    "block_id": "prd_name_block",
                    "label": {"type": "plain_text", "text": "PRD Name"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "prd_name",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "e.g. Apple Pay Integration — UK Market"
                        }
                    }
                },
                {
                    "type": "input",
                    "block_id": "prd_text_block",
                    "label": {"type": "plain_text", "text": "PRD Content"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "prd_text",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Paste the full PRD markdown here..."
                        }
                    }
                }
            ]
        }
    )


@app.view("prd_review_modal")
def handle_modal_submission(ack, body, view, client):
    """
    Called when the user submits the /review-prd modal.
    Acknowledges immediately, then runs the four-agent pipeline in a
    background thread to avoid Slack's 3-second response timeout.
    """
    ack()

    channel_id = view["private_metadata"]
    user_id = body["user"]["id"]
    values = view["state"]["values"]
    prd_name = values["prd_name_block"]["prd_name"]["value"].strip()
    prd_text = values["prd_text_block"]["prd_text"]["value"].strip()

    client.chat_postMessage(
        channel=channel_id,
        text=(
            f"<@{user_id}> Running 4-agent review on *{prd_name}* — "
            "this takes around 60 seconds... :hourglass_flowing_sand:"
        )
    )

    def _run():
        _run_and_post(client, channel_id, user_id, prd_name, prd_text)

    threading.Thread(target=_run, daemon=True).start()


# ── .md file upload handler ──────────────────────────────────────────────────

@app.event("file_shared")
def handle_file_shared(event, client, logger):
    """
    Automatically review any Markdown file (.md) shared in a channel
    where the bot is present.
    """
    try:
        file_id = event.get("file_id")
        channel_id = event.get("channel_id")
        user_id = event.get("user_id")

        if not channel_id or not file_id:
            return

        file_info = client.files_info(file=file_id)
        file_obj = file_info["file"]

        if not file_obj.get("name", "").endswith(".md"):
            return

        prd_name = (
            file_obj["name"]
            .removesuffix(".md")
            .replace("_", " ")
            .replace("-", " ")
            .title()
        )

        # Download private file using the bot token
        response = requests.get(
            file_obj["url_private"],
            headers={"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"},
            timeout=30
        )
        response.raise_for_status()
        prd_text = response.text.strip()

        if not prd_text:
            client.chat_postMessage(
                channel=channel_id,
                text=f"<@{user_id}> The uploaded file appears to be empty — nothing to review."
            )
            return

        client.chat_postMessage(
            channel=channel_id,
            text=(
                f"<@{user_id}> Detected PRD file *{file_obj['name']}* — "
                "running 4-agent review... :hourglass_flowing_sand: (~60 seconds)"
            )
        )

        def _run():
            _run_and_post(client, channel_id, user_id, prd_name, prd_text)

        threading.Thread(target=_run, daemon=True).start()

    except Exception as exc:
        logger.error(f"file_shared handler error: {exc}")


# ── Shared pipeline runner ────────────────────────────────────────────────────

def _run_and_post(client, channel_id: str, user_id: str, prd_name: str, prd_text: str):
    """
    Run the four-agent orchestrator and post Block Kit results to Slack.
    Called from a background thread so it can take as long as needed.
    """
    try:
        orchestrator = PRDReviewOrchestrator()
        review = orchestrator.review_prd(prd_text, prd_name)

        # Save JSON output locally as well
        output_path = orchestrator.save_review(review)
        print(f"Review saved: {output_path}")

        blocks = format_review_blocks(review)

        client.chat_postMessage(
            channel=channel_id,
            blocks=blocks,
            text=f"PRD Review complete: {prd_name}"   # fallback for notifications
        )

    except Exception as exc:
        client.chat_postMessage(
            channel=channel_id,
            text=(
                f"<@{user_id}> Review failed for *{prd_name}*: `{exc}`\n"
                "Check that `ANTHROPIC_API_KEY` is set and the PRD text is not empty."
            )
        )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Multi-Agent PRD Reviewer — Slack bot starting (Socket Mode)...")
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
