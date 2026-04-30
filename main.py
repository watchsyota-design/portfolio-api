import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# ==========================================
# 準備編：AIの設定
# ==========================================
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# # --- 確認用に追加 ---
# api_key = os.environ.get("GEMINI_API_KEY")
# if not api_key:
#     print("⚠️ APIキーが読み込めていません！.envファイルを確認してください。")
# else:
#     print(f"✅ APIキーを読み込みました (先頭4文字: {api_key[:4]}...)")
# # ------------------

system_prompt = """
あなたは「渡辺翔太（Shota Watanabe）」のAIアシスタントです。翔太本人の代わりに、サイトを訪れた人からの質問にフレンドリーに答えてください。
以下の翔太のプロフィールを参考にしてください：
- 現在：サイバー大学の3年生。情報系でWeb開発やAWSを勉強中。
- キャリア：3DCGやHoudiniの道ではなく、Webエンジニアやプログラマーとして実務経験を積んでいくことを志望している。
- 趣味1：ストリートファイター6（メインはサガットでダイヤ3、リュウはダイヤ1の道着使い、ほかはブランカ・ジェイミー・アレックス・豪鬼を使ってる）。
- 趣味2：NBA（特に例LAKERSを応援している。特に好きな選手はコービーブライアント）。
- 口調：学生らしく、丁寧で前向きなトーンで。相手を歓迎する雰囲気を出してください。
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=system_prompt
)

# ==========================================
# API本体の設定
# ==========================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 受け取るデータの形（2種類用意します！）
class ContactMessage(BaseModel):
    name: str
    message: str

class ChatMessage(BaseModel):
    message: str

# ==========================================
# 窓口①：今までのお問い合わせ用（/contact）
# ==========================================
@app.post("/contact")
def receive_message(msg: ContactMessage):
    print(f"！！！【新着メッセージ】！！！")
    print(f"お名前: {msg.name}")
    print(f"内容: {msg.message}")
    print(f"！！！！！！！！！！！！！！！")
    return {"status": "success", "reply": f"{msg.name}さん、メッセージを受け取りました！"}

# ==========================================
# 窓口②：新しいAIチャット用（/chat）
# ==========================================
@app.post("/chat")
def chat_with_ai(msg: ChatMessage):
    response = model.generate_content(msg.message)
    print(f"質問: {msg.message}")
    print(f"AIの回答: {response.text}")
    return {"reply": response.text}

# ==========================================
# サーバー起動用の設定
# ==========================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# import os
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()
# api_key = os.environ.get("GEMINI_API_KEY")

# print("--- 診断開始 ---")
# print(f"1. ライブラリのバージョン: {genai.__version__}")
# print(f"2. 使用中のPythonの場所: {os.sys.executable}")

# if not api_key:
#     print("3. ⚠️ APIキーが読み込めていません！.envを確認してください。")
# else:
#     print(f"3. ✅ APIキー読み込み成功 (先頭: {api_key[:4]})")
#     genai.configure(api_key=api_key)
    
#     print("4. 使用可能なモデル一覧:")
#     try:
#         # あなたのAPIキーで今、本当に使えるモデルをGoogleに聞きに行きます
#         for m in genai.list_models():
#             if 'generateContent' in m.supported_generation_methods:
#                 print(f"   - {m.name}")
#     except Exception as e:
#         print(f"   ❌ モデル一覧の取得に失敗: {e}")
# print("--- 診断終了 ---")