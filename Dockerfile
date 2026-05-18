# Pythonの軽量版イメージ(slim)をベースにする
FROM python:3.9-slim
# 作業ディレクトリを /app に設定する
WORKDIR /app
# 現在のディレクトリのファイルをすべてコンテナにコピーする
COPY . /app
# requirements.txtを使ってパッケージをインストールする
RUN pip install --no-cache-dir -r requirements.txt
# コンテナの「8000番ドア」を開ける宣言
EXPOSE 8000
# pythonでメインのファイル(app.py)を実行する
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]