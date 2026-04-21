import torch
import numpy as np
from PIL import Image
import base64
import io
import urllib.request
import urllib.error
import json

class QwenImageEditNode1:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image1": ("IMAGE",),
                "api_key": ("STRING", {"default": "sk-your-api-key"}),
                "endpoint": ("STRING", {"default": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"}),
                "model": ("STRING", {"default": "qwen-image-edit-max"}),
                
                # --- 修改：将宽度和高度的调节步长(step)设为 8 ---
                "width": ("INT", {"default": 1024, "min": 256, "max": 4096, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 256, "max": 4096, "step": 8}),
                
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}), 
                
                # --- 强制连线项放在最后防止错位 Bug ---
                "prompt": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate"
    CATEGORY = "Alibaba Cloud/Qwen"

    def tensor_to_base64(self, tensor):
        if len(tensor.shape) == 4:
            tensor = tensor[0]
        i = 255. * tensor.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"

    def generate(self, image1, api_key, endpoint, model, width, height, seed, prompt, image2=None, image3=None):
        if not api_key or api_key == "sk-your-api-key":
            raise ValueError("请在节点中配置正确的阿里云 DashScope API Key。")
            
        if not prompt or str(prompt).strip() == "":
            raise ValueError("Prompt不能为空。")
            
        # 1. 组装 Message
        content =[]
        content.append({"image": self.tensor_to_base64(image1)})
        if image2 is not None:
            content.append({"image": self.tensor_to_base64(image2)})
        if image3 is not None:
            content.append({"image": self.tensor_to_base64(image3)})
        content.append({"text": str(prompt)})
        
        # 2. 组装 Payload，将整数宽高动态拼接为 API 要求的 "W*H" 字符串
        dynamic_size = f"{width}*{height}"
        
        payload = {
            "model": model,
            "input": {
                "messages":[{"role": "user", "content": content}]
            },
            "parameters": {
                "n": 1,
                "seed": seed,
                "size": dynamic_size # 提交通过8的倍数调节的分辨率
            }
        }

        # 3. 发送同步请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "disable" 
        }

        req = urllib.request.Request(endpoint, headers=headers, data=json.dumps(payload).encode('utf-8'))
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8')
            raise RuntimeError(f"API HTTP 调用报错 {e.code}: {err_msg}")
        except Exception as e:
            raise RuntimeError(f"API 请求失败: {str(e)}")

        if "code" in result and result["code"]:
            raise RuntimeError(f"百炼 API 业务错误 {result.get('code')}: {result.get('message')}")

        # 4. 解析返回的图片 URL
        try:
            output_content = result["output"]["choices"][0]["message"]["content"]
            output_url = None
            for item in output_content:
                if "image" in item:
                    output_url = item["image"]
                    break
            
            if not output_url:
                raise ValueError("未找到生成图像的 URL")
        except KeyError:
            raise RuntimeError(f"解析失败: {json.dumps(result)}")

        # 5. 下载并转换图像格式
        try:
            req_img = urllib.request.Request(output_url, headers={"User-Agent": "ComfyUI-Qwen-Image-Edit/1.0"})
            with urllib.request.urlopen(req_img, timeout=60) as response:
                img_data = response.read()
            out_img = Image.open(io.BytesIO(img_data)).convert("RGB")
            out_img_np = np.array(out_img).astype(np.float32) / 255.0
            out_tensor = torch.from_numpy(out_img_np).unsqueeze(0)
        except Exception as e:
            raise RuntimeError(f"图像处理失败: {str(e)}")

        return (out_tensor,)
