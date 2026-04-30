from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# --- 魔法のブロック：CORS（コルス）の設定 ---
# これを書かないと、セキュリティの壁に阻まれてHTMLからデータを受け取れません！
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 開発中はどこからでもアクセスOKにする
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------------------------

# ① 受け取るデータの「形」を定義する
class ContactMessage(BaseModel):
    name: str
    message: str

# ② メッセージを受け取るための新しい窓口（POST）を作る
@app.post("/contact")
def receive_message(msg: ContactMessage):
    # 受け取ったデータをターミナル（黒い画面）に表示してみる
    print(f"！！！【新着メッセージ】！！！")
    print(f"お名前: {msg.name}")
    print(f"内容: {msg.message}")
    print(f"！！！！！！！！！！！！！！！")
    
    # サイト側（フロントエンド）に「無事に受け取ったよ！」と返事をする
    return {"status": "success", "reply": f"{msg.name}さん、メッセージを受け取りました！"}

import os

# Renderなどのクラウド環境で動かすための設定
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)