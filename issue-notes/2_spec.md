# クリップボードランチャー実装仕様書

## 概要
起動時のクリップボード内容を読み取り、TOML設定ファイルで定義された正規表現パターンにマッチするものを検出し、ユーザーがTUIで選択したアプリケーションを起動するPythonスクリプト。

## 技術スタック
- Python 3.11+ (Windows専用)
- 標準ライブラリ: `re`, `subprocess`, `msvcrt`, `tomllib`, `pathlib`, `sys`
- 外部ライブラリ: `pyperclip`
- 対象OS: Windows 10/11

## 動作フロー

### 1. 起動とクリップボード取得
- スクリプト起動時に`pyperclip.paste()`でクリップボード内容を取得
- クリップボードが空、またはテキストでない場合は「テキストが取得できません」と表示して終了

### 2. 一時ファイルへの保存
- クリップボード内容をTOMLで指定された`clipboard_temp_file`パスに保存
- エンコーディングはUTF-8 without BOM（`encoding='utf-8'`を指定）

### 3. パターンマッチング
- TOML設定ファイルの`[[patterns]]`セクションを上から順に評価
- 各パターンの`regex`でクリップボード内容全体に対してマッチング（`re.search`または`re.match`）
- マッチしたパターンをリストに格納

### 4. 結果表示と選択

#### マッチ数が0の場合
```
マッチするパターンがありません
```
と表示して終了

#### マッチ数が1以上の場合
以下の形式でTUIを表示:

```
クリップボード内容:
----------------------------------------
[1行目を80文字でカット]
[2行目を80文字でカット]
[3行目を80文字でカット]
----------------------------------------

マッチしたパターン:
a: [pattern name 1]
b: [pattern name 2]
c: [pattern name 3]
...

選択してください (a-[最後の文字], ESC: 終了): _
```

**表示仕様**
- クリップボード内容は先頭3行まで表示
- 各行は80文字でカット（超過分は`...`で省略表示）
- マッチしたパターンはa～zの順で割り当て（最大26個）
- パターン名は`[[patterns]]`の`name`フィールドを使用

### 5. キー入力受付
- `msvcrt.getch()`で1文字入力を待機（Windowsネイティブ）
- 入力がa～z（または対応する範囲）の場合:
  - 対応するパターンの`command`を取得
  - `{CLIPBOARD_FILE}`プレースホルダーを`clipboard_temp_file`のフルパスで置換
  - **Windows向けコマンド分割方法**:
    - 単純なスペース分割は使用しない（引用符やパスのスペース対応のため）
    - `subprocess.run(command, shell=True)`を使用
    - または手動で引用符を考慮した分割ロジックを実装
  - 例: `command = "notepad.exe {CLIPBOARD_FILE}"` → 置換後に実行
- ESCキー（`\x1b`または`b'\x1b'`）の場合: 何もせずプログラムを終了
- それ以外の入力: 無視して再度入力を待つ

**msvcrtの使用方法**
```python
import msvcrt
key = msvcrt.getch()  # bytes型で返される（例: b'a', b'\x1b'）
# a～z判定: b'a' <= key <= b'z'
# ESC判定: key == b'\x1b'
```

### 6. 終了
コマンド実行後、またはESC入力後にプログラムを終了

## TOML設定ファイル仕様

### ファイル名
`config.toml`（任意のディレクトリ、コマンドライン引数で指定。参考例は `examples/config.toml` を参照）

### 構造例
```toml
# 一時ファイルパス（クリップボード内容を保存）
# Windowsパス形式（スラッシュまたはバックスラッシュ）
clipboard_temp_file = "C:/temp/clipboard_content.txt"
# または clipboard_temp_file = "C:\\temp\\clipboard_content.txt"

# パターン定義（配列形式）
[[patterns]]
name = "URL"
regex = "^https?://.*"
command = "start chrome.exe {CLIPBOARD_FILE}"

[[patterns]]
name = "ローカルファイルパス"
regex = "^[A-Z]:\\\\.+"
command = "explorer.exe /select,{CLIPBOARD_FILE}"

[[patterns]]
name = "メールアドレス"
regex = "^[\\w.+-]+@[\\w.-]+\\.[a-z]{2,}$"
command = "start outlook.exe /a {CLIPBOARD_FILE}"

[[patterns]]
name = "GitHub Issue"
regex = "#\\d+"
command = "notepad.exe {CLIPBOARD_FILE}"

[[patterns]]
name = "カスタムスクリプト"
regex = "^CUSTOM:"
command = "python.exe process.py --input {CLIPBOARD_FILE} --output {CLIPBOARD_FILE}.result"
```

### フィールド定義

#### グローバル設定
- `clipboard_temp_file` (文字列, 必須): クリップボード内容を保存する一時ファイルのフルパス

#### `[[patterns]]`セクション
- `name` (文字列, 必須): パターンの表示名（TUIで表示される）
- `regex` (文字列, 必須): マッチング用の正規表現パターン
- `command` (文字列, 必須): 実行するコマンドライン
  - プレースホルダー`{CLIPBOARD_FILE}`を使用して一時ファイルパスを指定
  - 例: `"notepad.exe {CLIPBOARD_FILE}"`
  - 例: `"python.exe script.py --input {CLIPBOARD_FILE}"`
  - プレースホルダーは複数回使用可能
  - プレースホルダーがない場合はコマンドのみ実行される

## エラーハンドリング

### 必須のエラー処理
1. TOML設定ファイルが存在しない場合: エラーメッセージを表示して終了
2. TOMLの構文エラー: エラー内容を表示して終了
3. `clipboard_temp_file`への書き込み失敗: エラーメッセージを表示して終了
4. コマンド実行失敗: エラーメッセージを表示（ただしプログラムは終了しない）

### エラーメッセージ例
```
エラー: 設定ファイルが見つかりません (config.toml)
エラー: クリップボード内容の保存に失敗しました
エラー: コマンドの実行に失敗しました (chrome.exe)
```

## 実装上の注意点

### パフォーマンス
- 常駐せず、起動の都度実行するため起動速度を重視
- 不要なライブラリのインポートは避ける
- Python 3.11+の`tomllib`を使用（外部依存なし）

### Windows固有の考慮事項
- パス区切りは`\`と`/`両方に対応（`pathlib.Path`を使用）
- 一時ファイルのエンコーディングはUTF-8 without BOM（アプリケーション互換性を優先）
- コマンド実行時のコンソールウィンドウ制御（`subprocess.CREATE_NO_WINDOW`フラグ）
- `msvcrt.getch()`はbytes型を返すため、文字比較時は`b'a'`形式を使用

### セキュリティ
- **Windows環境でのコマンド実行**:
  - `shell=True`使用時は信頼できる設定ファイルからのみコマンドを読み込む
  - ユーザー入力を直接コマンドに埋め込まない（クリップボード内容はファイル経由で渡す）
  - パスインジェクション対策として、`clipboard_temp_file`のパスを検証
- 正規表現の`re.compile()`でエラーが出る場合はスキップし、警告を表示

### ユーザビリティ
- TUIはシンプルで直感的
- ESCでいつでも安全に終了可能
- マッチしたパターンが多い場合（26個超）は警告を表示

## 拡張性の考慮
将来的な拡張のために以下を考慮した設計とする:
- TOMLに追加フィールドを容易に追加可能な構造
- プレースホルダーの追加（例: `{CLIPBOARD_CONTENT}`, `{MATCH_GROUP_1}`など）
- 正規表現のキャプチャグループを利用した動的なコマンド生成
- 環境変数の展開（例: `{HOME}`, `{TEMP}`など）

## テストケース

### 基本動作
1. URL（http/https）のマッチとブラウザ起動
2. ローカルファイルパスのマッチとエクスプローラー起動
3. 複数パターンマッチ時のTUI表示と選択
4. マッチなしの場合のメッセージ表示
5. ESCキーでの終了
6. 改行を含むクリップボード内容のマッチと処理

### エッジケース
1. 空のクリップボード
2. 非常に長いクリップボード内容（数千行）
3. 正規表現が全てマッチしない場合
4. 無効な正規表現パターンがTOMLに含まれる場合

## 実装優先順位
1. コア機能（クリップボード取得、パターンマッチ、TUI、コマンド実行）
2. エラーハンドリング
3. 表示の調整（80文字カット、3行制限）
4. テストとデバッグ
