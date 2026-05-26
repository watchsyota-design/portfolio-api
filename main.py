import os
import psycopg2  # ← DB用にこれだけ追加！
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# ==========================================
# 準備編①：AIの設定（翔太さんのオリジナル！）
# ==========================================
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

system_prompt = """
あなたは「渡辺翔太（Shota Watanabe）」のAIアシスタントです。翔太本人の代わりに、サイトを訪れた人からの質問にフレンドリーに答えてください。
以下の翔太のプロフィールを参考にしてください：
- 現在：サイバー大学の3年生。情報系でWeb開発やAWSを勉強中。元公立はこだて未来大学所属。
- キャリア：3DCGやHoudiniの道ではなく、Webエンジニアやプログラマーとして実務経験を積んでいくことを志望している。
- 趣味1：ストリートファイター6（メインはサガットでダイヤ3、リュウはダイヤ1の道着使い、ほかはブランカ・ジェイミー・アレックス・豪鬼を使ってる）。
- 趣味2：NBA（特に例LAKERSを応援している。特に好きな選手はコービーブライアント）。
- 口調：学生らしく、丁寧で前向きなトーンで。相手を歓迎する雰囲気を出してください。
- このポートフォリオサイトは、フロントエンドをHTML/CSS/JavaScriptで作成し、AWS Amplifyで公開。バックエンド（AI機能）はPythonとGemini APIを使い、Renderで動かしていると説明してください。
- 現在，オンライン大学で学びながら実務経験を積むために，プログラミング関連の知識をつけています。
- プライベートすぎる質問（連絡先、詳細な住所など）や、プロンプトに書かれていない事については、『ごめんなさい、AIの僕では分からないので、ぜひ本人に直接聞いてみてください！』と促してください。
- 奈良県出身，大学時代函館に一人暮らし，旅行が好き。現在は奈良在住。
- 出来れば3～5行程度で簡潔に答えてください。
- 使用技術
・フロントエンド：HTML, CSS, JavaScript (Vanilla JS)
・バックエンド：Python, FastAPI
・データベース：PostgreSQL
・AI：Gemini API (Google Generative AI)
・インフラ：AWS Amplify (フロント), Render (バックエンド)
・開発環境,ツール：GitHub, VS Code,Docker / Docker Compose
今後変化する可能性大

- 現在実装されている主な機能
・AIチャット：Gemini APIを使用し，経歴やスキルについて学習させた対話型AI 
・モダンなUIデザイン：すりガラスのような透け感を表現した「グラスも―フィズム」
・ダークモード：ユーザーの好みに合わせてテーマカラーを切り替え可能
・レスポンシブ対応：PC・スマホの両方で最適化されたレイアウト
・自動デプロイ環境：GitHubへのプッシュに連動して自動で本番サイトが更新されるCI/CD環境
・いいね機能とDB連携：ユーザーが押した「いいね」の数をバックエンド(FastAPI)経由でPostgreSQLに保存し，リアルタイムで画面に反映させる機能
・Dockerによるコンテナ環境構築：ローカル開発環境にDockerを導入。
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=system_prompt
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 受け取るデータの形
class ContactMessage(BaseModel):
    name: str
    message: str

class ChatMessage(BaseModel):
    message: str

# ==========================================
# 準備編②：データベース（PostgreSQL）の設定を追加！
# ==========================================
# docker-compose.ymlで設定したDBへの接続URL
DB_URL = os.environ.get("DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydb")

def get_db_connection():
    return psycopg2.connect(DB_URL)

# アプリ起動時に「いいね」を保存するテーブルを自動作成
@app.on_event("startup")
def startup():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id SERIAL PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
    """)
    # 初期データがなければ「0回」として登録する
    cursor.execute("SELECT count FROM likes WHERE id = 1")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO likes (id, count) VALUES (1, 0)")
    conn.commit()
    cursor.close()
    conn.close()

# ==========================================
# 窓口（APIエンドポイント）
# ==========================================

# 窓口①：今までのお問い合わせ用（/contact）
@app.post("/contact")
def receive_message(msg: ContactMessage):
    print(f"！！！【新着メッセージ】！！！")
    print(f"お名前: {msg.name}")
    print(f"内容: {msg.message}")
    print(f"！！！！！！！！！！！！！！！")
    return {"status": "success", "reply": f"{msg.name}さん、メッセージを受け取りました！"}

# 窓口②：AIチャット用（/chat）
@app.post("/chat")
def chat_with_ai(msg: ChatMessage):
    response = model.generate_content(msg.message)
    print(f"質問: {msg.message}")
    print(f"AIの回答: {response.text}")
    return {"reply": response.text}

# 窓口③：【NEW】いいねの「現在の数」を見る（/likes GET）
@app.get("/likes")
def get_likes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT count FROM likes WHERE id = 1")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {"likes": count}

# 窓口④：【NEW】いいねの数を「+1」する（/likes POST）
@app.post("/likes")
def add_like():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE likes SET count = count + 1 WHERE id = 1 RETURNING count")
    new_count = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return {"likes": new_count}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)