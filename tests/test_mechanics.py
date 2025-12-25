import numpy as np

from twenty48.mechanics import slide_and_merge_line


def test_slide_and_merge_line_cases():
    cases = [
        ([2, 0, 2, 0], [4, 0, 0, 0], 4),
        ([2, 2, 2, 0], [4, 2, 0, 0], 4),
        ([2, 2, 2, 2], [4, 4, 0, 0], 8),
        ([4, 4, 2, 2], [8, 4, 0, 0], 12),
        ([2, 0, 0, 0], [2, 0, 0, 0], 0),
    ]
    for line, expected, reward in cases:
        out, got_reward, _ = slide_and_merge_line(line)
        assert np.array_equal(out, np.array(expected, dtype=np.int64))
        assert got_reward == reward
