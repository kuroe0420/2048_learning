```text
あなたはシニアPythonエンジニアです。2048の環境（Gym風API）をPythonで実装してください。目的は将来のExpectimax/RLで使うことです。以下の要求仕様を満たし、ユニットテストまで通る状態にしてください。実装はクリーンで拡張可能に。

# 要求仕様
- 盤面: 4x4 の numpy.ndarray (int64)。0は空。値は2,4,8,...の実値。
- action: int 0=UP,1=RIGHT,2=DOWN,3=LEFT
- reset(seed=None): 盤面初期化→ランダムに2タイル追加（2が90%、4が10%）→score=0→board.copy()を返す
- step(action): 
  1) 方向にスライド＋マージ（2048標準: 1手内で同一タイルは1回までマージ）
  2) 盤面が変化した場合のみタイルを1つ追加（空きセルにランダム。2:90%,4:10%）
  3) reward=その手で生成された合体タイル値の合計（例:2+2->4ならreward+=4）
  4) done=有効手なし（満杯かつ上下左右に合体不可）
  5) infoに invalid_move, moved, score, max_tile, won(2048到達), spawned(row,col,val or None) を含める
- 無効手: 盤面変化なし→タイル追加しない→reward=0→done判定は現盤面で再評価→info["invalid_move"]=True
- render(): テキスト表示でOK
- clone(): board/score/rng状態まで含めて完全コピー。clone後の遷移が一致すること。

# テスト要件（pytest）
- mechanics(ラインマージ)のテスト:
  [2,0,2,0] -> [4,0,0,0], reward=4
  [2,2,2,0] -> [4,2,0,0], reward=4
  [2,2,2,2] -> [4,4,0,0], reward=8
  [4,4,2,2] -> [8,4,0,0], reward=12
- envのテスト:
  - stepで変化がない場合 spawned=None かつタイル追加しない
  - done判定（満杯でもマージ可能ならFalse、不可ならTrue）
  - seed再現: 同seed+同行動列で最終盤面一致

# 実装方針
- スライド/マージは純関数で実装し、方向は回転/反転でLEFT処理を再利用してもよい。
- RNGはnumpy.random.Generatorかrandom.Randomで統一し、cloneで状態複製できるようにする。
- 依存は最小: numpy, pytest。pyproject.tomlで管理。

# 生成物
- リポジトリ構成:
  README.md（使い方、action定義、簡易例）
  pyproject.toml
  src/twenty48/{__init__.py,env.py,mechanics.py,utils.py}
  tests/{test_mechanics.py,test_env_step.py}
  scripts/{play_random.py,benchmark.py}
- `pytest -q` が通ること。
- `python scripts/play_random.py` でランダムプレイが動くこと。

まず全ファイルを作成し、その後に不足があれば自分で修正して完成させてください。
```