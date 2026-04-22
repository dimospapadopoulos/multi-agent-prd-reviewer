"""
Legal Agent
Reviews PRDs for legal, regulatory, and compliance gaps
Uses Claude API to generate legal and compliance critique
"""

import os
from anthropic import Anthropic
from typing import Dict


class LegalAgent:
    """
    Agent that reviews PRDs for legal and compliance risks

    Reviews PRD alongside all prior agent outputs, then generates
    targeted feedback on data privacy, payment regulation, consumer
    protection, market-specific rules, and audit trail requirements.
    """

    def __init__(self, api_key: str = None, system_prompt_path: str = "prompts/legal_system.txt"):
        """
        Initialize Legal Agent with Claude API

        Args:
            api_key: Anthropic API key (reads from env if not provided)
            system_prompt_path: Path to system prompt file
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or provided")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-6"

        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()

    def review(
        self,
        prd_text: str,
        validation_report: Dict,
        technical_critique: str,
        ux_critique: str
    ) -> Dict:
        """
        Generate legal and compliance critique of PRD

        Args:
            prd_text: Full PRD text
            validation_report: Validation results from ValidatorAgent
            technical_critique: Technical critique from SkepticAgent
            ux_critique: UX critique from UXAgent

        Returns:
            Dictionary with critique content and metadata
        """
        user_prompt = self._build_user_prompt(
            prd_text, validation_report, technical_critique, ux_critique
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        critique_text = response.content[0].text

        return {
            "critique": critique_text,
            "model": self.model,
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens
        }

    def _build_user_prompt(
        self,
        prd_text: str,
        validation_report: Dict,
        technical_critique: str,
        ux_critique: str
    ) -> str:
        """
        Build user prompt combining PRD and all prior agent context

        Args:
            prd_text: Full PRD text
            validation_report: Validation results
            technical_critique: Technical critique already generated
            ux_critique: UX critique already generated

        Returns:
            Formatted prompt string
        """
        score = validation_report['score']
        status = validation_report['status']

        prompt = f"""Review this PRD from a legal and compliance perspective.

VALIDATION SCORE: {score}/100 ({status})

TECHNICAL CRITIQUE ALREADY RAISED:
{technical_critique}

UX CRITIQUE ALREADY RAISED:
{ux_critique}

PRD CONTENT:
{prd_text}

---

Provide your legal and compliance critique following the format specified in your role.
Focus on data privacy, payment regulation, consumer protection, market-specific rules,
accessibility legislation, and audit trail obligations.
Do NOT repeat technical or UX issues already raised above — focus squarely on legal
and compliance dimensions.
Be specific and actionable."""

        return prompt
