

================================================================================# 評価対象モデル別 分散分析結果
ベンチマーク: lightblue/tengu_bench

## サマリー

| 評価対象モデル | 従来分散 | 新形式分散 | 分散減少率 | 従来評価者数 | 新形式評価者数 |
|---------------|----------|------------|------------|-------------|-------------|
| gemini-2.5-pro | 0.0121 | 0.0015 | +87.5% | 7 | 5 |
| gemini-2.5-flash | 0.0166 | 0.0054 | +67.3% | 7 | 5 |
| gemini-2.5-flash-lite-preview-06-17 | 0.0746 | 0.0277 | +62.9% | 6 | 5 |
| gemini-2.5-pro-preview-05-06 | 0.0265 | 0.0125 | +52.7% | 6 | 5 |
| gemini-2.5-pro-preview-03-25 | 0.0085 | 0.0061 | +27.6% | 6 | 5 |
| gemini-2.5-pro-preview-06-05 | 0.0036 | 0.0086 | -139.7% | 6 | 5 |

**全体平均分散減少率: 56.4%**
- 従来形式平均分散: 0.0237
- 新形式平均分散: 0.0103
- 両形式を持つモデル数: 6

## 詳細分析

### gemini-2.5-pro

**従来形式（judge_*）**: 7 評価者
- 平均スコア: 9.10
- 標準偏差: 0.1101
- 分散: 0.0121
- 範囲: 9.02 - 9.26 (差: 0.24)
- 評価者: judge_gpt-4.1-mini, judge_gemini-2.5-flash-lite-preview-06-17, judge_gemini-2.0-flash, judge_gemini-2.5-pro, judge_gemini-2.5-flash, judge_o4-mini, judge_gemini-2.5-flash-preview-05-20

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 8.95
- 標準偏差: 0.0389
- 分散: 0.0015
- 範囲: 8.92 - 8.99 (差: 0.08)
- 評価者: gemini-2.5-pro, gpt-4.1-mini, gemini-2.5-flash-preview-05-20, gemini-2.5-flash, gemini-2.5-flash-lite-preview-06-17

**分散改善効果**: +87.5%
→ 構造化出力により評価者間の一貫性が向上

### gemini-2.5-flash

**従来形式（judge_*）**: 7 評価者
- 平均スコア: 8.71
- 標準偏差: 0.1289
- 分散: 0.0166
- 範囲: 8.62 - 8.98 (差: 0.36)
- 評価者: judge_gemini-2.5-flash-lite-preview-06-17, judge_gpt-4.1-mini, judge_gemini-2.0-flash, judge_o4-mini, judge_gemini-2.5-pro, judge_gemini-2.5-flash, judge_gemini-2.5-flash-preview-05-20

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 8.51
- 標準偏差: 0.0737
- 分散: 0.0054
- 範囲: 8.45 - 8.61 (差: 0.16)
- 評価者: gpt-4.1-mini, gemini-2.5-flash-lite-preview-06-17, gemini-2.5-pro, gemini-2.5-flash-preview-05-20, gemini-2.5-flash

**分散改善効果**: +67.3%
→ 構造化出力により評価者間の一貫性が向上

### gemini-2.5-flash-lite-preview-06-17

**従来形式（judge_*）**: 6 評価者
- 平均スコア: 7.58
- 標準偏差: 0.2732
- 分散: 0.0746
- 範囲: 7.36 - 8.03 (差: 0.67)
- 評価者: judge_gemini-2.5-flash-lite-preview-06-17, judge_gpt-4.1-mini, judge_gemini-2.0-flash, judge_gemini-2.5-pro, judge_gemini-2.5-flash, judge_gemini-2.5-flash-preview-05-20

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 7.47
- 標準偏差: 0.1665
- 分散: 0.0277
- 範囲: 7.27 - 7.71 (差: 0.44)
- 評価者: gpt-4.1-mini, gemini-2.5-flash-lite-preview-06-17, gemini-2.5-flash-preview-05-20, gemini-2.5-flash, gemini-2.5-pro

**分散改善効果**: +62.9%
→ 構造化出力により評価者間の一貫性が向上

### gemini-2.5-pro-preview-05-06

**従来形式（judge_*）**: 6 評価者
- 平均スコア: 9.07
- 標準偏差: 0.1629
- 分散: 0.0265
- 範囲: 8.89 - 9.38 (差: 0.48)
- 評価者: judge_gemini-2.5-flash-lite-preview-06-17, judge_gpt-4.1-mini, judge_gemini-2.5-pro, judge_gemini-2.5-flash, judge_gemini-2.5-flash-preview-05-20, judge_gemini-2.0-flash

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 8.90
- 標準偏差: 0.1120
- 分散: 0.0125
- 範囲: 8.84 - 9.10 (差: 0.26)
- 評価者: gpt-4.1-mini, gemini-2.5-pro, gemini-2.5-flash-preview-05-20, gemini-2.5-flash, gemini-2.5-flash-lite-preview-06-17

**分散改善効果**: +52.7%
→ 構造化出力により評価者間の一貫性が向上

### gemini-2.5-pro-preview-03-25

**従来形式（judge_*）**: 6 評価者
- 平均スコア: 9.21
- 標準偏差: 0.0920
- 分散: 0.0085
- 範囲: 9.14 - 9.38 (差: 0.24)
- 評価者: judge_gemini-2.5-flash-lite-preview-06-17, judge_gpt-4.1-mini, judge_gemini-2.5-pro, judge_gemini-2.0-flash, judge_gemini-2.5-flash, judge_gemini-2.5-flash-preview-05-20

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 8.96
- 標準偏差: 0.0783
- 分散: 0.0061
- 範囲: 8.89 - 9.09 (差: 0.20)
- 評価者: gpt-4.1-mini, gemini-2.5-pro, gemini-2.5-flash-preview-05-20, gemini-2.5-flash, gemini-2.5-flash-lite-preview-06-17

**分散改善効果**: +27.6%
→ 構造化出力により評価者間の一貫性が向上

### gemini-2.5-pro-preview-06-05

**従来形式（judge_*）**: 6 評価者
- 平均スコア: 9.13
- 標準偏差: 0.0600
- 分散: 0.0036
- 範囲: 9.05 - 9.23 (差: 0.18)
- 評価者: judge_gpt-4.1-mini, judge_gemini-2.5-flash-lite-preview-06-17, judge_gemini-2.5-flash, judge_gemini-2.5-pro, judge_gemini-2.5-flash-preview-05-20, judge_gemini-2.0-flash

**新形式（構造化出力）**: 5 評価者
- 平均スコア: 8.96
- 標準偏差: 0.0929
- 分散: 0.0086
- 範囲: 8.87 - 9.07 (差: 0.21)
- 評価者: gpt-4.1-mini, gemini-2.5-flash-lite-preview-06-17, gemini-2.5-pro, gemini-2.5-flash-preview-05-20, gemini-2.5-flash

**分散改善効果**: -139.7%
→ 構造化出力で分散が増加（要調査）
