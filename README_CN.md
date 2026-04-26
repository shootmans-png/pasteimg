# pasteimg — Claude Code Skill：剪贴板图片一键转文字

> 一键分析剪贴板图片，适用于 Claude Code + DeepSeek V4 使用场景。
> [English Docs](README_EN.md)

## 这是什么？

`pasteimg` 是一个 Claude Code Skill，安装后在 Claude Code 中输入 `/pasteimg`，即可自动读取剪贴板中的图片，调用视觉大模型分析并输出文字描述。

## 为什么需要这个 Skill？

> **DeepSeek V4 不是多模态模型，不支持图片识别。** 当你在 Claude Code 中粘贴截图、UI 设计稿、代码截图时，DeepSeek V4 无法理解图片内容。

`pasteimg` 填补了这个空缺 — 它用 Gemini（或其他视觉大模型）来"看"图片，分析结果交给 DeepSeek V4 继续处理。两者互补，实现完整的图片理解工作流。

## 适用环境

- **Claude Code** 已配置接入 **DeepSeek V4**（参考 [DeepSeek API 文档](https://api-docs.deepseek.com/zh-cn/guides/coding_agents)）
- 操作系统：macOS / Linux（X11 或 Wayland）/ Windows（含 WSL）

## 安装

```bash
# 1. 将 pasteimg 目录复制到 Claude Code 的 skills 目录
cp -r pasteimg ~/.claude/skills/pasteimg

# 2. 设置 Gemini API Key（二选一）
export GEMINI_API_KEY="your-gemini-api-key"
# 或者
echo "your-gemini-api-key" > ~/.gemini/api_key.txt

# 3. Linux 用户安装剪贴板工具
sudo apt install xclip        # X11
sudo apt install wl-clipboard # Wayland
```

## 使用

在 Claude Code 中输入：

```
/pasteimg
```

首次使用前，先复制一张图片到剪贴板（`Win+Shift+S` / `Ctrl+C` / `Cmd+Ctrl+Shift+4`）。

## 切换视觉大模型

默认使用 **Gemini 3.1 Flash-Lite**。以下列出三种主流多模态模型的切换方式：

| 方案 | 模型 | 厂商 | 需要 |
|------|------|------|------|
| 默认 | Gemini 3.1 Flash-Lite | Google | `GEMINI_API_KEY` |
| 备选 A | GPT-5.4 | OpenAI | `OPENAI_API_KEY` |
| 备选 B | Claude Sonnet 4.6 | Anthropic | `ANTHROPIC_API_KEY` |

**方案 A — 切换为 GPT-5.4：**

编辑 `pasteimg.py` 中的 `analyze_image()` 函数，替换为 OpenAI API 格式：

```python
def analyze_image(filepath, api_key):
    import base64
    with open(filepath, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = json.dumps({
        "model": "gpt-5.4",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
            ]
        }]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )
    # ... 解析 response["choices"][0]["message"]["content"]
```

使用时设置 `export OPENAI_API_KEY="sk-..."` 并调整 `main()` 中读取的 key。

**方案 B — 切换为 Claude Sonnet 4.6：**

编辑 `pasteimg.py` 中的 `analyze_image()` 函数，替换为 Anthropic Messages API 格式：

```python
def analyze_image(filepath, api_key):
    import base64
    with open(filepath, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    mime = "image/png"
    if filepath.lower().endswith((".jpg", ".jpeg")):
        mime = "image/jpeg"

    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 2048,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": mime,
                    "data": img_b64
                }}
            ]
        }]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )
    # ... 解析 response["content"][0]["text"]
```

Claude 全系模型（Opus 4.7 / Sonnet 4.6 / Haiku 4.5）均原生支持视觉输入，支持 PNG / JPEG / GIF / WebP 格式。

使用时设置 `export ANTHROPIC_API_KEY="sk-ant-..."` 并调整 `main()` 中读取的 key。

## 目录结构

```
pasteimg/
  SKILL.md       # Claude Code Skill 定义文件
  pasteimg.py    # 核心脚本：剪贴板提取 + API 调用
  README_EN.md      # 英文文档
  README_CN.md   # 中文文档（本文件）
```

## 原理

```
剪贴板图片 ──→ 平台工具提取 (xclip/wl-paste/osascript/PowerShell)
              ──→ Base64 编码 ──→ 视觉大模型 API ──→ 文字描述输出
```

## License

MIT — 自由使用、修改、分享。
