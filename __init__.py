from .qwen_node import QwenImageEditNode
from .qwen_chat_node import QwenChatNode
from .qwen_prompt_node import QwenPromptMasterNode
from .qwen_t2i_node import QwenImageCreateNode
from .qwen_repaint_node import QwenImageRepaintNode # 新增重绘节点

NODE_CLASS_MAPPINGS = {
    "QwenImageEditNode": QwenImageEditNode,
    "QwenChatNode": QwenChatNode,
    "QwenPromptMasterNode": QwenPromptMasterNode,
    "QwenImageCreateNode": QwenImageCreateNode,
    "QwenImageRepaintNode": QwenImageRepaintNode # 新增
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImageEditNode": "Qwen Image Edit (Aliyun)",
    "QwenChatNode": "Qwen Chat & VL (Aliyun)",
    "QwenPromptMasterNode": "Qwen Prompt Master (Aliyun)",
    "QwenImageCreateNode": "Qwen Image Create (Aliyun)",
    "QwenImageRepaintNode": "Qwen Image Repaint (Aliyun)" # 新增显示名称
}

__all__ =['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']