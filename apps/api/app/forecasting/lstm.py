import numpy as np


class LSTMRegressor:
    def __init__(
        self,
        timesteps: int,
        hidden_dim: int = 16,
        learning_rate: float = 0.05,
        seed: int = 42,
    ):
        rng = np.random.default_rng(seed)
        self.timesteps = timesteps
        self.hidden_dim = hidden_dim
        self.learning_rate = learning_rate

        input_dim = 1
        scale_x = np.sqrt(2 / (input_dim + hidden_dim))
        scale_h = np.sqrt(2 / (hidden_dim + hidden_dim))

        self.wxf = rng.normal(0, scale_x, size=(input_dim, hidden_dim))
        self.whf = rng.normal(0, scale_h, size=(hidden_dim, hidden_dim))
        self.bf = np.ones(hidden_dim)

        self.wxi = rng.normal(0, scale_x, size=(input_dim, hidden_dim))
        self.whi = rng.normal(0, scale_h, size=(hidden_dim, hidden_dim))
        self.bi = np.zeros(hidden_dim)

        self.wxo = rng.normal(0, scale_x, size=(input_dim, hidden_dim))
        self.who = rng.normal(0, scale_h, size=(hidden_dim, hidden_dim))
        self.bo = np.zeros(hidden_dim)

        self.wxc = rng.normal(0, scale_x, size=(input_dim, hidden_dim))
        self.whc = rng.normal(0, scale_h, size=(hidden_dim, hidden_dim))
        self.bc = np.zeros(hidden_dim)

        self.wy = rng.normal(0, np.sqrt(2 / hidden_dim), size=(hidden_dim, 1))
        self.by = np.zeros(1)

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -60, 60)))

    def _forward(self, x: np.ndarray):
        n = x.shape[0]
        h = np.zeros((n, self.hidden_dim))
        c = np.zeros((n, self.hidden_dim))
        cache = []

        for t in range(self.timesteps):
            x_t = x[:, t, :]
            h_prev, c_prev = h, c

            f = self._sigmoid(x_t @ self.wxf + h_prev @ self.whf + self.bf)
            i = self._sigmoid(x_t @ self.wxi + h_prev @ self.whi + self.bi)
            o = self._sigmoid(x_t @ self.wxo + h_prev @ self.who + self.bo)
            g = np.tanh(x_t @ self.wxc + h_prev @ self.whc + self.bc)

            c = f * c_prev + i * g
            h = o * np.tanh(c)

            cache.append((x_t, h_prev, c_prev, f, i, o, g, c, h))

        y_hat = h @ self.wy + self.by
        return y_hat, h, cache

    def predict(self, x: np.ndarray) -> np.ndarray:
        x = x.reshape(x.shape[0], self.timesteps, 1)
        y_hat, _, _ = self._forward(x)
        return y_hat.reshape(-1)

    def train(self, x: np.ndarray, y: np.ndarray, epochs: int = 400) -> list[float]:
        x = x.reshape(x.shape[0], self.timesteps, 1)
        n = x.shape[0]
        y_col = y.reshape(-1, 1)
        loss_history: list[float] = []

        for _ in range(epochs):
            y_hat, h_final, cache = self._forward(x)
            error = y_hat - y_col
            loss = float(np.mean(error**2))
            loss_history.append(loss)

            dy = (2.0 / n) * error
            dwy = h_final.T @ dy
            dby = dy.sum(axis=0)
            dh_next = dy @ self.wy.T
            dc_next = np.zeros((n, self.hidden_dim))

            grads = {
                key: np.zeros_like(getattr(self, key))
                for key in (
                    "wxf", "whf", "bf",
                    "wxi", "whi", "bi",
                    "wxo", "who", "bo",
                    "wxc", "whc", "bc",
                )
            }

            for t in reversed(range(self.timesteps)):
                x_t, h_prev, c_prev, f, i, o, g, c, h = cache[t]

                dh = dh_next
                tanh_c = np.tanh(c)

                do = dh * tanh_c * o * (1 - o)
                dc = dc_next + dh * o * (1 - tanh_c**2)
                df = dc * c_prev * f * (1 - f)
                di = dc * g * i * (1 - i)
                dg = dc * i * (1 - g**2)

                grads["wxf"] += x_t.T @ df
                grads["whf"] += h_prev.T @ df
                grads["bf"] += df.sum(axis=0)

                grads["wxi"] += x_t.T @ di
                grads["whi"] += h_prev.T @ di
                grads["bi"] += di.sum(axis=0)

                grads["wxo"] += x_t.T @ do
                grads["who"] += h_prev.T @ do
                grads["bo"] += do.sum(axis=0)

                grads["wxc"] += x_t.T @ dg
                grads["whc"] += h_prev.T @ dg
                grads["bc"] += dg.sum(axis=0)

                dh_next = (
                    df @ self.whf.T + di @ self.whi.T + do @ self.who.T + dg @ self.whc.T
                )
                dc_next = dc * f

            self.wy -= self.learning_rate * dwy
            self.by -= self.learning_rate * dby
            for key, grad in grads.items():
                setattr(self, key, getattr(self, key) - self.learning_rate * grad)

        return loss_history
