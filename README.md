# Gemma Ollama Chatbot 🤖

A beautiful, ChatGPT-style web interface for running Gemma 2B locally via Ollama. Built as a single Python file with persistent chat history, streaming responses, and a stunning iOS-inspired UI.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![Ollama](https://img.shields.io/badge/Ollama-Latest-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **🎨 Stunning UI**: ChatGPT + iOS hybrid design with dark/light themes
- **💬 Perfect Memory**: Full conversation context sent with every message
- **⚡ Real-time Streaming**: Token-by-token response generation
- **💾 Persistent Storage**: Chat history survives server restarts (JSON-based)
- **🎭 3D Animations**: Particle effects, smooth transitions, glass-morphism
- **📱 Fully Responsive**: Works beautifully on mobile, tablet, and desktop
- **🔄 Advanced Features**: 
  - Copy messages
  - Regenerate responses
  - Export chat history
  - Theme toggle (dark/light)
  - Stop generation mid-stream
  - Chat session management

## 🎯 Why Use This?

### vs ChatGPT Web
- ✅ **100% Private**: All data stays on your machine
- ✅ **No API Costs**: No per-token charges
- ✅ **Offline Capable**: Works without internet (after model download)
- ✅ **Customizable**: Modify the system prompt, UI, or model easily

### vs Ollama CLI
- ✅ **Beautiful Interface**: Modern web UI instead of terminal
- ✅ **Persistent History**: Chats saved across sessions
- ✅ **Better UX**: Copy, regenerate, export, themes
- ✅ **Markdown Support**: Proper rendering of code blocks and formatting

### vs Other Ollama UIs
- ✅ **Single File**: No complex setup, just run `app.py`
- ✅ **Zero Database Setup**: Uses simple JSON storage
- ✅ **Production Ready**: Handles streaming, errors, edge cases
- ✅ **Gorgeous Design**: iOS-inspired with smooth animations

## 📋 Prerequisites

- **Python 3.10 or higher**
- **Ollama** installed and running
- **Gemma 2B model** pulled in Ollama

## 🚀 Installation

### Linux (Ubuntu/Debian)

```bash
# 1. Install Python 3.10+ (if not already installed)
sudo apt update
sudo apt install python3 python3-pip -y

# 2. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 3. Pull Gemma 2B model
ollama pull gemma:2b

# 4. Download the app
curl -O https://raw.githubusercontent.com/vikrant-project/gemma-open-source/main/app.py

# 5. Install Python dependencies
pip3 install flask flask-cors requests

# 6. Run the application
python3 app.py
```

**Access**: Open `http://localhost:9087` in your browser

---

### Windows

```powershell
# 1. Install Python 3.10+ from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation

# 2. Install Ollama
# Download from: https://ollama.com/download/windows
# Run the installer

# 3. Open Command Prompt or PowerShell and pull Gemma
ollama pull gemma:2b

# 4. Download app.py
# Save from: https://raw.githubusercontent.com/vikrant-project/gemma-open-source/main/app.py

# 5. Install Python dependencies
pip install flask flask-cors requests

# 6. Run the application
python app.py
```

**Access**: Open `http://localhost:9087` in your browser

---

### macOS

```bash
# 1. Install Python 3.10+ (using Homebrew)
brew install python@3.10

# 2. Install Ollama
brew install ollama

# 3. Start Ollama service
ollama serve &

# 4. Pull Gemma 2B model
ollama pull gemma:2b

# 5. Download the app
curl -O https://raw.githubusercontent.com/vikrant-project/gemma-open-source/main/app.py

# 6. Install Python dependencies
pip3 install flask flask-cors requests

# 7. Run the application
python3 app.py
```

**Access**: Open `http://localhost:9087` in your browser

---

## 🎮 How to Use

### First Time Setup

1. **Start Ollama** (if not running as service):
   ```bash
   ollama serve
   ```

2. **Verify Gemma model** is available:
   ```bash
   ollama list
   ```
   You should see `gemma:2b` in the list

3. **Run the app**:
   ```bash
   python3 app.py  # or python app.py on Windows
   ```

4. **Open browser**: Navigate to `http://localhost:9087`

### Basic Usage

- **Send Message**: Type in the input box and press Enter or click Send
- **New Chat**: Click "+ New Chat" button to start fresh
- **Copy Message**: Hover over any message and click "Copy"
- **Regenerate**: Click "Regenerate" on AI responses to get a new answer
- **Export**: Click "Export Chat" to download conversation as JSON
- **Theme Toggle**: Click the sun/moon icon to switch themes
- **Stop Generation**: Click "Stop" while AI is typing to halt response

### Keyboard Shortcuts

- `Enter`: Send message
- `Shift + Enter`: New line in message
- `Esc`: Close sidebar (mobile)

### Advanced Features

**Persistent Chat History**: All conversations are automatically saved to `chat_sessions.json`. Your chats survive server restarts.

**Perfect Memory**: The AI remembers every message in the current conversation. Try asking "What did I say earlier?" or "Summarize our conversation."

**Markdown Support**: 
- Use **bold** with `**text**`
- Use *italic* with `*text*`
- Code blocks with triple backticks
- Lists, headers, links all supported

## 🔧 Configuration

Edit these variables at the top of `app.py`:

```python
OLLAMA_API = "http://localhost:11434/api/chat"  # Ollama endpoint
MODEL_NAME = "gemma:2b"                         # Change model here
STORAGE_FILE = "chat_sessions.json"             # Storage location
```

### Using Different Models

```python
MODEL_NAME = "llama2"          # For Llama 2
MODEL_NAME = "mistral"         # For Mistral
MODEL_NAME = "codellama"       # For Code Llama
```

Make sure to pull the model first: `ollama pull <model-name>`

### Changing Port

```python
app.run(host="0.0.0.0", port=9087, ...)  # Change 9087 to your port
```

### Custom System Prompt

Edit the `SYSTEM_PROMPT` variable to change AI behavior:

```python
SYSTEM_PROMPT = """Your custom instructions here..."""
```

## 🏗️ Architecture

- **Backend**: Flask (Python) - handles API, storage, Ollama communication
- **Frontend**: Vanilla JS + HTML + CSS (all inline in single file)
- **Storage**: JSON file (`chat_sessions.json`)
- **AI**: Ollama API (local LLM inference)
- **Streaming**: Server-Sent Events (SSE)

## 📊 Comparison with Alternatives

| Feature | This App | Ollama CLI | ChatGPT Web | Open-WebUI |
|---------|----------|------------|-------------|------------|
| Single File | ✅ | ✅ | ❌ | ❌ |
| Beautiful UI | ✅ | ❌ | ✅ | ✅ |
| Setup Time | < 2 min | < 1 min | 0 min | 5-10 min |
| Privacy | 100% | 100% | 0% | 100% |
| Persistent Chats | ✅ | ❌ | ✅ | ✅ |
| Cost | Free | Free | $20/mo | Free |
| Offline | ✅ | ✅ | ❌ | ✅ |
| Mobile Friendly | ✅ | ❌ | ✅ | ✅ |
| Database Required | ❌ | ❌ | N/A | ✅ |

## 🐛 Troubleshooting

### Ollama Connection Error

**Problem**: Red status dot, "Ollama API error"

**Solution**:
```bash
# Check if Ollama is running
ollama list

# If not running, start it
ollama serve

# Verify the model exists
ollama pull gemma:2b
```

### Port Already in Use

**Problem**: `Address already in use`

**Solution**: Change port in `app.py` or kill the process:
```bash
# Linux/Mac
lsof -ti:9087 | xargs kill -9

# Windows
netstat -ano | findstr :9087
taskkill /PID <PID> /F
```

### Chat History Not Saving

**Problem**: Chats disappear after restart

**Solution**: Make sure `chat_sessions.json` has write permissions:
```bash
chmod 666 chat_sessions.json
```

### Slow Response Times

**Problem**: AI takes too long to respond

**Solutions**:
- Use a smaller model: `gemma:2b` instead of `gemma:7b`
- Reduce conversation history (edit code to limit messages)
- Ensure sufficient RAM (4GB+ recommended)
- Check CPU usage (Ollama uses CPU for inference on non-GPU systems)

## 🔐 Security Notes

- **Local Only**: Default binding to `0.0.0.0` allows LAN access
- **Production**: Add authentication if exposing to internet
- **HTTPS**: Use reverse proxy (nginx/caddy) for TLS
- **Firewall**: Block port 9087 if not needed externally

## 📜 License

MIT License - feel free to modify and distribute

## 🤝 Contributing

This is a single-file project for simplicity. Fork it and make it your own!

Suggested improvements:
- User authentication
- Multi-user support
- Voice input/output
- Image generation integration
- Custom model parameters UI

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Ollama Docs**: https://ollama.com/docs
- **Gemma Model**: https://ollama.com/library/gemma

## ⭐ Star This Repo

If you find this useful, give it a star! It helps others discover the project.

---

**Made with ❤️ for the open-source AI community**

🚀 **Deploy anywhere**: VPS, Raspberry Pi, your laptop
🔒 **Privacy first**: Your data never leaves your machine
⚡ **Lightning fast**: Local inference, no API delays
