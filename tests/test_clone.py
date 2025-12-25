import numpy as np

from twenty48.env import Twenty48Env


def test_clone_reproducibility():
    env = Twenty48Env()
    env.reset(seed=999)
    for action in [0, 1, 2]:
        env.step(action)

    cloned = env.clone()
    actions = [3, 2, 1, 0, 3]
    for action in actions:
        env.step(action)
        cloned.step(action)

    assert np.array_equal(env.board, cloned.board)
    assert env.score == cloned.score
