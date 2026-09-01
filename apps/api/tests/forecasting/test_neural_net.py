import numpy as np

from app.forecasting.neural_net import MLPRegressor


def test_train_reduces_loss():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(50, 4))
    y = x.sum(axis=1)

    model = MLPRegressor(input_dim=4, seed=1)
    losses = model.train(x, y, epochs=300)

    assert losses[-1] < losses[0]


def test_predict_shape_matches_input_rows():
    model = MLPRegressor(input_dim=3, seed=1)
    x = np.zeros((5, 3))
    predictions = model.predict(x)

    assert predictions.shape == (5,)


def test_can_fit_simple_linear_relationship():
    rng = np.random.default_rng(2)
    x = rng.uniform(-1, 1, size=(200, 2))
    y = 2 * x[:, 0] - x[:, 1]

    model = MLPRegressor(input_dim=2, hidden_dim=8, learning_rate=0.1, seed=3)
    model.train(x, y, epochs=800)
    predictions = model.predict(x)

    mae = np.mean(np.abs(predictions - y))
    assert mae < 0.25
