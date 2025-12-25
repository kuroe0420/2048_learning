# 2048 AI 開発フロー チェックリスト（Python環境・Codex運用前提）

## 初期セットアップ
- [x] 新規リポジトリ作成（例: `2048-ai`）
- [x] `pyproject.toml` 作成（numpy/pytest）
- [x] `src/` レイアウト採用、`pip install -e .` で動く
- [x] `pytest -q` を CI 相当として常時グリーン

## 実装（壊れにくい設計）
- [x] `mechanics.py` に「1行 LEFT 圧縮＋マージ」の純関数を作る
- [x] `test_mechanics.py` を先に通す
- [x] `env.py` を作る（reset/step/done）
- [x] `test_env_step.py` を通す（無効手、done、seed再現）
- [x] `scripts/play_random.py` で目視確認
- [x] `scripts/benchmark.py` で複数ゲームの平均スコアを出す

## 品質・拡張
- [x] `clone()` が RNG 状態まで一致する（探索で致命的）
- [x] `step()` は盤面変化の有無で spawn の有無が変わる（無効手で spawn しない）
- [x] `info` がデバッグに十分（invalid_move / spawned / max_tile）
- [x] `board` の参照共有を避ける（返却時 `copy()`）

## 合格ライン（環境の品質）
- [x] ランダムプレイで例外が出ない（目安 1,000 手程度）
- [x] seed 固定で完全再現できる（盤面一致）
- [x] done 判定が破綻しない（終局が来る）

## 進捗・運用
- [x] 進捗共有の仕組み導入完了（docs/PROGRESS.md, scripts/status.py）
- [x] 模倣学習パイプライン導入完了（generate/train/play）
