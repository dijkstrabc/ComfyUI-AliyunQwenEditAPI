from .qwen_node import QwenImageEditNode1

NODE_CLASS_MAPPINGS = {
    "QwenImageEditNode1": QwenImageEditNode1,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImageEditNode1": "Qwen Image Edit (Aliyun)1",
}

__all__ =['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
