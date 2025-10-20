# cat-clipboard-launcher

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
[[patterns]]
name = "テキストエディタで開く"
regex = ".*"
command = "notepad.exe {CLIPBOARD_FILE}"
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

Create or edit `config.toml` in the same directory as the launcher script:

```toml
# Path where clipboard content will be saved temporarily
# OPTIONAL: Defaults to "./clipboard_content.txt" (in current directory)
clipboard_temp_file = "C:/temp/clipboard_content.txt"

# Pattern definitions
[[patterns]]
name = "URL"
regex = "^https?://.*"
command = "start chrome.exe {CLIPBOARD_FILE}"

[[patterns]]
name = "GitHub Issue"
regex = "#\\d+"
command = "notepad.exe {CLIPBOARD_FILE}"
```

### Configuration Fields

- `clipboard_temp_file` (optional): Full path to temporary file for clipboard content
  - **Default**: `clipboard_content.txt` in the current directory
  - You can omit this field to use the default location
- `patterns` (required): Array of pattern definitions
  - `name`: Display name for the pattern
  - `regex`: Regular expression to match clipboard content
  - `command`: Command to execute (use `{CLIPBOARD_FILE}` as placeholder)

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
