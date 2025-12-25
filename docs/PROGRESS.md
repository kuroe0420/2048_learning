# 進捗 (SSOT)

最終更新: 2025-12-25 22:31

## 完了
- 進捗共有の仕組みを追加（docs/PROGRESS.md, scripts/status.py, scripts/run_tests.py）
- README に進捗/テスト手順を追記
- scripts/status.py と scripts/run_tests.py の動作確認
- dev ブランチを作成
- 模倣学習パイプラインの追加（generate/train/play）
- 進捗SSOTの重複を解消（docs/PROGRESS.md に統一）
- 2048-ai_docs を docs/archive/2048-ai_docs に移動
- SSOT/アーカイブ方針を README と docs に明記
- dev を master に統合
- 現状アルゴリズムと実行方法の案内
- GPU利用可否の問い合わせに回答
- 学習/推論のGPU対応（auto/cuda）を追加
- 教師データ生成→学習→推論プレイの動作確認
- 推論スコア低下について確認依頼
- 教師データ生成・学習・推論の再実行と結果記録
- 教師データ生成の高速化オプションを追加
- Expectimax 実行結果を記録
- 教師データ高速化→再学習→推論評価を実行
- 検証結果と考察をドキュメントに整理
- GitHub で docs/ 内容が見えない件の確認依頼を受領
- 学習/推論ログの取得と要約を追加
- 改行/BOMの診断と修正を実施

## 作業中
- なし

## 次にやること
- なし

## ブロッカー
- なし

## 実行結果
- pytest: PASS (scripts/run_tests.py)
- scripts/run_tests.py: PASS
- scripts/status.py: 実行済み
- generate_dataset: num-games=1 depth=1 sample-prob=0.2 保存=dataset_small.npz
- train_policy: epochs=3 batch=64 lr=1e-3 val=0.2 device=auto
- play_policy: Final score=736 max_tile=64 (seed=0, device=auto)
- generate_dataset: num-games=5 depth=2 sample-prob=1.0 保存=dataset_d2_g5.npz
- train_policy: epochs=10 batch=128 lr=1e-3 val=0.2 device=auto
- play_policy: Final score=712 max_tile=64 (seed=0, device=auto)
- play_expectimax: depth=3 Final score=3172 max_tile=256
- generate_dataset: num-games=20 depth=2 max-cells=2 max-steps=2000 保存=dataset_d2_g20_fast.npz
- train_policy: epochs=15 batch=256 lr=1e-3 val=0.1 device=auto
- play_policy: Final score=396 max_tile=32 (seed=0, device=auto)
- generate_dataset: num-games=5 depth=3 max-cells=2 max-steps=2000 保存=dataset_d3_g5_fast.npz
- train_policy: epochs=20 batch=256 lr=1e-3 val=0.1 device=auto
- play_policy: Final score=384 max_tile=32 (seed=0, device=auto)

## 進捗ブロック
```
# PROGRESS_UPDATE
updated: 2025-12-25 22:31
branch: master
commit: 7ab27fb chore: normalize docs newlines and update progress
tests: PASS
artifacts: train_last.log=present, play_policy_summary.json=present
next: - なし
blockers: - なし
```

## 変更点サマリ
- docs/PROGRESS.md をSSOT化し重複を解消
- docs/archive/2048-ai_docs に移動
- README/docs にSSOT/アーカイブ方針を追記
- dev_checklist に進捗/模倣学習項目を追加
- dev を master に統合

## ログ取得
- train command: `python scripts/train_policy.py --dataset data/raw/dataset_small.npz --epochs 5 --batch-size 256 --lr 1e-3 --val-ratio 0.1 --out-dir data/models --seed 0`
- play command: `python scripts/play_policy.py --model data/models/policy_best.pt --seed 0`
- train final: train_loss=1.323253 val_loss=1.388315 val_acc=0.299204
- train best: val_loss=1.375633 val_acc=0.303754
- play summary: final_score=1572 max_tile=128 invalid_rate=0.0 steps=156
- artifacts: `.artifacts/train_last.log`, `.artifacts/train_metrics.csv`, `.artifacts/play_policy_seed0.log`, `.artifacts/play_policy_summary.json`
