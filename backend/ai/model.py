
import torch
import torch.nn as nn


class ErrorClassifier(nn.Module):

    def __init__(self, input_size=8, hidden_size=64, num_classes=6):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.15),

            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),

            nn.Linear(hidden_size, num_classes)
        )

    def forward(self, x):
        return self.network(x)


class FixerAI:

    CLASSES = [
        "syntax",
        "undefined_reference",
        "type_error",
        "dependency",
        "configuration",
        "other"
    ]

    def __init__(self):
        self.model = None
        self.available = False

        try:
            self.model = ErrorClassifier()

            from config import MODELS_DIR
            weights = MODELS_DIR / "error_classifier.pt"

            if weights.exists():
                state = torch.load(
                    weights,
                    map_location="cpu",
                    weights_only=True
                )

                self.model.load_state_dict(state)
                self.model.eval()
                self.available = True

        except Exception as error:
            print("[AI] Model unavailable:", error)

    def predict(self, features):
        if not self.available:
            return {
                "available": False,
                "message": "학습된 모델이 없어 규칙 기반 분석을 사용합니다."
            }

        tensor = torch.tensor(
            features,
            dtype=torch.float32
        ).reshape(1, -1)

        with torch.no_grad():
            logits = self.model(tensor)
            probabilities = torch.softmax(logits, dim=1)[0]

        index = int(torch.argmax(probabilities))

        return {
            "available": True,
            "category": self.CLASSES[index],
            "confidence": float(probabilities[index])
        }
