# VS CodeでAnaconda環境を作成し、requirements.txtをインストールする手順

## 目的

VS Code上で、Anaconda / Miniconda の仮想環境を作成し、その環境に `requirements.txt` のライブラリをインストールする。

---

## 前提

以下がインストール済みであること。

- Visual Studio Code
- Anaconda または Miniconda
- VS Code拡張機能 `Python`

VS Codeの拡張機能は、左側の Extensions から `Python` と検索してインストールする。

---

## 1. Anaconda環境を作成する

まず、VS Codeのターミナルを開く。

```bash
Terminal > New Terminal
```

またはショートカット：

```text
Ctrl + `
```

次に、Conda環境を作成する。

例：Python 3.11 の環境を `myenv` という名前で作る場合

```bash
conda create -n master_dbe_env python=3.11
```

確認が出たら `y` を入力する。

```bash
Proceed ([y]/n)? y
```

---

## 2. 作成した環境を有効化する

```bash
conda activate master_dbe_env
```

有効化されると、ターミナルの左側に環境名が表示される。

例：

```bash
(myenv) C:\Users\...
```

または macOS / Linux の場合：

```bash
(myenv) user@pc:~/project$
```

---

## 3. VS CodeでPython Interpreterを選択する

VS Codeで、作成したConda環境をPython実行環境として選択する。

手順：

1. `Ctrl + Shift + P` を押す
2. `Python: Select Interpreter` と入力
3. 作成した環境を選択する

例：

```text
Python 3.11.x ('myenv': conda)
```

これにより、VS Codeで実行するPythonが `myenv` に切り替わる。

---

## 4. requirements.txt を用意する

プロジェクトフォルダに `requirements.txt` を置く。

例：

```text
project/
├── app.py
├── requirements.txt
└── README.md
```

`requirements.txt` の例：

```txt
numpy
pandas
matplotlib
scikit-learn
plotly
dash
```

バージョンを指定する場合：

```txt
numpy==1.26.4
pandas==2.2.2
dash==2.17.1
```

---

## 5. requirements.txt をインストールする

Conda環境が有効化されていることを確認する。

```bash
conda activate myenv
```

その上で、以下を実行する。

```bash
pip install -r requirements.txt
```

重要なのは、`pip install` を実行する前に、必ず対象のConda環境を有効化しておくこと。

---

## 6. インストール確認

以下のコマンドで、インストール済みパッケージを確認できる。

```bash
pip list
```

特定のライブラリだけ確認したい場合：

```bash
pip show pandas
```

Python側で確認する場合：

```bash
python
```

Pythonが起動したら：

```python
import pandas as pd
print(pd.__version__)
```

終了する場合：

```python
exit()
```

---

## 7. VS Codeで実行する

Pythonファイルを開き、右上の実行ボタンを押す。

またはターミナルで：

```bash
python app.py
```

Dashアプリの場合：

```bash
python app.py
```

実行後、以下のようなURLが表示されたらブラウザで開く。

```text
http://127.0.0.1:8050/
```

---

## 8. よく使うコマンド一覧

### Conda環境一覧を表示

```bash
conda env list
```

または：

```bash
conda info --envs
```

### 環境を有効化

```bash
conda activate myenv
```

### 環境を無効化

```bash
conda deactivate
```

### 環境を削除

```bash
conda remove -n myenv --all
```

### 現在の環境から requirements.txt を作成

```bash
pip freeze > requirements.txt
```

### Conda環境をYAML形式で出力

```bash
conda env export > environment.yml
```

### environment.yml から環境を再作成

```bash
conda env create -f environment.yml
```

---

## 9. requirements.txt と environment.yml の違い

### requirements.txt

`pip` 用の依存関係ファイル。

```bash
pip install -r requirements.txt
```

Pythonライブラリ中心のプロジェクトではこれで十分なことが多い。

### environment.yml

`conda` 用の環境定義ファイル。

```bash
conda env create -f environment.yml
```

Pythonのバージョン、Condaパッケージ、pipパッケージをまとめて管理できる。

例：

```yml
name: myenv
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
  - numpy
  - pandas
  - pip:
      - dash
      - plotly
```

チーム開発や再現性を重視する場合は、`environment.yml` の方が便利。

---

## 10. よくあるエラーと対処法

### `conda` コマンドが認識されない

エラー例：

```text
conda is not recognized as an internal or external command
```

対処法：

- Anaconda Promptを使う
- Anaconda / Minicondaを再インストールする
- インストール時にPATH設定を確認する
- VS Codeを再起動する

Windowsでは、まず Anaconda Prompt で作業すると失敗しにくい。

---

### VS Codeで作成した環境が表示されない

対処法：

1. VS Codeを再起動する
2. `Ctrl + Shift + P`
3. `Python: Select Interpreter`
4. `Enter interpreter path...` から手動で指定する

環境の場所は以下で確認できる。

```bash
conda env list
```

---

### `pip install -r requirements.txt` が別環境に入ってしまう

原因：

Conda環境を有効化していない状態で `pip install` している。

対処法：

```bash
conda activate myenv
python -m pip install -r requirements.txt
```

より確実にするため、`pip` ではなく以下の形で実行するとよい。

```bash
python -m pip install -r requirements.txt
```

---

### PowerShellで `conda activate` が使えない

対処法：

```bash
conda init powershell
```

その後、PowerShellまたはVS Codeを再起動する。

それでもうまくいかない場合は、Anaconda Promptを使う。

---

## 11. 推奨される基本手順

新しいプロジェクトでは、基本的に以下の流れで行う。

```bash
conda create -n myenv python=3.11
conda activate myenv
python -m pip install -r requirements.txt
```

その後、VS Codeで：

```text
Python: Select Interpreter
```

から `myenv` を選択する。

---

## 12. 例：Dashアプリ用の環境作成

```bash
conda create -n dash-app python=3.11
conda activate dash-app
python -m pip install -r requirements.txt
```

`requirements.txt` の例：

```txt
dash
plotly
pandas
numpy
openpyxl
```

実行：

```bash
python app.py
```

---

## まとめ

VS CodeでAnaconda環境を使う場合は、以下の3点が重要。

1. `conda create -n 環境名 python=バージョン` で環境を作成する
2. `conda activate 環境名` で環境を有効化する
3. VS Codeで `Python: Select Interpreter` から同じ環境を選択する

`requirements.txt` をインストールするときは、必ず対象環境を有効化した状態で実行する。

```bash
python -m pip install -r requirements.txt
```
