import numpy as np


class MLPRegressor:
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 16,
        learning_rate: float = 0.05,
        seed: int = 42,
    ):
        rng = np.random.default_rng(seed)
        self.learning_rate = learning_rate
        self.w1 = rng.normal(0, np.sqrt(2 / input_dim), size=(input_dim, hidden_dim))
        self.b1 = np.zeros(hidden_dim)
        self.w2 = rng.normal(0, np.sqrt(2 / hidden_dim), size=(hidden_dim, 1))
        self.b2 = np.zeros(1)

    @staticmethod
    def _relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(x, 0)

    @staticmethod
    def _relu_derivative(x: np.ndarray) -> np.ndarray:
        return (x > 0).astype(x.dtype)

    def _forward(self, x: np.ndarray):
        z1 = x @ self.w1 + self.b1
        a1 = self._relu(z1)
        z2 = a1 @ self.w2 + self.b2
        return z1, a1, z2

    def predict(self, x: np.ndarray) -> np.ndarray:
        _, _, z2 = self._forward(x)
        return z2.reshape(-1)

    def train(self, x: np.ndarray, y: np.ndarray, epochs: int = 400) -> list[float]:
        n = x.shape[0]
        y_col = y.reshape(-1, 1)
        loss_history: list[float] = []

        for _ in range(epochs):
            z1, a1, z2 = self._forward(x)
            error = z2 - y_col
            loss = float(np.mean(error**2))
            loss_history.append(loss)

            grad_z2 = (2.0 / n) * error
            grad_w2 = a1.T @ grad_z2
            grad_b2 = grad_z2.sum(axis=0)

            grad_a1 = grad_z2 @ self.w2.T
            grad_z1 = grad_a1 * self._relu_derivative(z1)
            grad_w1 = x.T @ grad_z1
            grad_b1 = grad_z1.sum(axis=0)

            self.w2 -= self.learning_rate * grad_w2
            self.b2 -= self.learning_rate * grad_b2
            self.w1 -= self.learning_rate * grad_w1
            self.b1 -= self.learning_rate * grad_b1

        return loss_history
