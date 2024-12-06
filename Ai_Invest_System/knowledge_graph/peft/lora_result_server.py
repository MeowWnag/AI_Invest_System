# filename: api_server.py

# encoding=utf-8
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="語言模型 API", version="1.0")

# 定義請求的數據模型
class GenerateRequest(BaseModel):
    prompts: List[str] = Field(..., example=[
        "這是一個句子。",])
    max_new_tokens: Optional[int] = Field(600, ge=1, le=4096, description="生成的最大新令牌數量")
    temperature: Optional[float] = Field(0.1, ge=0.0, le=2.0, description="採樣溫度")
    repetition_penalty: Optional[float] = Field(2.0, ge=0.0, description="重複懲罰因子")
    do_sample: Optional[bool] = Field(True, description="是否使用採樣")

# 定義回應的數據模型
class GenerateResponse(BaseModel):
    generated_texts: List[str]

# 初始化模型相關變數
base_model_id = "Breeze-7B-32k-Instruct-v1_0"
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

# 在啟動時載入模型
try:
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    eval_tokenizer = AutoTokenizer.from_pretrained(
        base_model_id, add_bos_token=True, trust_remote_code=True
    )
    ft_model = PeftModel.from_pretrained(
        base_model, "mistral-stock-info-train"
    )
    ft_model.eval()
    print("模型載入成功。")
except Exception as e:
    print(f"載入模型時出錯: {e}")

# 定義生成文本的端點
@app.post("/generate", response_model=GenerateResponse)
def generate_text(request: GenerateRequest):
    if not hasattr(ft_model, 'generate'):
        raise HTTPException(status_code=500, detail="模型未正確載入。")
    
    generated_texts = []
    for prompt in request.prompts:
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model_input = eval_tokenizer(prompt, return_tensors="pt").to(device)
            output_ids = ft_model.generate(
                **model_input,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                repetition_penalty=request.repetition_penalty,
                do_sample=request.do_sample
            )[0]
            generated_text = eval_tokenizer.decode(output_ids, skip_special_tokens=True)
            generated_texts.append(generated_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"生成文本時出錯: {e}")
    
    return GenerateResponse(generated_texts=generated_texts)