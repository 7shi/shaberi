# 評価対象モデル別 分散分析結果
ベンチマーク: lightblue/tengu_bench

## サマリー

| 評価対象モデル | 従来分散 | 新形式分散 | 分散減少率 | 従来評価者数 | 新形式評価者数 |
|---------------|----------|------------|------------|-------------|-------------|
| gemini-2.5-pro | 0.0130 | 0.0015 | +88.4% | 5 | 5 |
| gemini-2.5-flash-lite-preview-06-17 | 0.0792 | 0.0299 | +62.3% | 5 | 5 |
| gemini-2.5-flash | 0.0215 | 0.0125 | +41.9% | 5 | 5 |
| gemini-2.5-pro-preview-05-06 | 0.0321 | 0.0345 | -7.5% | 5 | 5 |
| gemini-2.5-pro-preview-06-05 | 0.0044 | 0.0086 | -94.2% | 5 | 5 |
| gemini-2.5-pro-preview-03-25 | 0.0091 | 0.0181 | -99.5% | 5 | 5 |

**全体平均分散減少率: 34.0%**
- 従来形式平均分散: 0.0266
- 新形式平均分散: 0.0175
- 両形式を持つモデル数: 6

## 詳細分析

### gemini-2.5-pro

**従来形式（judge_*）**: 5 評価者
- 平均スコア: 9.14
- 標準偏差: 0.1142
- 分散: 0.0130
- 範囲: 9.02 - 9.26 (差: 0.24)
- 評価者: judge_gpt-4.1-mini, judge_gemini-2.5-flash-lite-preview-06-17, judge_gemini-2.0-flash, judge_gemini-2.5-pro, judge_gemini-2.5-flash

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 8.95
- 標準偏差: 0.0389
- 分散: 0.0015
- 範囲: 8.92 - 8.99 (差: 0.08)
- 評価者: gemini-2.5-pro, gpt-4.1-mini, gemini-2.5-flash, gemini-2.5-flash-lite-preview-06-17, gemini-2.0-flash

**分散改善効果**: +88.4%
→ 構造化出力により評価者間の一貫性が向上

### gemini-2.5-flash-lite-preview-06-17

**従来形式（judge_*）**: 5 評価者
- 平均スコア: 7.62
- 標準偏差: 0.2814
- 分散: 0.0792
- 範囲: 7.36 - 8.03 (差: 0.67)
- 評価者: judge_gemini-2.5-flash-lite-preview-06-17, judge_gpt-4.1-mini, judge_gemini-2.0-flash, judge_gemini-2.5-pro, judge_gemini-2.5-flash

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 7.51
- 標準偏差: 0.1728
- 分散: 0.0299
- 範囲: 7.27 - 7.71 (差: 0.44)
- 評価者: gpt-4.1-mini, gemini-2.0-flash, gemini-2.5-flash-lite-preview-06-17, gemini-2.5-flash, gemini-2.5-pro

**分散改善効果**: +62.3%
→ 構造化出力により評価者間の一貫性が向上

### gemini-2.5-flash

**従来形式（judge_*）**: 5 評価者
- 平均スコア: 8.74
- 標準偏差: 0.1468
- 分散: 0.0215
- 範囲: 8.62 - 8.98 (差: 0.36)
- 評価者: judge_gemini-2.5-flash-lite-preview-06-17, judge_gpt-4.1-mini, judge_gemini-2.0-flash, judge_gemini-2.5-pro, judge_gemini-2.5-flash

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 8.49
- 標準偏差: 0.1119
- 分散: 0.0125
- 範囲: 8.32 - 8.61 (差: 0.28)
- 評価者: gpt-4.1-mini, gemini-2.5-flash-lite-preview-06-17, gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash

**分散改善効果**: +41.9%
→ 構造化出力により評価者間の一貫性が向上

### gemini-2.5-pro-preview-05-06

**従来形式（judge_*）**: 5 評価者
- 平均スコア: 9.09
- 標準偏差: 0.1793
- 分散: 0.0321
- 範囲: 8.89 - 9.38 (差: 0.48)
- 評価者: judge_gemini-2.5-flash-lite-preview-06-17, judge_gpt-4.1-mini, judge_gemini-2.5-pro, judge_gemini-2.5-flash, judge_gemini-2.0-flash

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 8.84
- 標準偏差: 0.1858
- 分散: 0.0345
- 範囲: 8.57 - 9.10 (差: 0.53)
- 評価者: gpt-4.1-mini, gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite-preview-06-17, gemini-2.0-flash

**分散改善効果**: -7.5%
→ 構造化出力で分散が増加（要調査）

### gemini-2.5-pro-preview-06-05

**従来形式（judge_*）**: 5 評価者
- 平均スコア: 9.13
- 標準偏差: 0.0667
- 分散: 0.0044
- 範囲: 9.05 - 9.23 (差: 0.18)
- 評価者: judge_gpt-4.1-mini, judge_gemini-2.5-flash-lite-preview-06-17, judge_gemini-2.5-flash, judge_gemini-2.5-pro, judge_gemini-2.0-flash

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 8.96
- 標準偏差: 0.0929
- 分散: 0.0086
- 範囲: 8.87 - 9.07 (差: 0.21)
- 評価者: gpt-4.1-mini, gemini-2.5-flash-lite-preview-06-17, gemini-2.5-pro, gemini-2.0-flash, gemini-2.5-flash

**分散改善効果**: -94.2%
→ 構造化出力で分散が増加（要調査）

### gemini-2.5-pro-preview-03-25

**従来形式（judge_*）**: 5 評価者
- 平均スコア: 9.23
- 標準偏差: 0.0953
- 分散: 0.0091
- 範囲: 9.14 - 9.38 (差: 0.24)
- 評価者: judge_gemini-2.5-flash-lite-preview-06-17, judge_gpt-4.1-mini, judge_gemini-2.5-pro, judge_gemini-2.0-flash, judge_gemini-2.5-flash

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 8.92
- 標準偏差: 0.1346
- 分散: 0.0181
- 範囲: 8.72 - 9.09 (差: 0.38)
- 評価者: gpt-4.1-mini, gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite-preview-06-17, gemini-2.0-flash

**分散改善効果**: -99.5%
→ 構造化出力で分散が増加（要調査）
