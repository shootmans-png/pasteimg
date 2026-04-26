#!/usr/bin/env python3
"""
pasteimg — Cross-platform clipboard image → Gemini multimodal analysis.
Zero dependencies: Python 3 stdlib + your platform's clipboard tool.

Quick setup for new users:
  export GEMINI_API_KEY="your-gemini-api-key"
  # or: echo "your-key" > ~/.gemini/api_key.txt

Platform clipboard tools (auto-detected):
  macOS  : built-in (osascript)
  Linux  : xclip (X11) or wl-clipboard (Wayland)  —  install one: apt install xclip
  Windows: built-in (PowerShell)

To swap the vision model: set GEMINI_MODEL env var,
  e.g. export GEMINI_MODEL="gemini-2.5-pro-preview"
  Or edit analyze() below to call a different API entirely.
"""

import os
import sys
import json
import base64
import tempfile
import subprocess
import urllib.request
import urllib.error

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")

PROMPT = os.environ.get(
    "IMAGE_ANALYSIS_PROMPT",
    "请详细描述这张图片的内容。如果是截图或UI，说明界面元素、文字内容、布局结构。"
    "如果是代码截图，提取其中的代码。如果是照片，描述场景、物体、人物等。用中文回答。",
)


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    keyfile = os.path.expanduser("~/.gemini/api_key.txt")
    if os.path.isfile(keyfile):
        return open(keyfile).read().strip()
    return ""


def clipboard_to_file():
    """Extract image from clipboard → temp file path. Returns None if no image."""

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name

    # --- macOS (osascript) ---
    if sys.platform == "darwin":
        script = """
set f to (POSIX file "/tmp/_pasteimg_tmp.png")
try
    set img to (the clipboard as «class PNGf»)
    set fh to open for access f with write permission
    write img to fh
    close access fh
    return "ok"
on error
    return "empty"
end try"""
        r = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and "ok" in r.stdout:
            try:
                os.rename("/tmp/_pasteimg_tmp.png", tmp)
            except OSError:
                import shutil
                shutil.copy("/tmp/_pasteimg_tmp.png", tmp)
            return tmp
        os.unlink(tmp)
        return None

    # --- Linux X11 (xclip) ---
    r = subprocess.run(
        ["which", "xclip"], capture_output=True, timeout=5
    )
    if r.returncode == 0:
        r = subprocess.run(
            ["xclip", "-selection", "clipboard", "-t", "image/png", "-o"],
            capture_output=True, timeout=10,
        )
        if r.returncode == 0 and len(r.stdout) > 100:
            with open(tmp, "wb") as f:
                f.write(r.stdout)
            return tmp

    # --- Linux Wayland (wl-paste) ---
    r = subprocess.run(
        ["which", "wl-paste"], capture_output=True, timeout=5
    )
    if r.returncode == 0:
        r = subprocess.run(
            ["wl-paste", "--type", "image/png"],
            capture_output=True, timeout=10,
        )
        if r.returncode == 0 and len(r.stdout) > 100:
            with open(tmp, "wb") as f:
                f.write(r.stdout)
            return tmp

    # --- Windows / WSL (PowerShell) ---
    ps = "powershell.exe" if sys.platform == "linux" else "powershell"
    r = subprocess.run(["which", ps], capture_output=True, timeout=5)
    if r.returncode == 0:
        win_tmp = f"claude_pasteimg_{os.getpid()}.png"
        cmd = (
            "Add-Type -AssemblyName System.Drawing;"
            "$img = Get-Clipboard -Format Image -ErrorAction SilentlyContinue;"
            "if ($img -eq $null) { exit 2 };"
            f"$img.Save($env:TEMP + '\\\\{win_tmp}',"
            " [System.Drawing.Imaging.ImageFormat]::Png);"
            f"Write-Output ($env:TEMP + '\\\\{win_tmp}')"
        )
        r = subprocess.run(
            [ps, "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, timeout=15,
            encoding="utf-8", errors="replace",
        )
        if r.returncode == 0 and r.stdout.strip():
            win_path = r.stdout.strip().split("\n")[-1].strip()
            if sys.platform == "linux" and len(win_path) > 2 and win_path[1] == ":":
                wsl_path = "/mnt/{}/{}".format(
                    win_path[0].lower(),
                    win_path[3:].replace("\\", "/"),
                )
                if os.path.isfile(wsl_path):
                    import shutil
                    shutil.copy(wsl_path, tmp)
                    try:
                        os.unlink(wsl_path)
                    except OSError:
                        pass
                    return tmp
            elif os.path.isfile(win_path):
                import shutil
                shutil.copy(win_path, tmp)
                return tmp

    os.unlink(tmp)
    return None


def analyze_image(filepath, api_key):
    """Send image to Gemini, return text result."""

    with open(filepath, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Sniff mime type
    mime = "image/png"
    if filepath.lower().endswith((".jpg", ".jpeg")):
        mime = "image/jpeg"
    elif filepath.lower().endswith(".gif"):
        mime = "image/gif"
    elif filepath.lower().endswith(".webp"):
        mime = "image/webp"

    payload = json.dumps(
        {
            "contents": [
                {
                    "parts": [
                        {"text": PROMPT},
                        {"inline_data": {"mime_type": mime, "data": img_b64}},
                    ]
                }
            ],
            "generationConfig": {"maxOutputTokens": 2048},
        }
    ).encode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"

    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            candidates = result.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                return "".join(p.get("text", "") for p in parts)
            return f"Gemini returned no content: {json.dumps(result, ensure_ascii=False)}"
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return f"API Error {e.code}: {body}"
    except Exception as e:
        return f"Error: {e}"


def main():
    api_key = get_api_key()
    if not api_key:
        print(
            "ERROR: GEMINI_API_KEY not set.\n"
            "  export GEMINI_API_KEY=\"your-key\"\n"
            "  # or: echo \"your-key\" > ~/.gemini/api_key.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    tmp_path = clipboard_to_file()
    if not tmp_path:
        print(
            "ERROR: No image in clipboard.\n"
            "Copy an image first — Win+Shift+S / Ctrl+C / Cmd+Ctrl+Shift+4.",
            file=sys.stderr,
        )
        sys.exit(1)

    result = analyze_image(tmp_path, api_key)
    try:
        os.unlink(tmp_path)
    except OSError:
        pass
    print(result)


if __name__ == "__main__":
    main()
