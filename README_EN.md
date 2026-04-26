# pasteimg — Claude Code Skill: Clipboard Image to Text

> One-click clipboard image analysis for Claude Code with DeepSeek V4.
> [中文文档](README_CN.md)

## What is this?

`pasteimg` is a Claude Code Skill. After installation, type `/pasteimg` in Claude Code to instantly capture the image from your clipboard, send it to a vision LLM, and get a detailed text description.

## Why this Skill?

> **DeepSeek V4 is not a multimodal model — it cannot process images.** When you paste screenshots, UI mockups, or code snippets into Claude Code, DeepSeek V4 simply cannot see them.

`pasteimg` fills this gap — it uses Gemini (or any vision LLM of your choice) to "look" at images, then returns the analysis as text that DeepSeek V4 can continue working with. Together they form a complete image understanding workflow.

## Prerequisites

- **Claude Code** configured with **DeepSeek V4** (see [DeepSeek API Docs](https://api-docs.deepseek.com/guides/coding_agents))
- OS: macOS / Linux (X11 or Wayland) / Windows (including WSL)

## Installation

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

## Usage

In Claude Code, type:

```
/pasteimg
```

Make sure you have an image in your clipboard first (`Win+Shift+S` / `Ctrl+C` / `Cmd+Ctrl+Shift+4`).

## Switching Vision Models

Default model is **Gemini 3.1 Flash-Lite**. Here are three popular multimodal models you can switch to:

| Option | Model | Provider | Requires |
|--------|-------|----------|----------|
| Default | Gemini 3.1 Flash-Lite | Google | `GEMINI_API_KEY` |
| Option A | GPT-5.4 | OpenAI | `OPENAI_API_KEY` |
| Option B | Claude Sonnet 4.6 | Anthropic | `ANTHROPIC_API_KEY` |

**Option A — Switch to GPT-5.4:**

Edit the `analyze_image()` function in `pasteimg.py` to use the OpenAI Chat Completions API format:

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
    # ... parse response["choices"][0]["message"]["content"]
```

Set `export OPENAI_API_KEY="sk-..."` and adjust `main()` to read the correct key.

**Option B — Switch to Claude Sonnet 4.6:**

Edit the `analyze_image()` function to use the Anthropic Messages API format:

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
    # ... parse response["content"][0]["text"]
```

All Claude models (Opus 4.7 / Sonnet 4.6 / Haiku 4.5) natively support vision with PNG / JPEG / GIF / WebP formats. See the [Claude Vision docs](https://platform.claude.com/docs/en/docs/build-with-claude/vision) for details.

Set `export ANTHROPIC_API_KEY="sk-ant-..."` and adjust `main()` accordingly.

## Structure

```
pasteimg/
  SKILL.md      # Claude Code Skill definition
  pasteimg.py   # Core script: clipboard extraction + API call
  README.md     # This file (English)
  README_CN.md  # Chinese documentation
```

## How it works

```
Clipboard Image ──→ Platform tool (xclip/wl-paste/osascript/PowerShell)
                 ──→ Base64 Encode ──→ Vision LLM API ──→ Text Output
```

## License

MIT — feel free to use, modify, and share.
