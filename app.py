#!/usr/bin/env python3
"""
Gemma Ollama Chatbot - Single File Application
A ChatGPT-style interface for Gemma 2B via Ollama
Host: 0.0.0.0:9087 | Model: gemma:2b
"""

from flask import Flask, render_template_string, request, jsonify, Response, make_response
from flask_cors import CORS
import requests
import json
import uuid
import os
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# In-memory session storage
active_sessions = {}

# Configuration
OLLAMA_API = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma:2b"
STORAGE_FILE = "chat_sessions.json"

# Mastermind System Prompt
SYSTEM_PROMPT = """You are a highly intelligent AI assistant with perfect memory of this entire conversation. You remember every message the user has sent and every answer you have given. You can reference, recall, and build upon earlier parts of the conversation at any time.

Rules:
- Always remember the full context of this chat session
- If the user asks what they said earlier, quote it precisely
- Keep answers clear, concise, and helpful
- If unsure, say so honestly
- Format code blocks with triple backticks and language name
- Use markdown for lists, bold, headers when helpful
- Be conversational but smart
- Never pretend you cannot remember previous messages"""

# Storage management
def load_sessions():
    """Load all chat sessions from JSON file"""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_sessions(sessions):
    """Save all chat sessions to JSON file"""
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving sessions: {e}")

def get_session_id():
    """Get or create session ID from cookie"""
    sid = request.cookies.get('session_id')
    if not sid:
        sid = str(uuid.uuid4())
    return sid

def get_conversation(sid):
    """Get current conversation history"""
    sessions = load_sessions()
    if sid not in sessions:
        sessions[sid] = {
            'messages': [],
            'title': 'New Chat',
            'created_at': datetime.now().isoformat()
        }
        save_sessions(sessions)
    return sessions[sid]['messages']

def save_conversation(sid, messages, title=None):
    """Save conversation history"""
    sessions = load_sessions()
    if sid not in sessions:
        sessions[sid] = {
            'created_at': datetime.now().isoformat()
        }
    sessions[sid]['messages'] = messages
    if title:
        sessions[sid]['title'] = title[:30]
    save_sessions(sessions)

# HTML Template (inline)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemma AI Chat</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-primary: #0d0d0d;
            --bg-secondary: #1a1a1a;
            --bg-sidebar: rgba(20, 20, 20, 0.95);
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
            --accent-blue: #0A84FF;
            --ai-bubble: rgba(40, 40, 40, 0.8);
            --border-glow: rgba(10, 132, 255, 0.3);
            --gradient-1: #0d0d0d;
            --gradient-2: #111827;
        }

        [data-theme="light"] {
            --bg-primary: #ffffff;
            --bg-secondary: #f5f5f5;
            --bg-sidebar: rgba(245, 245, 245, 0.95);
            --text-primary: #000000;
            --text-secondary: #666666;
            --accent-blue: #007AFF;
            --ai-bubble: rgba(240, 240, 240, 0.9);
            --border-glow: rgba(0, 122, 255, 0.2);
            --gradient-1: #ffffff;
            --gradient-2: #f0f0f0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            overflow: hidden;
            animation: bgGradient 8s ease infinite;
        }

        @keyframes bgGradient {
            0%, 100% { background: var(--gradient-1); }
            50% { background: var(--gradient-2); }
        }

        .container {
            display: flex;
            height: 100vh;
            position: relative;
        }

        /* Particle Background */
        .particle-field {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        }

        .particle {
            position: absolute;
            width: 3px;
            height: 3px;
            background: var(--accent-blue);
            border-radius: 50%;
            opacity: 0.3;
            animation: float 6s infinite ease-in-out;
        }

        @keyframes float {
            0%, 100% { transform: translate(0, 0); }
            25% { transform: translate(10px, -20px); }
            50% { transform: translate(-10px, -40px); }
            75% { transform: translate(5px, -20px); }
        }

        /* Sidebar */
        .sidebar {
            width: 260px;
            background: var(--bg-sidebar);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            flex-direction: column;
            z-index: 10;
            transition: transform 0.3s ease;
        }

        .sidebar-header {
            padding: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .new-chat-btn {
            width: 100%;
            padding: 12px;
            background: var(--accent-blue);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .new-chat-btn:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 20px rgba(10, 132, 255, 0.3);
        }

        .new-chat-btn:active {
            transform: scale(0.98);
        }

        .chat-history {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }

        .chat-history-item {
            padding: 12px;
            margin: 5px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 13px;
            color: var(--text-secondary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .chat-history-item:hover {
            background: rgba(255, 255, 255, 0.05);
            transform: perspective(500px) rotateY(2deg);
        }

        /* Main Chat Area */
        .main-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
            z-index: 1;
        }

        /* Top Nav */
        .top-nav {
            padding: 15px 30px;
            background: var(--bg-secondary);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
        }

        .model-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(10, 132, 255, 0.1);
            border: 1px solid var(--accent-blue);
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #34C759;
            animation: pulse 2s infinite;
        }

        .status-dot.offline {
            background: #FF3B30;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .theme-toggle {
            padding: 8px 16px;
            background: var(--bg-sidebar);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            color: var(--text-primary);
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }

        .theme-toggle:hover {
            background: var(--accent-blue);
            color: white;
        }

        /* Messages Area */
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 30px;
            scroll-behavior: smooth;
        }

        .message {
            display: flex;
            margin-bottom: 20px;
            animation: messageSlideIn 0.25s ease;
            opacity: 0;
            animation-fill-mode: forwards;
        }

        @keyframes messageSlideIn {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            justify-content: flex-end;
        }

        .message-bubble {
            max-width: 70%;
            padding: 14px 18px;
            border-radius: 18px;
            position: relative;
            word-wrap: break-word;
        }

        .message.user .message-bubble {
            background: var(--accent-blue);
            color: white;
            border-radius: 18px 18px 4px 18px;
        }

        .message.ai .message-bubble {
            background: var(--ai-bubble);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 18px 18px 18px 4px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .message-actions {
            display: flex;
            gap: 8px;
            margin-top: 8px;
            opacity: 0;
            transition: opacity 0.2s;
        }

        .message:hover .message-actions {
            opacity: 1;
        }

        .action-btn {
            padding: 4px 10px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 6px;
            color: var(--text-secondary);
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .action-btn:hover {
            background: var(--accent-blue);
            color: white;
        }

        /* Typing Indicator */
        .typing-indicator {
            display: none;
            align-items: center;
            gap: 4px;
            padding: 14px 18px;
            background: var(--ai-bubble);
            border-radius: 18px;
            width: fit-content;
        }

        .typing-indicator.active {
            display: flex;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: var(--text-secondary);
            border-radius: 50%;
            animation: typingBounce 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }

        /* Input Area */
        .input-area {
            padding: 20px 30px;
            background: var(--bg-secondary);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .input-container {
            display: flex;
            gap: 12px;
            align-items: flex-end;
            max-width: 900px;
            margin: 0 auto;
        }

        .input-wrapper {
            flex: 1;
            position: relative;
        }

        #messageInput {
            width: 100%;
            padding: 14px 50px 14px 18px;
            background: var(--bg-sidebar);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            color: var(--text-primary);
            font-size: 15px;
            font-family: inherit;
            resize: none;
            max-height: 120px;
            transition: all 0.2s;
        }

        #messageInput:focus {
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.1),
                        0 8px 20px rgba(10, 132, 255, 0.2);
        }

        .send-btn {
            padding: 14px 24px;
            background: var(--accent-blue);
            border: none;
            border-radius: 24px;
            color: white;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 12px rgba(10, 132, 255, 0.3);
        }

        .send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(10, 132, 255, 0.4);
        }

        .send-btn:active {
            transform: scale(0.95);
        }

        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .stop-btn {
            padding: 14px 24px;
            background: #FF3B30;
            border: none;
            border-radius: 24px;
            color: white;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            display: none;
        }

        .stop-btn.active {
            display: block;
        }

        /* Code Blocks */
        pre {
            background: #1e1e1e !important;
            border-radius: 12px;
            padding: 0;
            overflow: hidden;
            position: relative;
            margin: 16px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .code-header {
            background: #2d2d2d;
            padding: 8px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .code-language {
            font-size: 12px;
            color: #888;
            font-weight: 600;
            text-transform: uppercase;
        }

        .code-content {
            padding: 16px;
            overflow-x: auto;
        }

        code {
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
        }

        pre code {
            background: transparent !important;
            padding: 0 !important;
        }

        /* Inline code */
        :not(pre) > code {
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 13px;
            color: #e06c75;
        }

        [data-theme="light"] :not(pre) > code {
            background: rgba(0, 0, 0, 0.06);
            color: #c7254e;
        }

        .copy-code-btn {
            padding: 6px 12px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            color: white;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .copy-code-btn:hover {
            background: var(--accent-blue);
            border-color: var(--accent-blue);
        }

        .copy-code-btn.copied {
            background: #34C759;
            border-color: #34C759;
        }

        /* Export Button */
        .export-btn {
            padding: 8px 16px;
            background: var(--bg-sidebar);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            color: var(--text-primary);
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }

        .export-btn:hover {
            background: #34C759;
            color: white;
        }

        /* Empty State */
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            gap: 20px;
        }

        .empty-state h2 {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-blue), #5E5CE6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .empty-state p {
            color: var(--text-secondary);
            font-size: 16px;
        }

        /* Hamburger Menu */
        .hamburger {
            display: none;
            flex-direction: column;
            gap: 4px;
            cursor: pointer;
            padding: 10px;
        }

        .hamburger span {
            width: 24px;
            height: 3px;
            background: var(--text-primary);
            border-radius: 2px;
            transition: all 0.3s;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .sidebar {
                position: fixed;
                left: 0;
                top: 0;
                height: 100vh;
                transform: translateX(-100%);
                z-index: 100;
            }

            .sidebar.open {
                transform: translateX(0);
            }

            .hamburger {
                display: flex;
            }

            .message-bubble {
                max-width: 85%;
            }

            .top-nav {
                padding: 15px;
            }
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.3);
        }
    </style>
</head>
<body data-theme="dark">
    <!-- Particle Field -->
    <div class="particle-field" id="particleField"></div>

    <div class="container">
        <!-- Sidebar -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <button class="new-chat-btn" onclick="newChat()">+ New Chat</button>
            </div>
            <div class="chat-history" id="chatHistory">
                <!-- History items will be loaded here -->
            </div>
        </div>

        <!-- Main Area -->
        <div class="main-area">
            <!-- Top Nav -->
            <div class="top-nav">
                <div style="display: flex; gap: 15px; align-items: center;">
                    <div class="hamburger" onclick="toggleSidebar()">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <div class="model-badge">
                        <span class="status-dot" id="statusDot"></span>
                        <span>Gemma 2B</span>
                    </div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button class="export-btn" onclick="exportChat()">Export Chat</button>
                    <button class="theme-toggle" onclick="toggleTheme()">
                        <span id="themeIcon">☀️</span>
                    </button>
                </div>
            </div>

            <!-- Messages -->
            <div class="messages-container" id="messagesContainer">
                <div class="empty-state" id="emptyState">
                    <h2>Gemma AI Assistant</h2>
                    <p>Start a conversation with perfect memory retention</p>
                </div>
            </div>

            <!-- Input Area -->
            <div class="input-area">
                <div class="input-container">
                    <div class="input-wrapper">
                        <textarea 
                            id="messageInput" 
                            placeholder="Message Gemma..." 
                            rows="1"
                            onkeydown="handleKeyPress(event)"
                        ></textarea>
                    </div>
                    <button class="send-btn" id="sendBtn" onclick="sendMessage()">Send</button>
                    <button class="stop-btn" id="stopBtn" onclick="stopGeneration()">Stop</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentEventSource = null;
        let currentTheme = 'dark';
        let isGenerating = false;

        // Configure marked.js
        marked.setOptions({
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (e) {}
                }
                return hljs.highlightAuto(code).value;
            },
            breaks: true,
            gfm: true
        });

        // Custom renderer for code blocks with copy button
        const renderer = new marked.Renderer();
        const originalCodeRenderer = renderer.code.bind(renderer);
        
        renderer.code = function(code, language) {
            const validLang = language || 'text';
            const langName = validLang.charAt(0).toUpperCase() + validLang.slice(1);
            const highlighted = language && hljs.getLanguage(language)
                ? hljs.highlight(code, { language: language }).value
                : hljs.highlightAuto(code).value;
            
            return `
                <pre>
                    <div class="code-header">
                        <span class="code-language">${langName}</span>
                        <button class="copy-code-btn" onclick="copyCode(this, \`${code.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">
                            Copy
                        </button>
                    </div>
                    <div class="code-content">
                        <code class="hljs language-${validLang}">${highlighted}</code>
                    </div>
                </pre>
            `;
        };

        marked.use({ renderer });

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            createParticles();
            checkStatus();
            loadHistory();
            autoResizeTextarea();
        });

        // Create particle field
        function createParticles() {
            const field = document.getElementById('particleField');
            for (let i = 0; i < 30; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 6 + 's';
                particle.style.animationDuration = (Math.random() * 4 + 4) + 's';
                field.appendChild(particle);
            }
        }

        // Check Ollama status
        async function checkStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                const statusDot = document.getElementById('statusDot');
                if (data.ok) {
                    statusDot.classList.remove('offline');
                } else {
                    statusDot.classList.add('offline');
                }
            } catch (error) {
                document.getElementById('statusDot').classList.add('offline');
            }
        }

        // Load chat history
        async function loadHistory() {
            try {
                const response = await fetch('/history');
                const data = await response.json();
                const historyDiv = document.getElementById('chatHistory');
                historyDiv.innerHTML = '';
                
                data.history.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'chat-history-item';
                    div.textContent = item.title;
                    div.onclick = () => loadSession(item.id);
                    historyDiv.appendChild(div);
                });
            } catch (error) {
                console.error('Error loading history:', error);
            }
        }

        // Send message
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message || isGenerating) return;

            // Hide empty state
            document.getElementById('emptyState').style.display = 'none';

            // Add user message
            addMessage(message, 'user');
            input.value = '';
            input.style.height = 'auto';

            // Show typing indicator
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message ai';
            typingDiv.innerHTML = `
                <div class="typing-indicator active">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;
            document.getElementById('messagesContainer').appendChild(typingDiv);
            scrollToBottom();

            // Toggle buttons
            isGenerating = true;
            document.getElementById('sendBtn').style.display = 'none';
            document.getElementById('stopBtn').classList.add('active');

            // Stream response
            try {
                currentEventSource = new EventSource('/chat?message=' + encodeURIComponent(message));
                let aiMessageDiv = null;
                let aiMessageContent = '';

                currentEventSource.onmessage = function(event) {
                    if (event.data === '[DONE]') {
                        currentEventSource.close();
                        typingDiv.remove();
                        isGenerating = false;
                        document.getElementById('sendBtn').style.display = 'block';
                        document.getElementById('stopBtn').classList.remove('active');
                        loadHistory();
                        return;
                    }

                    if (event.data.startsWith('[ERROR]')) {
                        typingDiv.remove();
                        addMessage('Error: ' + event.data.substring(7), 'ai');
                        isGenerating = false;
                        document.getElementById('sendBtn').style.display = 'block';
                        document.getElementById('stopBtn').classList.remove('active');
                        return;
                    }

                    // Remove typing indicator on first token
                    if (!aiMessageDiv) {
                        typingDiv.remove();
                        aiMessageDiv = addMessage('', 'ai');
                    }

                    aiMessageContent += event.data;
                    const bubble = aiMessageDiv.querySelector('.message-bubble');
                    bubble.innerHTML = marked.parse(aiMessageContent);

                    scrollToBottom();
                };

                currentEventSource.onerror = function() {
                    currentEventSource.close();
                    typingDiv.remove();
                    isGenerating = false;
                    document.getElementById('sendBtn').style.display = 'block';
                    document.getElementById('stopBtn').classList.remove('active');
                };
            } catch (error) {
                console.error('Error:', error);
                typingDiv.remove();
                isGenerating = false;
                document.getElementById('sendBtn').style.display = 'block';
                document.getElementById('stopBtn').classList.remove('active');
            }
        }

        // Stop generation
        function stopGeneration() {
            if (currentEventSource) {
                currentEventSource.close();
                currentEventSource = null;
            }
            isGenerating = false;
            document.getElementById('sendBtn').style.display = 'block';
            document.getElementById('stopBtn').classList.remove('active');
            
            const typingIndicators = document.querySelectorAll('.typing-indicator');
            typingIndicators.forEach(el => el.parentElement.remove());
        }

        // Add message to UI
        function addMessage(text, sender) {
            const messagesContainer = document.getElementById('messagesContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const content = sender === 'ai' ? marked.parse(text) : text;
            
            messageDiv.innerHTML = `
                <div class="message-bubble">${content}</div>
                <div class="message-actions">
                    <button class="action-btn" onclick="copyMessage(this)">Copy</button>
                    ${sender === 'ai' ? '<button class="action-btn" onclick="regenerate()">Regenerate</button>' : ''}
                </div>
            `;
            
            messagesContainer.appendChild(messageDiv);
            scrollToBottom();
            return messageDiv;
        }

        // Copy code from code block
        function copyCode(btn, code) {
            navigator.clipboard.writeText(code).then(() => {
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy:', err);
                btn.textContent = 'Failed';
                setTimeout(() => {
                    btn.textContent = 'Copy';
                }, 2000);
            });
        }

        // Copy message
        function copyMessage(btn) {
            const bubble = btn.closest('.message').querySelector('.message-bubble');
            const text = bubble.innerText;
            navigator.clipboard.writeText(text).then(() => {
                btn.textContent = 'Copied!';
                setTimeout(() => btn.textContent = 'Copy', 2000);
            }).catch(err => {
                console.error('Failed to copy:', err);
            });
        }

        // Regenerate last response
        async function regenerate() {
            // Remove last AI message
            const messages = document.querySelectorAll('.message.ai');
            if (messages.length > 0) {
                messages[messages.length - 1].remove();
            }

            try {
                const response = await fetch('/regenerate', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    // The last user message will be re-sent automatically
                    // Trigger send with the stored message
                    sendMessage();
                }
            } catch (error) {
                console.error('Error regenerating:', error);
            }
        }

        // New chat
        async function newChat() {
            try {
                const response = await fetch('/new', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    document.getElementById('messagesContainer').innerHTML = `
                        <div class="empty-state" id="emptyState">
                            <h2>Gemma AI Assistant</h2>
                            <p>Start a conversation with perfect memory retention</p>
                        </div>
                    `;
                    loadHistory();
                }
            } catch (error) {
                console.error('Error creating new chat:', error);
            }
        }

        // Export chat
        async function exportChat() {
            try {
                const response = await fetch('/export');
                const data = await response.json();
                
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `chat-export-${new Date().toISOString()}.json`;
                a.click();
                URL.revokeObjectURL(url);
            } catch (error) {
                console.error('Error exporting chat:', error);
            }
        }

        // Toggle theme
        function toggleTheme() {
            currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', currentTheme);
            document.getElementById('themeIcon').textContent = currentTheme === 'dark' ? '☀️' : '🌙';
        }

        // Toggle sidebar
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
        }

        // Handle keyboard
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        // Auto-resize textarea
        function autoResizeTextarea() {
            const textarea = document.getElementById('messageInput');
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
        }

        // Scroll to bottom
        function scrollToBottom() {
            const container = document.getElementById('messagesContainer');
            container.scrollTop = container.scrollHeight;
        }

        // Load session
        async function loadSession(sessionId) {
            // Not implemented in this version - would require backend support
            console.log('Load session:', sessionId);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main page"""
    response = make_response(render_template_string(HTML_TEMPLATE))
    
    # Set session cookie if not exists
    if not request.cookies.get('session_id'):
        response.set_cookie('session_id', str(uuid.uuid4()), max_age=30*24*60*60)
    
    return response

@app.route('/status')
def status():
    """Check Ollama status"""
    try:
        response = requests.get(f"{OLLAMA_API.replace('/api/chat', '/api/tags')}", timeout=2)
        return jsonify({"ok": response.status_code == 200})
    except:
        return jsonify({"ok": False})

@app.route('/chat')
def chat():
    """Stream chat responses using SSE"""
    message = request.args.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Get session ID
    sid = get_session_id()

    def generate():
        try:
            # Get conversation history
            conversation = get_conversation(sid)
            
            # Build messages for Ollama with system prompt
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Add conversation history
            for msg in conversation:
                messages.append(msg)
            
            # Add new user message
            user_message = {"role": "user", "content": message}
            messages.append(user_message)
            
            # Call Ollama API with streaming
            response = requests.post(
                OLLAMA_API,
                json={
                    "model": MODEL_NAME,
                    "messages": messages,
                    "stream": True
                },
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                yield f"data: [ERROR]Ollama API error: {response.status_code}\n\n"
                return
            
            # Stream the response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if 'message' in chunk and 'content' in chunk['message']:
                            content = chunk['message']['content']
                            full_response += content
                            yield f"data: {content}\n\n"
                    except json.JSONDecodeError:
                        continue
            
            # Save conversation
            conversation.append(user_message)
            conversation.append({"role": "assistant", "content": full_response})
            
            # Auto-generate title from first message
            title = None
            if len(conversation) == 2:  # First exchange
                title = message[:30] + "..." if len(message) > 30 else message
            
            save_conversation(sid, conversation, title)
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: [ERROR]{str(e)}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/new', methods=['POST'])
def new_chat():
    """Create a new chat session"""
    try:
        # Create new session ID
        new_sid = str(uuid.uuid4())
        response = make_response(jsonify({"success": True, "session_id": new_sid}))
        response.set_cookie('session_id', new_sid, max_age=30*24*60*60)
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history')
def history():
    """Get chat history"""
    try:
        sessions = load_sessions()
        history_list = []
        
        for sid, data in list(sessions.items())[-20:]:  # Last 20 sessions
            history_list.append({
                "id": sid,
                "title": data.get('title', 'New Chat'),
                "created_at": data.get('created_at', '')
            })
        
        return jsonify({"history": reversed(history_list)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/regenerate', methods=['POST'])
def regenerate():
    """Regenerate last response"""
    try:
        sid = get_session_id()
        conversation = get_conversation(sid)
        
        # Remove last assistant message if exists
        if conversation and conversation[-1]['role'] == 'assistant':
            conversation.pop()
            save_conversation(sid, conversation)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/export')
def export():
    """Export current chat"""
    try:
        sid = get_session_id()
        conversation = get_conversation(sid)
        sessions = load_sessions()
        
        export_data = {
            "session_id": sid,
            "title": sessions.get(sid, {}).get('title', 'Chat Export'),
            "created_at": sessions.get(sid, {}).get('created_at', ''),
            "messages": conversation
        }
        
        return jsonify(export_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("=" * 60)
    print("  Gemma Ollama Chatbot Server Starting")
    print("=" * 60)
    print(f"  URL: http://0.0.0.0:9087")
    print(f"  Model: {MODEL_NAME}")
    print(f"  Storage: {STORAGE_FILE}")
    print("=" * 60)
    print("\n⚠️  Make sure Ollama is running:")
    print("     ollama run gemma:2b")
    print("\n🚀 Server starting...\n")
    
    app.run(host="0.0.0.0", port=9087, debug=False, threaded=True)
