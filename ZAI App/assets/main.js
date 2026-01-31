document.getElementById('send-btn').addEventListener('click', sendMessage);

function sendMessage() {
    const input = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');

    if (input.value.trim() === "") return;

    // Create User Message Bubble
    const userMsg = `
        <div class="message user-msg">
            <div class="avatar">U</div>
            <div class="text">${input.value}</div>
        </div>`;
    
    chatWindow.innerHTML += userMsg;
    
    // Clear Input
    const query = input.value;
    input.value = "";
    
    // Auto-scroll
    chatWindow.scrollTop = chatWindow.scrollHeight;

function sendMessage() {
    const input = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const engine = document.getElementById('engine-select').value;

    if (input.value.trim() === "") return;

    // 1. Add User Message
    chatWindow.innerHTML += `<div class="message user-msg"><div class="text">${input.value}</div></div>`;
    
    const userQuery = input.value;
    input.value = "";

    // 2. Show "Thinking..." with Zega Green Glow
    const thinkingId = "think-" + Date.now();
    chatWindow.innerHTML += `
        <div class="message ai-msg" id="${thinkingId}">
            <div class="avatar">Z</div>
            <div class="text" style="color: #58f01b; font-style: italic;">ZEGA is processing via ${engine}...</div>
        </div>`;
    
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // 3. THE REAL CONNECTION
    // This calls a function in your Python main.py
    if (window.pybridge) {
        window.pybridge.process_ai_query(userQuery, engine, (response) => {
            document.getElementById(thinkingId).querySelector('.text').innerText = response;
        });
    } else {
        // Fallback if running in browser without Python
        setTimeout(() => {
            document.getElementById(thinkingId).querySelector('.text').innerText = 
            "Error: PyBridge not detected. Run main.py to connect to the LPU.";
        }, 1000);
    }
}