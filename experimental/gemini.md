# gemini.py - Gemini API クライアント

## 設計思想

### 1. シンプルで直感的なAPI
Google Gemini APIの複雑さを隠蔽し、シンプルで使いやすいインターフェースを提供。`print`関数と同じ`file`パラメータでストリーミング出力を制御。

### 2. 思考プロセスの透明性
Gemini 2.5の思考機能を活用し、AIの推論過程を可視化。思考プロセスと最終回答を分離して取得可能。

### 3. 堅牢性とリトライ機能
APIエラー（429, 500, 503）に対する自動リトライ機能を内蔵。レート制限時は適切な待機時間を設定。

### 4. 柔軟な出力制御
ストリーミング出力の有効/無効化、出力先の変更に対応。CLI用途からバッチ処理まで幅広く対応。

## 主要関数

### `generate_content_retry_with_thoughts()`
思考プロセスと回答を分離して取得する関数。

```python
thoughts, text = generate_content_retry_with_thoughts(
    model="gemini-2.5-pro-preview-06-05",
    config=config_text,
    contents=[{"role": "user", "parts": [{"text": "質問内容"}]}],
    include_thoughts=True,        # 思考プロセスを含める
    thinking_budget=None,         # 思考時間の制限（オプション）
    file=sys.stdout              # 出力先（None で無効化）
)
```

**戻り値**: `(thoughts: str, text: str)` のタプル
- `thoughts`: AIの思考プロセス
- `text`: 最終的な回答

### `generate_content_retry()`
互換性維持のためのラッパー関数。

```python
text = generate_content_retry(
    model="gemini-2.5-flash-preview-05-20",
    config=config_text,
    contents=[{"role": "user", "parts": [{"text": "質問内容"}]}],
    include_thoughts=True,
    thinking_budget=None,
    file=sys.stdout
)
```

**戻り値**: `str` - 最終的な回答のみ

## 設定とスキーマ

### 基本設定
```python
# テキスト出力用
config_text = types.GenerateContentConfig(
    response_mime_type="text/plain",
)

# JSON出力用（スキーマ指定）
config_json = config_from_schema_string('''
{
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "confidence": {"type": "number"}
    },
    "required": ["answer", "confidence"]
}
''')
```

### スキーマ関数
```python
# JSONスキーマ文字列から設定を生成
config = config_from_schema_string(schema_json_string)

# スキーマファイルから設定を生成
config = config_from_schema("schema.json")
```

## 出力制御

### 標準出力（デフォルト）
```python
text = generate_content_retry(model, config, contents)
# 思考プロセスと回答がリアルタイムで表示される
```

### 出力無効化
```python
text = generate_content_retry(model, config, contents, file=None)
# 画面出力なし、結果のみ取得
```

### ファイル出力
```python
with open("conversation.txt", "w", encoding="utf-8") as f:
    text = generate_content_retry(model, config, contents, file=f)
# ファイルに思考プロセスと回答を保存
```

### ログファイル出力
```python
import sys
with open("debug.log", "w", encoding="utf-8") as log_file:
    thoughts, text = generate_content_retry_with_thoughts(
        model, config, contents, 
        file=log_file  # ログファイルに詳細を記録
    )
    print(f"結果: {text}")  # 結果のみコンソールに表示
```

## エラーハンドリング

### 自動リトライ対象エラー
- **429**: レート制限 → `retryDelay`に従って待機
- **500**: サーバーエラー → 15秒待機後リトライ
- **502**: Bad Gateway → 15秒待機後リトライ
- **503**: サービス利用不可 → 15秒待機後リトライ

### リトライ動作
- 最大5回までリトライ
- 各試行間で適切な待機時間を設定
- 最終試行時は待機なし
- 全試行失敗時は`RuntimeError`

## 思考機能の活用

### 思考プロセスの分析
```python
thoughts, answer = generate_content_retry_with_thoughts(
    model, config, contents, file=None
)

# 思考プロセスを分析
if "数学" in thoughts:
    print("数学的推論を使用")
if "step" in thoughts.lower():
    print("段階的思考を実行")

print(f"最終回答: {answer}")
```

### 思考時間の制御
```python
# 短時間での回答が必要な場合
quick_answer = generate_content_retry(
    model, config, contents,
    thinking_budget=30,  # 30秒以内の思考時間
    file=None
)
```

## ファイル操作

### ファイルアップロード
```python
# 画像ファイルをアップロード
image_file = upload_file("image.jpg", "image/jpeg")

contents = [
    {"role": "user", "parts": [
        {"text": "この画像について説明してください"},
        {"fileData": {"mimeType": image_file.mime_type, "fileUri": image_file.uri}}
    ]}
]

text = generate_content_retry(model, config, contents)

# 使用後はファイルを削除
delete_file(image_file)
```

## 利用例

### 対話システム
```python
def chat_with_gemini():
    while True:
        user_input = input("質問: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        contents = [{"role": "user", "parts": [{"text": user_input}]}]
        
        print("\n🤖 Gemini:")
        answer = generate_content_retry(
            model="gemini-2.5-pro-preview-06-05",
            config=config_text,
            contents=contents,
            include_thoughts=True
        )
        print()
```

### バッチ処理
```python
questions = ["質問1", "質問2", "質問3"]
results = []

for i, question in enumerate(questions):
    contents = [{"role": "user", "parts": [{"text": question}]}]
    
    # 進捗表示のためファイル出力
    with open(f"log_{i+1}.txt", "w", encoding="utf-8") as log:
        thoughts, answer = generate_content_retry_with_thoughts(
            model, config, contents, file=log
        )
    
    results.append({
        "question": question,
        "thoughts": thoughts,
        "answer": answer
    })
    
    print(f"完了: {i+1}/{len(questions)}")
```

## モデル一覧

```python
models = [
    "gemini-2.5-flash-preview-05-20",    # 高速、低コスト
    "gemini-2.5-pro-preview-06-05",     # 高性能、思考機能対応
]

default_model = models[0]  # Flash をデフォルトに設定
```

## 注意事項

1. **環境変数**: `GEMINI_API_KEY` の設定が必要
2. **エンコーディング**: ファイル出力時は UTF-8 を推奨
3. **リソース管理**: アップロードファイルは使用後に削除
4. **レート制限**: 429エラー時は自動的に待機するが、適切な間隔での利用を推奨
5. **思考機能**: Gemini 2.5 Pro のみ対応、Flash では利用不可