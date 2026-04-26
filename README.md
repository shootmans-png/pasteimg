# pasteimg — Claude Code Skill: Clipboard Image to Text

> 一键分析剪贴板图片，适用于 Claude Code + DeepSeek V4 使用场景。
> One-click clipboard image analysis for Claude Code with DeepSeek V4.

[中文](#中文) | [English](#english)

---

## 中文

### 这是什么？

`pasteimg` 是一个 Claude Code Skill，安装后在 Claude Code 中输入 `/pasteimg`，即可自动读取剪贴板中的图片，调用 Gemini 多模态视觉模型分析并输出文字描述。

### 适用环境

- **Claude Code** 已配置接入 **DeepSeek V4**（参考 [DeepSeek API 文档](https://api-docs.deepseek.com/zh-cn/guides/coding_agents)）
- 操作系统：macOS / Linux（X11 或 Wayland）/ Windows（含 WSL）

### 安装

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

### 使用

在 Claude Code 中输入：

```
/pasteimg
```

首次使用前，先复制一张图片到剪贴板（`Win+Shift+S` / `Ctrl+C` / `Cmd+Ctrl+Shift+4`）。

### 自定义视觉模型

默认使用 Gemini 3 Flash。如需更换：

```bash
export GEMINI_MODEL="gemini-3.1-pro-preview"  # 换成 Pro 版
```

或直接编辑 `pasteimg.py` 中的 `analyze_image()` 函数，对接 GPT-4V / Claude Vision 等任意多模态 API。

### 目录结构

```
pasteimg/
  SKILL.md      # Claude Code Skill 定义文件
  pasteimg.py   # 核心脚本：剪贴板提取 + Gemini API 调用
```

### 原理

```
剪贴板图片 ──→ 平台工具提取 (xclip/wl-paste/osascript/PowerShell)
              ──→ Base64 编码 ──→ Gemini API ──→ 文字描述输出
```

---

## English

### What is this?

`pasteimg` is a Claude Code Skill. After installation, type `/pasteimg` in Claude Code to instantly capture the image from your clipboard, send it to the Gemini vision model, and get a detailed text description.

### Prerequisites

- **Claude Code** configured with **DeepSeek V4** (see [DeepSeek API Docs](https://api-docs.deepseek.com/guides/coding_agents))
- OS: macOS / Linux (X11 or Wayland) / Windows (including WSL)

### Installation

```bash
# 1. Copy the pasteimg folder into Claude Code skills directory
cp -r pasteimg ~/.claude/skills/pasteimg

# 2. Set your Gemini API key (choose one)
export GEMINI_API_KEY="your-gemini-api-key"
# or
echo "your-gemini-api-key" > ~/.gemini/api_key.txt

# 3. Linux users: install clipboard tool
sudo apt install xclip        # X11
sudo apt install wl-clipboard # Wayland
```

### Usage

In Claude Code, type:

```
/pasteimg
```

Make sure you have an image in your clipboard first (`Win+Shift+S` / `Ctrl+C` / `Cmd+Ctrl+Shift+4`).

### Using a different vision model

Default model is Gemini 3 Flash. To change:

```bash
export GEMINI_MODEL="gemini-3.1-pro-preview"  # Upgrade to Pro
```

Or edit the `analyze_image()` function in `pasteimg.py` to call any multimodal API (GPT-4V, Claude Vision, etc.).

### Structure

```
pasteimg/
  SKILL.md      # Claude Code Skill definition
  pasteimg.py   # Core script: clipboard extraction + Gemini API call
```

### How it works

```
Clipboard Image ──→ Platform tool (xclip/wl-paste/osascript/PowerShell)
                 ──→ Base64 Encode ──→ Gemini API ──→ Text Output
```

---

## License

MIT — feel free to use, modify, and share.
