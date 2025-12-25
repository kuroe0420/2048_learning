# 模倣学習 (Behavior Cloning) 仕様

## 目的
- Expectimax を教師として方策ネットに蒸留する
- 高速な推論で次の action を選択できるようにする

## データ形式 (npz)
- boards: (K, 4, 4) int16
- actions: (K,) uint8
- scores: (K,) int32
- rewards: (K,) int32
- max_tiles: (K,) int16
- dones: (K,) bool
- step_indices: (K,) int32
- seeds: (K,) int32
- depths: (K,) int16

## エンコーディング
- one-hot 方式
- チャネル数 = max_pow + 1 (0=empty, k=2^k)
- 値が max_pow を超える場合は max_pow にクランプ

## 学習手順
1) データ生成
   - `python scripts/generate_dataset.py --num-games 50 --depth 3 --out data/raw/dataset_small.npz --sample-prob 1.0`
2) 学習
   - `python scripts/train_policy.py --dataset data/raw/dataset_small.npz --epochs 5 --batch-size 256 --lr 1e-3 --val-ratio 0.1 --out-dir data/models`
3) 推論プレイ
   - `python scripts/play_policy.py --model data/models/policy_best.pt --seed 0`

## 再現性
- `--seed` を指定するとゲーム単位で seed を固定して再現可能

## 既知の限界
- 期待値探索は行わないため Expectimax より弱い
- 盤面分布が教師データに依存する
