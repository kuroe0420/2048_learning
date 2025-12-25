# 2048 AI 開発フロー チェックリスト（Python環境・Codex運用前提）

## 初期セットアップ
- [ ] 新規リポジトリ作成（例: `2048-ai`）
- [ ] `pyproject.toml` 作成（numpy/pytest）
- [ ] `src/` レイアウト採用、`pip install -e .` で動く
- [ ] `pytest -q` をCI相当として常時グリーン

## 実装順（壊れにくい）
- [ ] `mechanics.py` に「1行LEFT圧縮＋マージ」純関数を作る
- [ ] `test_mechanics.py` を先に通す
- [ ] `env.py` を作る（reset/step/done）
- [ ] `test_env_step.py` を通す（無効手、done、seed再現）
- [ ] `scripts/play_random.py` で目視確認
- [ ] `scripts/benchmark.py` で複数ゲームの平均が出る

## 品質・将来拡張
- [ ] `clone()` が RNG 状態まで一致する（探索で致命的）
- [ ] `step()` が **盤面変化の有無でspawnの有無が変わる**（無効手でspawnしない）
- [ ] `info` がデバッグに十分（invalid_move / spawned / max_tile）
- [ ] `board` の参照共有を避ける（返却時は `copy()`）

## 合格ライン（環境完成）
- [ ] ランダムプレイで例外が出ない（1万手程度）
- [ ] seed固定で完全再現できる（盤面一致）
- [ ] done判定が破綻しない（終局が来る）
