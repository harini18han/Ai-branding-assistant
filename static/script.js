document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const welcomeScreen = document.getElementById('welcome-screen');
    const generatorScreen = document.getElementById('generator-screen');
    const startBtn = document.getElementById('start-btn');

    startBtn.addEventListener('click', () => {
        welcomeScreen.classList.remove('active');
        welcomeScreen.classList.add('hidden');
        setTimeout(() => {
            generatorScreen.classList.remove('hidden');
            generatorScreen.classList.add('active');
        }, 500); // Wait for fade out
    });

    // Generation
    const generateBtn = document.getElementById('generate-btn');
    const productIdeaInput = document.getElementById('product-idea');
    const loadingDiv = document.getElementById('loading');
    const resultContainer = document.getElementById('result-container');
    const brandingContent = document.getElementById('branding-content');
    const downloadBtn = document.getElementById('download-btn');

    let currentPdfUrl = null;

    generateBtn.addEventListener('click', async () => {
        const product = productIdeaInput.value.trim();
        if (!product) {
            alert('Please enter a product idea!');
            return;
        }

        // UI State
        generateBtn.disabled = true;
        loadingDiv.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        downloadBtn.classList.add('hidden');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ product: product })
            });

            if (!response.ok) {
                throw new Error('Failed to generate branding');
            }

            const data = await response.json();
            
            // Parse Markdown
            brandingContent.innerHTML = marked.parse(data.branding_text);
            
            // Setup download URL
            if (data.pdf_url) {
                currentPdfUrl = data.pdf_url;
                downloadBtn.classList.remove('hidden');
            }

            resultContainer.classList.remove('hidden');

        } catch (error) {
            console.error(error);
            alert('An error occurred during generation. Make sure the backend is running.');
        } finally {
            generateBtn.disabled = false;
            loadingDiv.classList.add('hidden');
        }
    });

    downloadBtn.addEventListener('click', () => {
        if (currentPdfUrl) {
            window.open(currentPdfUrl, '_blank');
        }
    });

    // Chatbot
    const chatbotWidget = document.getElementById('chatbot-widget');
    const chatbotHeader = document.getElementById('chatbot-header');
    const chatbotBody = document.getElementById('chatbot-body');
    const chatToggle = document.getElementById('chat-toggle');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatMessages = document.getElementById('chat-messages');

    let chatOpen = true;

    chatbotHeader.addEventListener('click', () => {
        chatOpen = !chatOpen;
        if (chatOpen) {
            chatbotBody.classList.remove('hidden');
            chatToggle.textContent = '_';
        } else {
            chatbotBody.classList.add('hidden');
            chatToggle.textContent = '□';
        }
    });

    const addMessage = (text, sender, isHtml = false) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        if (isHtml) {
            msgDiv.innerHTML = text;
            msgDiv.querySelectorAll('p').forEach(p => p.style.margin = '0 0 0.5rem 0');
            msgDiv.querySelectorAll('p:last-child').forEach(p => p.style.margin = '0');
        } else {
            msgDiv.textContent = text;
        }
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msgDiv;
    };

    const sendMessage = async () => {
        const text = chatInput.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        chatInput.value = '';
        chatInput.disabled = true;
        chatSend.disabled = true;

        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message ai';
        loadingDiv.id = loadingId;
        loadingDiv.textContent = '...';
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: text })
            });

            if (!response.ok) {
                throw new Error('Chat failed');
            }

            const data = await response.json();
            document.getElementById(loadingId).remove();
            
            // Parse Markdown for chat response
            addMessage(marked.parse(data.response), 'ai', true);

        } catch (error) {
            console.error(error);
            document.getElementById(loadingId).textContent = 'Sorry, an error occurred.';
        } finally {
            chatInput.disabled = false;
            chatSend.disabled = false;
            chatInput.focus();
        }
    };

    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
