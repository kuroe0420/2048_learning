# 2048 AI 開発（Python環境）: 環境実装 要求仕様・Codexプロンプト・開発チェックリスト

このドキュメントは、Python環境で 2048 のゲーム環境（Gym風API）を実装するための **要求仕様**、**Codex向けプロンプト（そのまま貼り付けて使用）**、および **開発フローのチェックリスト**をまとめたものです。

---

## 1. 要求仕様（PRD + 技術仕様）

### 1.1 目的
- 2048のゲーム環境を **Python上で再現**し、将来の探索（Expectimax）・学習（RL/DL）に共通利用できる **安定した環境API** を提供する。
- 初期段階では **学習器は作らず**、環境（状態遷移・報酬・終了判定・乱数）と評価基盤（ロギング・シード固定・簡易ベンチ）を完成させる。

### 1.2 スコープ（今回作るもの）
- 4x4固定の2048環境（将来拡張できる設計にする）
- Gym互換に寄せたAPI：`reset()`, `step(action)`, `render()`, `clone()`（探索向け）
- 乱数タイル生成（2が90%、4が10%、空きセルにランダム配置）
- 合体ルール：**1手で同一タイルは1回まで合体**（2048標準）
- 報酬：標準は「その手で増えたスコア（合体で生成された値の合計）」
  - 例：2+2→4 で reward += 4
- 終了判定：
  - `done=True` = 盤面が満杯かつ上下左右いずれも合体不可（有効手なし）
  - `won`（任意）：2048生成をフラグで保持（続行可能設定も将来対応）
- 乱数制御：`seed` 指定で再現可能

### 1.3 非スコープ（後でやる）
- AI（Expectimax/RL）
- GUI
- 高速化（Numba等）
- 盤面サイズの可変（設計上は想定、実装は4x4でOK）

---

## 2. 環境API仕様（厳密）

### 2.1 データ表現
- `board`: `np.ndarray` shape `(4,4)` dtype `np.int64`（0は空）
- 状態は **値そのもの（2,4,8,...)** を保持（指数表現は採用しない）
- `score`: int
- `rng`: `random.Random` か `numpy.random.Generator`（いずれかで統一）

### 2.2 アクション定義
- `action` は `int`:
  - `0=UP`, `1=RIGHT`, `2=DOWN`, `3=LEFT`
- 無効手（盤面が変化しない移動）の扱い：
  - **標準仕様**：盤面が変化しない場合、タイル追加は行わず、reward=0、done判定はその盤面で再評価する（継続）
  - `info["invalid_move"]=True` を返す

### 2.3 `reset(seed=None) -> obs`
- 盤面を全0にし、ランダムに2タイルを追加（2/4の確率含む）
- `score=0`
- `seed` が渡されたら内部RNGを初期化
- 戻り値 `obs` は `board.copy()` を返す（参照共有禁止）

### 2.4 `step(action) -> (obs, reward, done, info)`
処理順序（重要）:
1) 方向に応じて行/列を取り出し、**スライド＋マージ**して新しい盤面を作る  
2) 盤面が変化した場合のみ、新規タイルを1つ追加  
3) `reward` を確定（その手で合体したタイル値の合計）  
4) `done` 判定  
5) `info` を返す  

`info` 推奨キー:
- `invalid_move: bool`
- `moved: bool`（invalid_moveの否定でもよい）
- `score: int`（現在スコア）
- `max_tile: int`
- `won: bool`
- `spawned: tuple[int,int,int] | None`（(row,col,value)）
- `merged: list[dict]`（デバッグ用：どのラインでどの値が合体したか）

### 2.5 `render(mode="human")`
- まずはテキストでOK：
  - 4x4を整形してprint
  - `score`, `max_tile` 表示

### 2.6 `clone() -> Env`
- Expectimax用に **完全コピー**（board, score, rng state）を返す
- RNGの状態も複製し、`clone()`後の遷移が一致すること

---

## 3. 2048の正しさ（テスト要件）

### 3.1 スライド＋マージ（LEFT例）
- `[2,0,2,0] -> [4,0,0,0] reward=4`
- `[2,2,2,0] -> [4,2,0,0] reward=4`（連鎖マージ禁止の確認）
- `[2,2,2,2] -> [4,4,0,0] reward=8`
- `[4,4,2,2] -> [8,4,0,0] reward=12`
- `[2,0,0,0] -> [2,0,0,0] reward=0`（変化なし）

### 3.2 方向の整合
- UP/RIGHT/DOWN は LEFT の実装を回転/反転で再利用するか、同じ結果になること

### 3.3 生成タイル
- 空きセルにのみ出現
- 値が {2,4} のみであること

### 3.4 終了判定
- 満杯でも合体可能なら `done=False`
- 合体不可なら `done=True`

### 3.5 seed再現
- 同seed + 同行動列で最終盤面が一致

---

## 4. リポジトリ構成（Codexに作らせる成果物）
```
2048-ai/
  README.md
  pyproject.toml              # 依存: numpy, pytest, (任意) rich
  src/twenty48/
    __init__.py
    env.py                    # Twenty48Env
    mechanics.py              # ライン圧縮・マージの純関数
    utils.py                  # seed, clone補助
  tests/
    test_mechanics.py
    test_env_step.py
  scripts/
    play_random.py            # ランダムプレイで動作確認
    benchmark.py              # Nゲーム平均スコア
```

---

## 5. Codex向け 初回プロンプト（そのまま貼り付けて使用）

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

---

## 6. 開発フローのチェックリスト（Codex運用前提）

### 6.1 初期セットアップ
- [ ] 新規リポジトリ作成（例: `2048-ai`）
- [ ] `pyproject.toml` 作成（numpy/pytest）
- [ ] `src/` レイアウト採用、`pip install -e .` で動く
- [ ] `pytest -q` をCI相当として常時グリーン

### 6.2 実装順（壊れにくい）
- [ ] `mechanics.py` に「1行LEFT圧縮＋マージ」純関数を作る
- [ ] `test_mechanics.py` を先に通す
- [ ] `env.py` を作る（reset/step/done）
- [ ] `test_env_step.py` を通す（無効手、done、seed再現）
- [ ] `scripts/play_random.py` で目視確認
- [ ] `scripts/benchmark.py` で複数ゲームの平均が出る

### 6.3 品質・将来拡張
- [ ] `clone()` が RNG 状態まで一致する（探索で致命的）
- [ ] `step()` が **盤面変化の有無でspawnの有無が変わる**（無効手でspawnしない）
- [ ] `info` がデバッグに十分（invalid_move / spawned / max_tile）
- [ ] `board` の参照共有を避ける（返却時は `copy()`）

### 6.4 ベンチマーク基準（環境完成の合格ライン）
- [ ] ランダムプレイで例外が出ない（1万手程度）
- [ ] seed固定で完全再現できる（盤面一致）
- [ ] done判定が破綻しない（終局が来る）
