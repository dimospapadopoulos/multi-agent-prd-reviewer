"""
Skeptic Agent
Plays "skeptical tech lead" to challenge PRD assumptions and probe feasibility
Uses Claude API to generate technical critique
"""

import os
from anthropic import Anthropic
from typing import Dict


class SkepticAgent:
    """
    Agent that challenges PRDs with technical skepticism
    
    Reviews PRD + validation results and generates critical questions
    about assumptions, feasibility, scale, and edge cases
    """
    
    def __init__(self, api_key: str = None, system_prompt_path: str = "prompts/skeptic_system.txt"):
        """
        Initialize Skeptic Agent with Claude API
        
        Args:
            api_key: Anthropic API key (reads from env if not provided)
            system_prompt_path: Path to system prompt file
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or provided")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Latest Sonnet
        
        # Load system prompt
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()
    
    def challenge(self, prd_text: str, validation_report: Dict) -> Dict:
        """
        Generate technical critique of PRD
        
        Args:
            prd_text: Full PRD text
            validation_report: Validation results from ValidatorAgent
            
        Returns:
            Dictionary with critique content and metadata
        """
        # Build user prompt combining PRD and validation results
        user_prompt = self._build_user_prompt(prd_text, validation_report)
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extract critique text
        critique_text = response.content[0].text
        
        return {
            "critique": critique_text,
            "model": self.model,
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens
        }
    
    def _build_user_prompt(self, prd_text: str, validation_report: Dict) -> str:
        """
        Build the user prompt combining PRD and validation context
        
        Args:
            prd_text: Full PRD text
            validation_report: Validation results
            
        Returns:
            Formatted prompt string
        """
        # Extract validation context
        score = validation_report['score']
        status = validation_report['status']
        missing_critical = validation_report.get('missing_critical', [])
        missing_high = validation_report.get('missing_high', [])
        
        # Build validation summary
        validation_summary = f"**Validation Score:** {score}/100 ({status})\n\n"
        
        if missing_critical:
            validation_summary += f"**Critical Sections Missing:**\n"
            for section in missing_critical:
                validation_summary += f"- {section}\n"
            validation_summary += "\n"
        
        if missing_high:
            validation_summary += f"**High Priority Sections Missing:**\n"
            for section in missing_high:
                validation_summary += f"- {section}\n"
            validation_summary += "\n"
        
        # Combine into full prompt
        prompt = f"""Review this PRD with your technical expertise.

VALIDATION RESULTS:
{validation_summary}

PRD CONTENT:
{prd_text}

---

Provide your technical critique following the format specified in your role.
Focus on the HARDEST technical challenges and RISKIEST assumptions.
Be specific and actionable."""

        return prompt