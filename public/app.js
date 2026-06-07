const chatContainer = document.getElementById('chatContainer');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');


// --- MODAL WINDOW MANAGEMENT ---
const loginBtn = document.getElementById('loginBtn');
const loginModal = document.getElementById('loginModal');
const closeModal = document.getElementById('closeModal');

// New Registration Modal Elements
const registerModal = document.getElementById('registerModal');
const closeRegisterModal = document.getElementById('closeRegisterModal');
const openRegisterLink = document.getElementById('openRegister');
const openLoginLink = document.getElementById('openLogin');

// Open Login Modal from Header
loginBtn.addEventListener('click', () => {
    loginModal.classList.remove('hidden');
    registerModal.classList.add('hidden');
});

// Close Buttons
closeModal.addEventListener('click', () => loginModal.classList.add('hidden'));
closeRegisterModal.addEventListener('click', () => registerModal.classList.add('hidden'));

// Toggle from Login Screen -> Create Account Screen
openRegisterLink.addEventListener('click', (e) => {
    e.preventDefault();
    loginModal.classList.add('hidden');
    registerModal.classList.remove('hidden');
});

// Toggle from Create Account Screen -> Login Screen
openLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    registerModal.classList.add('hidden');
    loginModal.classList.remove('hidden');
});

// Close modals if user clicks anywhere outside the white boxes
window.addEventListener('click', (e) => {
    if (e.target === loginModal) loginModal.classList.add('hidden');
    if (e.target === registerModal) registerModal.classList.add('hidden');
});

// Prevent form submissions from reloading page since they are mockups
document.getElementById('loginForm').addEventListener('submit', (e) => e.preventDefault());
document.getElementById('registerForm').addEventListener('submit', (e) => e.preventDefault());
// Handle Messaging
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    // 1. Render User Bubble
    appendUserMessage(text);
    userInput.value = '';

    // 2. Render Loading Spinner Indicator
    const loadingId = appendLoadingIndicator();

    try {
        // Here we hit your local Python API wrapper backend (e.g. FastAPI/Flask running on port 8000)
        // Which handles the Supabase queries and cached exchange computations under the hood
        const response = await fetch('http://127.0.0.1:8001/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        
        removeLoadingIndicator(loadingId);

        if (response.ok) {
            const data = await response.json();
            appendBotMessage(data.reply);
        } else {
            // Fallback default message on connection errors
            appendBotMessage("I don't know exactly what it is, but I can help you with finding a university or suitable menu for you!");
        }
    } catch (error) {
        removeLoadingIndicator(loadingId);
        // Fallback default message when server isn't running or unknown question
        appendBotMessage("I don't know exactly what it is, but I can help you with finding a university or suitable menu for you!");
    }
});

function appendUserMessage(text) {
    const html = `
        <div class="flex items-start gap-3 max-w-[75%] ml-auto justify-end user-message-appear">
            <div class="bg-rose-400 text-white rounded-2xl rounded-tr-none px-4 py-3 shadow-sm text-sm leading-relaxed">
                ${escapeHTML(text)}
            </div>
        </div>
    `;
    chatContainer.insertAdjacentHTML('beforeend', html);
    scrollToBottom();
}

function appendBotMessage(text) {
    // Convert the raw Markdown from the Python agent into structured HTML elements
    // breakless: true ensures line breaks are respected naturally
    const formattedHtml = marked.parse(text, { breaks: true });

    const html = `
        <div class="flex items-start gap-3 max-w-[75%] message-appear">
            <img src="./images/bot-avatar.png" alt="Bot Avatar" class="w-10 h-10 rounded-full border border-rose-200 bg-white object-cover shrink-0">
            <div class="bg-rose-100 text-rose-900 rounded-2xl rounded-tl-none px-5 py-3 shadow-sm text-sm leading-relaxed markdown-content w-full">
                ${formattedHtml}
            </div>
        </div>
    `;
    chatContainer.insertAdjacentHTML('beforeend', html);
    scrollToBottom();
}

function appendLoadingIndicator() {
    const id = 'loading-' + Date.now();
    const html = `
        <div id="${id}" class="flex items-start gap-3 max-w-[75%] message-appear">
            <img src="./images/bot-avatar.png" alt="Bot Avatar" class="w-10 h-10 rounded-full border border-rose-200 bg-white object-cover">
            <div class="bg-rose-100 text-rose-400 rounded-2xl rounded-tl-none px-5 py-3 shadow-sm text-sm flex items-center gap-1">
                <span class="w-2 h-2 bg-rose-400 rounded-full animate-bounce"></span>
                <span class="w-2 h-2 bg-rose-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                <span class="w-2 h-2 bg-rose-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
            </div>
        </div>
    `;
    chatContainer.insertAdjacentHTML('beforeend', html);
    scrollToBottom();
    return id;
}

function removeLoadingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}