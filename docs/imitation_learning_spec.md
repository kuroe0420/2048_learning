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
   - 生成の高速化: `--max-cells 2` や `--max-steps 2000` を指定可能
2) 学習
   - `python scripts/train_policy.py --dataset data/raw/dataset_small.npz --epochs 5 --batch-size 256 --lr 1e-3 --val-ratio 0.1 --out-dir data/models --device auto`
3) 推論プレイ
   - `python scripts/play_policy.py --model data/models/policy_best.pt --seed 0 --device auto`

## 再現性
- `--seed` を指定するとゲーム単位で seed を固定して再現可能
- `--device auto` で CUDA が利用可能なら GPU を使用

## 既知の限界
- 期待値探索は行わないため Expectimax より弱い
- 盤面分布が教師データに依存する

## 検証結果と考察
### 実測結果（seed=0, device=auto）
- 教師データ: num-games=1, depth=1, sample-prob=0.2 / 学習: epochs=3, batch=64, val=0.2  
  → 推論スコア: Final score=736, max_tile=64
- 教師データ: num-games=5, depth=2, sample-prob=1.0 / 学習: epochs=10, batch=128, val=0.2  
  → 推論スコア: Final score=712, max_tile=64
- 教師データ: num-games=20, depth=2, max-cells=2, max-steps=2000 / 学習: epochs=15, batch=256, val=0.1  
  → 推論スコア: Final score=396, max_tile=32
- 教師データ: num-games=5, depth=3, max-cells=2, max-steps=2000 / 学習: epochs=20, batch=256, val=0.1  
  → 推論スコア: Final score=384, max_tile=32

### 考察
- データ量が少ないと学習が不安定で、推論スコアは Expectimax より大きく劣る
- 低サンプリング/低ゲーム数では分布が偏り、方策が特定の手に寄りやすい
- Expectimax 教師生成の計算コストが高く、depth を上げるほどデータ量確保が難しい
- 高速化（max-cells, max-steps）は生成を進めやすくするが、教師の質が下がる可能性がある

### 次の改善案
- depth=2 のまま num-games を 50〜100 に増やす（量の確保）
- depth=3 で num-games を 10〜20 に増やす（質の確保）
- 学習のエポック増加やバッチサイズ調整で安定化を狙う
