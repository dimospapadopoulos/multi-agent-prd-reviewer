"""
Validator Agent
Wraps the existing PRD validation logic to check completeness
"""

import yaml
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ValidationResult:
    """Result from validating a single section"""
    section_name: str
    required: bool
    found: bool
    severity: str
    keywords_found: List[str]
    score: int


class ValidatorAgent:
    """
    Agent that validates PRD completeness against a template
    
    Uses keyword-based detection to check if required sections are present
    Scores the PRD 0-100 based on weighted section importance
    """
    
    def __init__(self, template_path: str):
        """
        Initialize validator with a YAML template
        
        Args:
            template_path: Path to prd_template.yaml file
        """
        self.template_path = template_path
        self.template = self._load_template()
        self.scoring = self.template.get('scoring', {})
        
    def _load_template(self) -> dict:
        """Load and parse YAML template"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def validate(self, prd_text: str) -> Tuple[List[ValidationResult], int]:
        """
        Validate PRD text against template
        
        Args:
            prd_text: The full PRD text to validate
            
        Returns:
            Tuple of (list of ValidationResults, overall score)
        """
        # Convert PRD to lowercase for case-insensitive matching
        prd_lower = prd_text.lower()
        
        results = []
        total_score = 0
        max_score = 0
        
        # Check each section in template
        for section in self.template.get('sections', []):
            section_name = section['name']
            required = section['required']
            severity = section['severity']
            keywords = section.get('keywords', [])
            
            # Check if any keywords are found in PRD
            keywords_found = [kw for kw in keywords if kw.lower() in prd_lower]
            found = len(keywords_found) > 0
            
            # Calculate score for this section
            weight_key = f"{severity}_weight"
            section_weight = self.scoring.get(weight_key, 0)
            section_score = section_weight if found else 0
            
            # Track max possible score
            if required:
                max_score += section_weight
            
            # Add to total if found
            total_score += section_score
            
            # Create result
            result = ValidationResult(
                section_name=section_name,
                required=required,
                found=found,
                severity=severity,
                keywords_found=keywords_found,
                score=section_score
            )
            results.append(result)
        
        # Calculate percentage score
        overall_score = int((total_score / max_score * 100)) if max_score > 0 else 0
        
        return results, overall_score
    
    def format_report(self, results: List[ValidationResult], score: int) -> dict:
        """
        Format validation results into structured report
        
        Args:
            results: List of ValidationResult objects
            score: Overall score (0-100)
            
        Returns:
            Dictionary with formatted report data
        """
        # Categorize results
        missing_critical = [r for r in results if not r.found and r.required and r.severity == 'critical']
        missing_high = [r for r in results if not r.found and r.required and r.severity == 'high']
        missing_medium = [r for r in results if not r.found and r.severity == 'medium']
        found = [r for r in results if r.found]
        
        # Determine status
        if score >= 90:
            status = "READY FOR REVIEW"
            status_emoji = "✅"
        elif score >= 70:
            status = "NEEDS IMPROVEMENT"
            status_emoji = "⚠️"
        else:
            status = "NOT READY"
            status_emoji = "❌"
        
        return {
            "score": score,
            "status": status,
            "status_emoji": status_emoji,
            "missing_critical": [r.section_name for r in missing_critical],
            "missing_high": [r.section_name for r in missing_high],
            "missing_medium": [r.section_name for r in missing_medium],
            "found_sections": [r.section_name for r in found],
            "total_sections": len(results),
            "found_count": len(found),
            "missing_count": len(results) - len(found)
        }