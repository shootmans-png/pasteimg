---
name: pasteimg
description: 读取剪贴板中的图片并用 Gemini 视觉模型分析内容
level: 0
---

# Paste Image

从剪贴板读取图片，调用 Gemini 视觉模型分析内容。跨平台支持 macOS / Linux / Windows。

> 新用户安装：需设置 Gemini API Key
>   export GEMINI_API_KEY="your-key"
>   或 echo "your-key" > ~/.gemini/api_key.txt
> Linux 用户还需安装剪贴板工具：sudo apt install xclip（X11）或 wl-clipboard（Wayland）
> 想换其他多模态模型？编辑 `pasteimg.py` 中的 `analyze_image()` 函数即可。

## 执行步骤

1. 获取本 skill 目录路径，运行 `python3 <skill_dir>/pasteimg.py`
2. 将脚本的 stdout 输出展示给用户
3. 如果脚本 stderr 提示 `No image in clipboard`，告知用户先复制图片到剪贴板（Win+Shift+S / Ctrl+C / Cmd+Ctrl+Shift+4）
4. 如果脚本 stderr 提示 `GEMINI_API_KEY not set`，告知用户按上方说明配置 API Key
