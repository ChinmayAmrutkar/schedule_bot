// script.js

// IMPORTANT: Replace this URL with your deployed Google Cloud Function's URL
const backendUrl = 'https://process-schedule-request-725064701138.us-west1.run.app/';

const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const messagesContainer = document.getElementById('messages');

async function sendMessage() {
    const userMessage = userInput.value.trim();
    if (userMessage === '') {
        return;
    }

    // Display user's message
    appendMessage(userMessage, 'user');
    userInput.value = '';

    // Simulate thinking time
    appendMessage('Thinking...', 'bot');

    try {
        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: userMessage }),
        });
        
        const data = await response.json();
        
        // Remove the 'Thinking...' message
        messagesContainer.removeChild(messagesContainer.lastChild);

        // Display bot's response
        if (data.status === 'success') {
            appendMessage(data.message, 'bot');
        } else {
            appendMessage(data.message, 'bot');
        }

    } catch (error) {
        console.error('Error:', error);
        // Remove the 'Thinking...' message
        messagesContainer.removeChild(messagesContainer.lastChild);
        appendMessage('Oops! Something went wrong. Please try again.', 'bot');
    }
}

function appendMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    
    const p = document.createElement('p');
    p.textContent = text;
    messageDiv.appendChild(p);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight; // Auto-scroll to the bottom
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

