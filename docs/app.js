// ========== 설정 ==========
// 배포 후 Render 백엔드 URL로 변경하세요
const API_BASE = localStorage.getItem('api_url') || 'http://localhost:8000/api';

let token = localStorage.getItem('access_token');
let currentConversationId = null;

// ========== 화면 전환 ==========
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

// ========== 인증 ==========
async function handleAuth(isRegister) {
  const nickname = document.getElementById('nickname-input').value.trim();
  const password = document.getElementById('password-input').value.trim();
  const errorEl = document.getElementById('login-error');

  if (!nickname || !password) {
    errorEl.textContent = '닉네임과 비밀번호를 입력해주세요';
    errorEl.style.display = 'block';
    return;
  }

  const endpoint = isRegister ? '/auth/register' : '/auth/login';
  try {
    const res = await fetch(API_BASE + endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nickname, password }),
    });

    if (res.ok) {
      const data = await res.json();
      token = data.access_token;
      localStorage.setItem('access_token', token);
      errorEl.style.display = 'none';
      loadConversations();
    } else {
      const err = await res.json();
      errorEl.textContent = err.detail || (isRegister ? '이미 사용 중인 닉네임이에요' : '닉네임 또는 비밀번호가 틀렸어요');
      errorEl.style.display = 'block';
    }
  } catch {
    errorEl.textContent = '서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.';
    errorEl.style.display = 'block';
  }
}

function logout() {
  token = null;
  localStorage.removeItem('access_token');
  showScreen('login-screen');
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
}

// ========== 대화 목록 ==========
async function loadConversations() {
  showScreen('list-screen');
  const listEl = document.getElementById('conversation-list');

  try {
    const res = await fetch(API_BASE + '/conversations', {
      headers: authHeaders(),
    });

    if (res.status === 401) {
      logout();
      return;
    }

    const conversations = await res.json();

    if (conversations.length === 0) {
      listEl.innerHTML = `
        <div class="empty-list">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <p>아직 대화가 없어요<br>새 대화를 시작해보세요!</p>
        </div>`;
      return;
    }

    listEl.innerHTML = conversations.map(conv => `
      <div class="conv-item" onclick="openConversation('${conv.id}', '${escapeHtml(conv.title)}')">
        <div class="conv-avatar">🍼</div>
        <div class="conv-info">
          <div class="conv-title">${escapeHtml(conv.title)}</div>
          <div class="conv-time">${formatTime(conv.updated_at)}</div>
        </div>
        <button class="conv-delete" onclick="event.stopPropagation(); deleteConversation('${conv.id}')" title="삭제">×</button>
      </div>
    `).join('');
  } catch {
    listEl.innerHTML = '<div class="empty-list"><p>서버에 연결할 수 없어요</p></div>';
  }
}

async function createConversation() {
  try {
    const res = await fetch(API_BASE + '/conversations', {
      method: 'POST',
      headers: authHeaders(),
    });
    const conv = await res.json();
    openConversation(conv.id, conv.title);
  } catch {
    alert('대화를 생성할 수 없어요');
  }
}

async function deleteConversation(id) {
  if (!confirm('이 대화를 삭제할까요?')) return;
  await fetch(API_BASE + `/conversations/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  loadConversations();
}

// ========== 채팅 ==========
async function openConversation(id, title) {
  currentConversationId = id;
  document.getElementById('chat-title').textContent = title;
  showScreen('chat-screen');

  const container = document.getElementById('messages-container');
  container.innerHTML = '';

  try {
    const res = await fetch(API_BASE + `/conversations/${id}/messages`, {
      headers: authHeaders(),
    });
    const messages = await res.json();

    if (messages.length === 0) {
      container.innerHTML = `
        <div id="empty-chat" class="empty-chat">
          <div style="font-size:48px">🍼</div>
          <p>안녕! 육아톡이야 😊<br>무슨 이야기든 편하게 해줘!</p>
        </div>`;
    } else {
      messages.forEach(m => appendMessage(m.role, m.content));
    }

    scrollToBottom();
  } catch {
    container.innerHTML = '<div class="empty-chat"><p>메시지를 불러올 수 없어요</p></div>';
  }

  document.getElementById('message-input').focus();
}

function showList() {
  loadConversations();
}

function appendMessage(role, content) {
  const emptyChat = document.getElementById('empty-chat');
  if (emptyChat) emptyChat.remove();

  const container = document.getElementById('messages-container');
  const div = document.createElement('div');
  div.className = `message ${role}`;

  if (role === 'assistant') {
    div.innerHTML = `
      <div class="bubble">
        <div class="bot-label">육아톡 🍼</div>
        <div class="bubble-content">${escapeHtml(content)}</div>
      </div>`;
  } else {
    div.innerHTML = `<div class="bubble">${escapeHtml(content)}</div>`;
  }

  container.appendChild(div);
  return div;
}

function appendTypingIndicator() {
  const emptyChat = document.getElementById('empty-chat');
  if (emptyChat) emptyChat.remove();

  const container = document.getElementById('messages-container');
  const div = document.createElement('div');
  div.className = 'message assistant';
  div.id = 'typing-message';
  div.innerHTML = `
    <div class="bubble">
      <div class="bot-label">육아톡 🍼</div>
      <div class="bubble-content"><div class="typing-dots"><span></span><span></span><span></span></div></div>
    </div>`;
  container.appendChild(div);
  scrollToBottom();
  return div;
}

async function sendMessage() {
  const input = document.getElementById('message-input');
  const content = input.value.trim();
  if (!content || !currentConversationId) return;

  const sendBtn = document.getElementById('send-btn');
  sendBtn.disabled = true;
  input.value = '';
  input.style.height = 'auto';

  appendMessage('user', content);
  scrollToBottom();

  const typingEl = appendTypingIndicator();

  try {
    const res = await fetch(API_BASE + `/chat/${currentConversationId}`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ content }),
    });

    typingEl.remove();

    const botDiv = appendMessage('assistant', '');
    const bubbleContent = botDiv.querySelector('.bubble-content');
    let fullText = '';

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6));
            if (data.type === 'chunk') {
              fullText += data.content;
              bubbleContent.textContent = fullText;
              scrollToBottom();
            } else if (data.type === 'done') {
              // Update title if it was auto-generated
              try {
                const convRes = await fetch(API_BASE + '/conversations', {
                  headers: authHeaders(),
                });
                const convs = await convRes.json();
                const current = convs.find(c => c.id === currentConversationId);
                if (current) {
                  document.getElementById('chat-title').textContent = current.title;
                }
              } catch {}
            }
          } catch {}
        }
      }
    }
  } catch {
    typingEl.remove();
    appendMessage('assistant', '죄송해요, 오류가 발생했어요. 다시 시도해주세요.');
  }

  sendBtn.disabled = false;
  input.focus();
}

function handleKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

// ========== 유틸 ==========
function scrollToBottom() {
  const container = document.getElementById('messages-container');
  requestAnimationFrame(() => {
    container.scrollTop = container.scrollHeight;
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatTime(isoStr) {
  const d = new Date(isoStr);
  const now = new Date();
  const isToday = d.toDateString() === now.toDateString();
  const pad = n => String(n).padStart(2, '0');

  if (isToday) {
    return `${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }
  return `${pad(d.getMonth() + 1)}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

// ========== Textarea 자동 크기 조절 ==========
document.addEventListener('DOMContentLoaded', () => {
  const textarea = document.getElementById('message-input');
  textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
  });

  // 엔터키로 로그인
  document.getElementById('password-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleAuth(false);
  });
});

// ========== 초기화 ==========
(async function init() {
  if (token) {
    try {
      const res = await fetch(API_BASE + '/auth/me', {
        headers: authHeaders(),
      });
      if (res.ok) {
        loadConversations();
        return;
      }
    } catch {}
    // 토큰이 유효하지 않음
    localStorage.removeItem('access_token');
    token = null;
  }
  showScreen('login-screen');
})();
