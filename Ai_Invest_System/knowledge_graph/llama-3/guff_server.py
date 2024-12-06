from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_cpp import Llama
#import torch


# 初始化模型
model = Llama(model_path="llama-3-taiwan-70b-instruct-q4_k_s.gguf",
              n_gpu_layers=40,# 使用 GPU 的層數，-1 表示全部在 GPU 上執行
              n_ctx=8000
)
#print(torch.cuda.is_available())
app = FastAPI()

# 定义请求体模型
class ChatRequest(BaseModel):
    message: str
    tempature: float = 0.3
    max_tokens: int = 2048
    top_p: float = 0.5
    repeat_penalty: float = 1.2

@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    user_tempature = request.tempature
    user_max_tokens = request.max_tokens
    user_top_p = request.top_p
    user_repeat_penalty = request.repeat_penalty

    if not user_message:
        raise HTTPException(status_code=400, detail="請提供訊息內容")

    # 使用模型生成回覆
    response = model.create_chat_completion(
        temperature=user_tempature,
        max_tokens=user_max_tokens,
        top_p=user_top_p,
        top_k=50,
        repeat_penalty=user_repeat_penalty,
        messages=[{
            "role": "user",
            "content": user_message
        }]
    )

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8062)