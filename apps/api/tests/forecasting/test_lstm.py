import numpy as np

from app.forecasting.lstm import LSTMRegressor


def _make_linear_sequence_dataset(n=64, timesteps=6, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, size=(n, timesteps))
    y = x.sum(axis=1) * 0.1
    return x, y


def test_lstm_predict_output_shape():
    x, y = _make_linear_sequence_dataset()
    model = LSTMRegressor(timesteps=6, hidden_dim=8, seed=1)
    model.train(x, y, epochs=5)
    predictions = model.predict(x)
    assert predictions.shape == (x.shape[0],)


def test_lstm_training_reduces_loss():
    x, y = _make_linear_sequence_dataset()
    model = LSTMRegressor(timesteps=6, hidden_dim=8, learning_rate=0.05, seed=1)
    loss_history = model.train(x, y, epochs=150)
    assert loss_history[-1] < loss_history[0]


def test_lstm_is_deterministic_for_fixed_seed():
    x, y = _make_linear_sequence_dataset()
    first = LSTMRegressor(timesteps=6, hidden_dim=8, seed=3)
    first.train(x, y, epochs=20)
    second = LSTMRegressor(timesteps=6, hidden_dim=8, seed=3)
    second.train(x, y, epochs=20)
    np.testing.assert_allclose(first.predict(x), second.predict(x))


def test_lstm_handles_single_row_prediction():
    x, y = _make_linear_sequence_dataset(n=32)
    model = LSTMRegressor(timesteps=6, hidden_dim=4, seed=2)
    model.train(x, y, epochs=10)
    single = model.predict(x[:1])
    assert single.shape == (1,)
