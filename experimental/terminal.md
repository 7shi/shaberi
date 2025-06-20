# terminal.py - Markdown太字→ターミナル装飾変換モジュール

## 設計思想

### 目的
Markdown記法の`**太字**`をターミナル上でColoramaを使って視覚的に表現するためのユーティリティ。  
CLIアプリケーションでMarkdown形式のテキストを美しく表示することを目的としている。

### 設計原則

1. **堅牢性**: 不正な形式やタグの閉じ忘れに対して寛容
   - 改行時に自動的にスタイルをリセット
   - 文字列終端でのスタイル自動クローズ

2. **ストリーミング対応**: リアルタイム出力での使用を想定
   - `MarkdownStreamConverter`でチャンク単位の処理をサポート
   - バッファリングによる`*`の曖昧性解決

3. **プラットフォーム互換性**: 
   - Windows向けに`just_fix_windows_console()`を実行
   - 改行コードの正規化（CR/CRLF → LF）

### アーキテクチャ

```
入力: "**太字**の文字列"
     ↓
解析: ** の検出とトグル
     ↓
出力: Style.BRIGHT + "太字" + Style.NORMAL + "の文字列"
```

## API リファレンス

### 関数

#### `bold(text: str) -> str`
シンプルな太字変換関数。

**パラメータ:**
- `text`: 太字にしたい文字列

**戻り値:**
- Coloramaスタイルでラップされた文字列

**例:**
```python
print(bold("重要なメッセージ"))
# → Style.BRIGHT + "重要なメッセージ" + Style.NORMAL
```

#### `convert_markdown(text: str) -> str`
Markdownテキスト全体を一括変換する関数。

**パラメータ:**
- `text`: Markdown形式の文字列（`**太字**`を含む）

**戻り値:**
- Coloramaスタイルに変換された文字列

**動作:**
- `**` の検出でbright_modeをトグル
- 改行時に自動的にスタイルリセット
- 文字列終端で未クローズのスタイルを自動クローズ

**例:**
```python
text = "これは**重要な**情報です\n**別の行**です"
print(convert_markdown(text))
```

### クラス

#### `MarkdownStreamConverter`
ストリーミング処理用のMarkdown変換クラス。

**用途:**
- リアルタイム出力（例：LLMの応答ストリーム）
- 大きなテキストの分割処理

**メソッド:**

##### `__init__()`
コンバーターを初期化。

**内部状態:**
- `buffer`: 未処理の文字（主に末尾の`*`）
- `bright_mode`: 現在の太字モード状態

##### `feed(chunk: str) -> str`
テキストチャンクを処理して変換結果を返す。

**パラメータ:**
- `chunk`: 処理するテキストの断片

**戻り値:**
- 変換済みテキスト（Coloramaスタイル付き）

**特徴:**
- 末尾の`*`はバッファに保持（次のchunkで`**`判定）
- 改行での自動スタイルリセット

##### `flush() -> str`
バッファの残りを出力し、状態をリセット。

**戻り値:**
- バッファに残った文字とスタイルリセット

**使用例:**
```python
converter = MarkdownStreamConverter()
for chunk in streaming_chunks:
    print(converter.feed(chunk), end='')
print(converter.flush(), end='')  # 最後に必須
```

## 使用例

### 基本的な使用
```python
from terminal import convert_markdown

text = "**エラー**: ファイルが見つかりません"
print(convert_markdown(text))
```

### ストリーミング使用
```python
from terminal import MarkdownStreamConverter

converter = MarkdownStreamConverter()
chunks = ["**進行中", "**の処理", "\n完了しました"]

for chunk in chunks:
    print(converter.feed(chunk), end='')
print(converter.flush())
```

## 制限事項

1. **入れ子の装飾**: `***太字斜体***`のような複合装飾は未対応
2. **その他のMarkdown**: 見出し、リスト、コードブロック等は変換対象外
3. **エスケープ**: `\**`によるエスケープは未対応

## 技術詳細

### Colorama依存
- `Style.BRIGHT`: 太字開始
- `Style.NORMAL`: スタイルリセット
- `just_fix_windows_console()`: Windows互換性確保

### 状態管理
`MarkdownStreamConverter`は有限状態機械として実装：
- `bright_mode=False`: 通常モード
- `bright_mode=True`: 太字モード
- `buffer`: 保留中の文字（`*`の曖昧性解決用）