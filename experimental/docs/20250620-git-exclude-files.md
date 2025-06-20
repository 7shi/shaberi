# Gitの特定のコミットからファイルを除外する手順

## 概要

既にコミット済みの履歴から特定のファイルを除外する方法をまとめたガイドです。本ドキュメントは実際のプロジェクトでREADME.mdとdocs/README.mdを誤ってコミットしてしまった際の修正作業を基に作成されています。

## 前提知識：Git操作の基本概念

### detached HEAD
- 特定のコミットに直接checkoutした状態
- ブランチから切り離された状態で作業可能
- 一時的な修正作業に適している

### rebase
- コミット履歴を書き換える操作
- `rebase --onto`: 特定のコミット範囲を別の位置に移動
- 複雑な履歴では予期しない結果になる場合がある

### cherry-pick
- 特定のコミットを現在のブランチに適用
- 一つずつ確実にコミットを復元可能
- エラー時の対処が容易

### reflog
- Gitの全操作履歴を記録
- 削除されたコミットも一定期間追跡可能
- 失われたコミットの復元に必須

## 状況の確認

### 1. 対象コミットの特定
```bash
# コミット履歴を確認
git log --oneline

# 特定のコミットの内容を確認
git show <commit-hash> --name-only
```

### 2. 除外対象ファイルの確認
```bash
# 特定のコミットに含まれるファイル一覧
git show <commit-hash> --name-only

# 例：963ed30の場合
git show 963ed30 --name-only
# experimental/README.md        ← 除外したい
# experimental/docs/README.md   ← 除外したい
# experimental/dump_questions.py ← 保持したい
# ...
```

## 手順1: detached HEADで修正コミットを作成

### ステップ1: 対象コミットにcheckout
```bash
# 修正したいコミットに直接移動
git checkout <commit-hash>
# 例：git checkout 963ed30
```

### ステップ2: コミットを一時的に取り消し
```bash
# コミットを取り消してファイルをワーキングディレクトリに戻す
git reset HEAD~1
```

### ステップ3: 必要なファイルのみを再ステージング
```bash
# 除外したいファイル以外をadd
git add <keep-file1> <keep-file2> ...

# 例：README.mdを除外してdump_questions.py関連のみを追加
git add 1tengu.json 2elyza.json 3mt.json analyze_evaluations.md analyze_evaluations.py dump_questions.md dump_questions.py
```

### ステップ4: 修正されたコミットを作成
```bash
# 元のコミットメッセージで再コミット
git commit -m "元のコミットメッセージ"
# 例：git commit -m "shaberi3データセットの分類・抽出ツールを追加"
```

### ステップ5: 新しいコミットハッシュを記録
```bash
# 新しいコミットハッシュを確認・記録
git log --oneline | head -1
# 例：0d0ec38 shaberi3データセットの分類・抽出ツールを追加
```

## 手順2: cherry-pickによる安全な履歴再構築（推奨）

修正されたコミットから後続の履歴を再構築する確実な方法です。

### ステップ6: 修正されたコミット位置に移動
```bash
# まず修正されたコミットまでreset
git reset --hard <new-commit>
# 例：git reset --hard 0d0ec38
```

### ステップ7: reflogで失われたコミットを確認
```bash
# 失われたコミットハッシュを特定
git reflog | head -20
```

### ステップ8: 必要なコミットを順番にcherry-pick
```bash
# 必要なコミットを順番にcherry-pick
git cherry-pick <commit1>
git cherry-pick <commit2>
git cherry-pick <commit3>
```

### 実例（本プロジェクトでの復元順序）
```bash
git cherry-pick cf14602  # conv_tengu.py
git cherry-pick 00afac5  # check_criteria.py  
git cherry-pick 6438b23  # md_to_schema.py
git cherry-pick b333640  # tengu-000.py
git cherry-pick 15bd983  # tengu.py
git cherry-pick 4591f4d  # score_tool.py
git cherry-pick 239b9eb  # totals_to_csv.py

# 新しいファイルは手動で追加
git add merge_csv.md merge_csv.py
git commit -m "CSVファイルマージツールを追加"
```

## 失敗例：rebase --ontoを使った履歴置き換え

実際のプロジェクトで試行した方法ですが、複雑な履歴では正しく動作しませんでした。

### 試行した手順
```bash
# 元のブランチに戻る
rm README.md docs/README.md  # 不要なuntrackedファイルを削除
git checkout experimental

# 履歴を再構築（失敗）
git rebase --onto 0d0ec38 963ed30~1 experimental
```

### 発生した問題
- 重複コミットが発生
- 履歴の順序が混乱
- 予期しないコミットの消失
- トラブルシューティングが困難

### 失敗の原因
- 複雑な履歴構造での依存関係
- rebase --ontoの動作の予測困難性
- 後続コミットとの関係性

## 代替手順: インタラクティブリベース（小規模な修正用）

### より簡単な方法（後続コミットが少ない場合）
```bash
# 作業前にstash
git stash

# インタラクティブリベース開始
git rebase -i <commit-hash>~1

# エディタで該当行を 'pick' から 'edit' に変更
# リベースが停止したら：
git reset HEAD~1
git add <keep-files-only>
git commit -C ORIG_HEAD
git rebase --continue
```

## filter-branch（歴史全体から除外する場合）

### 特定ファイルを歴史から完全削除
```bash
# 警告：これは歴史を完全に書き換えます
git filter-branch --index-filter 'git rm --cached --ignore-unmatch <file-path>' HEAD
```

## トラブルシューティング

### cherry-pick時のエラー対処

#### 空のコミットエラー
```bash
# エラーメッセージ：
# The previous cherry-pick is now empty, possibly due to conflict resolution.

# 対処法1：スキップ
git cherry-pick --skip

# 対処法2：手動でファイルを追加してコミット
git add <missing-files>
git commit -m "適切なコミットメッセージ"
```

#### コンフリクト発生時
```bash
# コンフリクトを手動で解決後
git add <resolved-files>
git cherry-pick --continue
```

### detached HEAD状態からの復帰
```bash
# 作業内容を保持したい場合
git branch <new-branch-name>  # 新しいブランチを作成
git checkout <original-branch>
git merge <new-branch-name>   # 必要に応じてマージ

# 作業内容を破棄したい場合
git checkout <original-branch>  # 直接元のブランチに戻る
```

## 重要な注意事項

### 1. 共有リポジトリでの作業
- 他の開発者と共有しているブランチでは**極めて慎重**に実行
- 履歴の書き換え後は `git push --force-with-lease` が必要
- チームメンバーに事前通知を行う

### 2. バックアップの作成
```bash
# 作業前に必ずブランチをバックアップ
git branch backup-<branch-name>
```

### 3. 作業の確認
```bash
# 各ステップで状況を確認
git status
git log --oneline | head -10
git show --name-only  # 現在のコミット内容
```

## まとめ

この手順により、特定のコミットから不要なファイルを除外し、履歴を適切に修正できます。ただし、履歴の書き換えは影響範囲が大きいため、十分な注意と事前準備が必要です。

### 推奨される実行順序
1. 状況確認とバックアップ作成
2. detached HEADでの修正コミット作成
3. cherry-pickによる履歴再構築【推奨】
4. 結果の検証

## 実際の経験から学んだポイント

### cherry-pickのメリット（推奨理由）
- 一つずつ確実にコミットを適用
- 各ステップで状況を確認可能
- エラーが発生しても局所的に対処可能
- 最終的な履歴が予測しやすい
- 複雑な履歴でも安全に動作

### rebase --ontoの問題点（避けるべき理由）
- 複雑な履歴では予期しない結果になりやすい
- 重複コミットが発生する可能性
- トラブルシューティングが困難
- 依存関係の把握が困難

### 成功の指標
- 除外したいファイルがコミット履歴から消えている
- 必要なファイルはすべて保持されている
- 後続のコミットが正しく復元されている
- コミットメッセージと順序が適切に保持されている