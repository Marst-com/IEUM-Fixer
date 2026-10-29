from ai.model import FixerAI


class InferenceEngine:

    def __init__(self):
        self.ai = FixerAI()

    @staticmethod
    def extract_features(issue):
        message = issue.get("message", "").lower()
        title = issue.get("title", "").lower()

        return [
            float("syntax" in title or "syntax" in message),
            float("undefined" in message or "not defined" in message),
            float("type" in message),
            float("module" in message or "import" in message),
            float("config" in message or "json" in message),
            float("error" in title),
            min(len(message) / 500, 1.0),
            min(issue.get("line", 1) / 1000, 1.0)
        ]

    def classify(self, issue):
        return self.ai.predict(
            self.extract_features(issue)
        )
