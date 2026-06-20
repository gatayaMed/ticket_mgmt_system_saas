"""
AI-powered priority predictor: predicts ticket priority.
"""
from typing import Dict, Any
from ..core.orchestrator import AIOrchestrator
from ..providers.base import AIRequest


class PriorityPredictor:
    """Predict ticket priority (low, medium, high, critical)."""

    CATEGORIES = ['low', 'medium', 'high', 'critical']

    def __init__(self):
        self.orchestrator = AIOrchestrator()

    def predict(self, title: str, description: str) -> Dict[str, Any]:
        """Predict priority for a ticket."""
        prompt = (
            f"Analyze this ticket and predict its priority level.\n\n"
            f"Title: {title}\nDescription: {description}\n\n"
            f"Consider: urgency keywords (urgent, down, blocker, critical), "
            f"business impact, number of users affected, and severity.\n"
            f"Return the most appropriate priority: low, medium, high, or critical."
        )
        request = AIRequest(prompt=prompt, temperature=0.3, max_tokens=50)
        response = self.orchestrator.generate(request)

        # Parse priority from response
        content = response.content.lower().strip().strip('.')
        for cat in self.CATEGORIES:
            if cat in content:
                return {
                    'priority': cat,
                    'confidence': 70.0,
                    'reasoning': content[:200],
                }

        # Fallback: use classify
        text = f"Title: {title}\nDescription: {description}"
        scores = self.orchestrator.classify_text(text, self.CATEGORIES)
        best = max(scores, key=scores.get) if scores else 'medium'
        return {
            'priority': best,
            'confidence': round(scores.get(best, 0) * 100, 1),
            'reasoning': 'Predicted from content analysis',
        }

    def predict_sync(self, title: str, description: str) -> Dict[str, Any]:
        return self.predict(title, description)
