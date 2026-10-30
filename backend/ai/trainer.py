
mport torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from ai.model import ErrorClassifier


def train(
    features,
    labels,
    epochs=100,
    learning_rate=0.001,
    save_path="models/error_classifier.pt"
):
    x = torch.tensor(features, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.long)

    dataset = TensorDataset(x, y)

    loader = DataLoader(
        dataset,
        batch_size=32,
        shuffle=True
    )

    model = ErrorClassifier()
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=learning_rate
    )

    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        total_loss = 0

        for batch_x, batch_y in loader:
            optimizer.zero_grad()

            output = model(batch_x)
            loss = criterion(output, batch_y)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        if (epoch + 1) % 10 == 0:
            print(
                f"Epoch {epoch + 1}/{epochs} "
                f"Loss: {total_loss / len(loader):.5f}"
            )

    model.eval()

    torch.save(
        model.state_dict(),
        save_path
    )

    print("Model saved:", save_path)
