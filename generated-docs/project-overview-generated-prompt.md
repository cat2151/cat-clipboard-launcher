Last updated: 2025-11-10


# プロジェクト概要生成プロンプト（来訪者向け）

## 生成するもの：
- projectを3行で要約する
- プロジェクトで使用されている技術スタックをカテゴリ別に整理して説明する
- プロジェクト全体のファイル階層ツリー（ディレクトリ構造を図解）
- プロジェクト全体のファイルそれぞれの説明
- プロジェクト全体の関数それぞれの説明
- プロジェクト全体の関数の呼び出し階層ツリー

## 生成しないもの：
- Issues情報（開発者向け情報のため）
- 次の一手候補（開発者向け情報のため）
- ハルシネーションしそうなもの（例、存在しない機能や計画を勝手に妄想する等）

## 出力フォーマット：
以下のMarkdown形式で出力してください：

```markdown
# Project Overview

## プロジェクト概要
[以下の形式で3行でプロジェクトを要約]
- [1行目の説明]
- [2行目の説明]
- [3行目の説明]

## 技術スタック
[使用している技術をカテゴリ別に整理して説明]
- フロントエンド: [フロントエンド技術とその説明]
- 音楽・オーディオ: [音楽・オーディオ関連技術とその説明]
- 開発ツール: [開発支援ツールとその説明]
- テスト: [テスト関連技術とその説明]
- ビルドツール: [ビルド・パース関連技術とその説明]
- 言語機能: [言語仕様・機能とその説明]
- 自動化・CI/CD: [自動化・継続的統合関連技術とその説明]
- 開発標準: [コード品質・統一ルール関連技術とその説明]

## ファイル階層ツリー
```
[プロジェクトのディレクトリ構造をツリー形式で表現]
```

## ファイル詳細説明
[各ファイルの役割と機能を詳細に説明]

## 関数詳細説明
[各関数の役割、引数、戻り値、機能を詳細に説明]

## 関数呼び出し階層ツリー
```
[関数間の呼び出し関係をツリー形式で表現]
```
```


以下のプロジェクト情報を参考にして要約を生成してください：

## プロジェクト情報
名前: 
説明: # cat-clipboard-launcher

- 3行でまとめ
  - 常駐せず、明示的に起動して使うランチャ
  - A～Zキーで選ぶ
  - 選択肢はtoml設定ファイルで指定したregexでmatchしたものが表示される、つまりクリップボード内容で自動判別

- 操作イメージ
  - テキストエディタで、思いつきを書く
  - 先頭に指示commandを書く
  - それらを範囲選択コピーする
  - cat-clipboard-launcherを起動する
    - ※例えば無難な操作としては、ホットキーでコマンドラインランチャを起動し、そこでaliasを入力する
  - cat-clipboard-launcher画面が表示されたことを確認する
  - Aキー～Zキーを押して、何をlaunchするか選ぶ
  - 目的のアプリがlaunchされたことを確認する
    - 例えば、テキストエディタに思いつきで書いたMMLが音楽として演奏されたことを確認する

- 開発の動機
  - に関する備忘
    - 認知負荷、精神的スタック
      - 思いついたものをすぐ書くほうが楽
        - 精神的スタックに「音楽アプリを起動する」などを積む必要がないので
          - 思いついた瞬間にテキストエディタにMMLを書いたら、
            - そのあとでそのMMLを食わせるための音楽アプリを起動するほうが、
              - すぐ書ける、点で優れている
                - ※一長一短であり、使い分けすればよいものであるので、
                  - 常にこのムーブをすべきという主張ではない点に留意されたい
  - 常駐しない
    - シンプル
      - 「クリップボードにコピーされたらその瞬間に自動判別してアプリが動くか？それとも自動判別は今はoffか？」
        - をuserが常に意識する、現在がどちらのmodeなのか、を精神的スタックを使って意識する、
          - というのは、ステートフルであり、
            - そのぶん認知負荷が高い
              - user体験としては、「常に手動起動する」と認知しているほうが認知負荷が低く、楽である
                - これは筆者の経験則であり、人それぞれであることには留意されたい（このtext全般がそう）
  - 検証用
    - これで実際のuser体験がどうなるかを検証するくらいの目的
    - なのでこれで格段に便利になるかも、みたいな想定はあまりしていない
    - 1年数回使うくらいの頻度に落ち着くか、完全にボツにして違う運用にするか、といった可能性も想定している

- 開発の備忘
  - issue #2 の仮仕様は、Claudeに壁打ちして生成させたもの

### 備忘、用途、事例
- webのcodeをそのまま実行したいとき便利
  - 手順
    - クリップボードに入れるボタンをクリック
    - clipを起動
    - 自動認識で例えばpythonが候補に出るのでazキーで選ぶ
  - ※セキュリティリスクを考慮した上で、実行するかしないかを選ぶこと
  - ※短縮できるのは、localでsrcを開いて保存、pythonコマンドで実行、という操作
- 頻繁に使うtext filterを登録すると便利かもしれません
    - 例、頻繁に行う文字列加工処理を、好きなプログラミング言語でtext filterとして実装します
        - それをこのlauncherで呼び出せば、どんなアプリ上でテキストを書いていても、
            - 好きなプログラミング言語のtext filterでそれを加工できます
                - そのeditorの設定やscript APIを調査するのが億劫と感じたときに
                    - 特に、マイナーなeditorで、agentでなく人力でそれをやる必要がありそうなときに

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start Guide

cat-clipboard-launcherを最速で使い始める方法：

### 1. 必要最小限の設定ファイルを作成

プロジェクトのルートディレクトリ（`src/launcher.py`と同じ階層）に`config.toml`を作成し、**たった1行**追加するだけ：

```toml
patterns = [{name = "テキストエディタで開く", regex = ".*", command = "notepad.exe {CLIPBOARD_FILE}"}]
```

これで設定完了です！

### 2. 使ってみる

1. 何かテキストをクリップボードにコピーする
2. ランチャーを起動する：
   ```bash
   python src/launcher.py --config-filename config.toml
   ```
3. `a`キーを押してパターンを選択
4. メモ帳が起動してクリップボードの内容が表示されます

**注意事項：**
- `clipboard_temp_file`の設定は省略可能です（デフォルト：カレントディレクトリの`clipboard_content.txt`）
- パターンは最低1つ必要です

### より詳しい設定

複数のパターンを追加して、クリップボードの内容に応じて自動判別できます：

```toml
# clipboard_temp_fileは省略可（デフォルト：./clipboard_content.txt）

[[patterns]]
name = "URL"
regex = "^https?://.*"
command = "start chrome.exe {CLIPBOARD_FILE}"

[[patterns]]
name = "GitHub Issue"
regex = "#\\d+"
command = "notepad.exe {CLIPBOARD_FILE}"
```

## Configuration

Create or edit `config.toml` for your specific needs. You can use `examples/config.toml` as a reference template:

```toml
# Path where clipboard content will be saved temporarily
# OPTIONAL: Defaults to "./clipboard_content.txt" (in current directory)
clipboard_temp_file = "./clipboard_content.txt"

# Pattern definitions
[[patterns]]
name = "URL"
regex = "^https?://.*"
command = "start chrome.exe {CLIPBOARD_FILE}"

[[patterns]]
name = "GitHub Issue"
regex = "#\\d+"
command = "notepad.exe {CLIPBOARD_FILE}"

[[patterns]]
name = "Text Filter"
regex = "^FILTER:"
command = "python.exe filter.py --input {CLIPBOARD_FILE} --output {CLIPBOARD_FILE}.result"
output_file = "{CLIPBOARD_FILE}.result"
write_output_to_clipboard = true  # Output will be written back to clipboard
```

### Configuration Fields

- `clipboard_temp_file` (optional): Full path to temporary file for clipboard content
  - **Default**: `clipboard_content.txt` in the current directory
  - You can omit this field to use the default location
- `patterns` (required): Array of pattern definitions
  - `name`: Display name for the pattern
  - `regex`: Regular expression to match clipboard content
  - `command`: Command to execute (use `{CLIPBOARD_FILE}` as placeholder)
  - `output_file`: (Optional) Path to output file. Can use `{CLIPBOARD_FILE}` placeholder
  - `write_output_to_clipboard`: (Optional, default: `false`) When `true` and `output_file` is specified, the content will be written back to clipboard after command execution

## Running the Launcher

```bash
# The --config-filename argument is required
python src/launcher.py --config-filename path/to/config.toml

# Example with absolute path
python src/launcher.py --config-filename C:/Users/username/config.toml

# Example with relative path
python src/launcher.py --config-filename ./config.toml
```

**Note**: The `--config-filename` argument is required. There is no default configuration file.

## Usage Flow

1. Copy text to clipboard
2. Run the launcher
3. The launcher will:
   - Display first 3 lines of clipboard content (80 chars max per line)
   - Show matched patterns (a-z)
   - Wait for your choice
4. Press a-z to select a pattern, or ESC to exit
5. Selected command will be executed

## Example Workflow

1. Copy `https://github.com/example/repo` to clipboard
2. Run launcher
3. See "URL" pattern matched
4. Press 'a' to open in browser
5. Chrome opens with the clipboard content

## Testing

Run tests with:

```bash
pytest tests/test_launcher.py -v
```

## Development

Format and lint code:

```bash
# Format code
ruff format src/ tests/

# Fix linting issues
ruff check --fix src/ tests/
```


依存関係:
{}

## ファイル階層ツリー
📄 .editorconfig
📄 .gitignore
📁 .vscode/
  📊 settings.json
📄 LICENSE
📖 README.md
📖 REFACTORING.md
📄 _config.yml
📁 examples/
  📄 config.toml
📁 generated-docs/
📁 issue-notes/
  📖 2_spec.md
📄 pytest.ini
📄 requirements.txt
📄 ruff.toml
📁 src/
  📄 __init__.py
  📄 clipboard.py
  📄 config.py
  📄 executor.py
  📄 input_handler.py
  📄 launcher.py
  📄 pattern_matcher.py
  📄 tui.py
📁 tests/
  📄 __init__.py
  📄 test_launcher.py

## ファイル詳細分析


## 関数呼び出し階層
関数呼び出し階層を分析できませんでした

## プロジェクト構造（ファイル一覧）
.vscode/settings.json
README.md
REFACTORING.md
issue-notes/2_spec.md

上記の情報を基に、プロンプトで指定された形式でプロジェクト概要を生成してください。
特に以下の点を重視してください：
- 技術スタックは各カテゴリごとに整理して説明
- ファイル階層ツリーは提供された構造をそのまま使用
- ファイルの説明は各ファイルの実際の内容と機能に基づく
- 関数の説明は実際に検出された関数の役割に基づく
- 関数呼び出し階層は実際の呼び出し関係に基づく


---
Generated at: 2025-11-10 08:17:10 JST
