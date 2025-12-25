import numpy as np

from twenty48.env import Twenty48Env


def test_invalid_move_no_spawn():
    env = Twenty48Env()
    env.board = np.array(
        [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        dtype=np.int64,
    )
    obs, reward, done, info = env.step(3)
    assert reward == 0
    assert info["invalid_move"] is True
    assert info["spawned"] is None
    assert done is False
    assert np.array_equal(obs, env.board)


def test_done_detection():
    env = Twenty48Env()
    env.board = np.array(
        [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ],
        dtype=np.int64,
    )
    _, _, done, _ = env.step(3)
    assert done is True

    env.board = np.array(
        [
            [2, 2, 4, 8],
            [16, 32, 64, 128],
            [256, 512, 1024, 2],
            [4, 8, 16, 32],
        ],
        dtype=np.int64,
    )
    _, _, done, _ = env.step(3)
    assert done is False


def test_seed_reproducibility():
    actions = [0, 1, 2, 3, 0, 1, 2, 3]
    env1 = Twenty48Env()
    env2 = Twenty48Env()
    env1.reset(seed=123)
    env2.reset(seed=123)
    for action in actions:
        env1.step(action)
        env2.step(action)
    assert np.array_equal(env1.board, env2.board)
    assert env1.score == env2.score
