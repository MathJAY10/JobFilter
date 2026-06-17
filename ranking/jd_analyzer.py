from dataclasses import dataclass
from typing import List

@dataclass
class JDExtraction:
    must_have_skills: List[str]
    preferred_skills: List[str]
    negative_signals: List[str]

class JDAnalyzer:
    """Deterministic, rule-based JD parser without LLMs."""
    
    def __init__(self, must_have_headers: List[str] = None, preferred_headers: List[str] = None):
        self.must_have_headers = must_have_headers or ["must have", "requirements", "required", "what you need"]
        self.preferred_headers = preferred_headers or ["preferred", "bonus", "nice to have"]
        self.negative_headers = ["avoid", "negative", "not looking for"]

    def analyze(self, jd_text: str) -> JDExtraction:
        """Parses a job description to extract keywords per section."""
        lines = jd_text.split('\n')
        
        must_have = []
        preferred = []
        negative = []
        
        current_section = None
        
        for line in lines:
            line_lower = line.strip().lower()
            if not line_lower:
                continue
                
            # Detect section changes
            if any(h in line_lower for h in self.must_have_headers):
                current_section = 'must_have'
                continue
            elif any(h in line_lower for h in self.preferred_headers):
                current_section = 'preferred'
                continue
            elif any(h in line_lower for h in self.negative_headers):
                current_section = 'negative'
                continue
                
            # Extract bullet points or sentences as skills/signals
            clean_line = line.strip("*-• ").strip()
            if clean_line and current_section:
                if current_section == 'must_have':
                    must_have.append(clean_line)
                elif current_section == 'preferred':
                    preferred.append(clean_line)
                elif current_section == 'negative':
                    negative.append(clean_line)
                    
        return JDExtraction(
            must_have_skills=must_have,
            preferred_skills=preferred,
            negative_signals=negative
        )
