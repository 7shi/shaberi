# Git: 新規ファイルとgit resetの動作について

## 概要

Gitにおいて、新規ファイル（new file）と既存ファイルの変更では、`git reset`コマンドの動作が異なります。この文書では、その違いと適切な操作方法について説明します。

なお、この対処法は`git status`の出力の中に書いてあります。

```
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
```

## 新規ファイルと既存ファイルの違い

### 既存ファイルの変更

既存ファイルに対する変更は、以下のコマンドでステージングから取り消すことができます：

```bash
# ソフトリセット（コミットを取り消すが、変更は保持）
git reset --soft HEAD

# 結果：ステージングから外れて「Changes not staged for commit」になる
```

### 新規ファイル（new file）

新規ファイルは、`git reset --soft`では取り消すことができません。以下のコマンドを使用する必要があります：

```bash
# 方法1: restore --stagedを使用
git restore --staged <file>

# 方法2: resetを使用（HEADを指定）
git reset HEAD <file>

# すべてのファイルを対象にする場合
git restore --staged .

# 結果：ステージングから外れて「Untracked files」になる
```

## 理由

この動作の違いは、Gitの内部構造に起因します：

1. **`git reset --soft`の役割**
   - コミット履歴を操作するコマンド
   - HEADの位置を移動させる
   - 既存のGit履歴に存在するファイルのみを扱う

2. **新規ファイルの特性**
   - まだGitの履歴に存在しない
   - インデックス（ステージングエリア）にのみ存在
   - コミット履歴の操作では扱えない

3. **`restore --staged`の役割**
   - 純粋にステージングエリアを操作
   - Git履歴に関係なく、インデックスの内容を変更
   - 新規ファイルも既存ファイルも同様に扱える

## 実例

```bash
# 初期状態
$ git status
Changes to be committed:
  new file:   data/new_file.json
  modified:   existing_file.py

# git reset --soft HEADを実行
$ git reset --soft HEAD

# 結果：新規ファイルはステージングに残る
$ git status
Changes to be committed:
  new file:   data/new_file.json
Changes not staged for commit:
  modified:   existing_file.py

# restore --stagedで新規ファイルも取り消し
$ git restore --staged .

# 結果：すべてがステージングから外れる
$ git status
Changes not staged for commit:
  modified:   existing_file.py
Untracked files:
  data/new_file.json
```

## ベストプラクティス

1. **統一的な操作**
   - `git restore --staged .`を使用すれば、新規・既存問わずすべてのファイルをステージングから外せる

2. **個別ファイルの操作**
   - 特定のファイルのみを扱う場合は、ファイル名を明示的に指定

3. **状態の確認**
   - 操作前後で`git status`を実行し、期待通りの結果になっているか確認

## 関連コマンド

- `git add`: ファイルをステージングに追加
- `git status`: 現在の状態を確認
- `git diff --staged`: ステージングされた変更を確認
- `git reset --mixed`: デフォルトのreset（ステージングと作業ディレクトリから変更を取り消し）
- `git reset --hard`: すべての変更を破棄（要注意）

## まとめ

新規ファイルのステージングを取り消す場合は、`git reset --soft`ではなく`git restore --staged`を使用する必要があります。これはGitの内部構造に起因する仕様であり、理解しておくことで適切なGit操作が可能になります。