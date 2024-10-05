let currentQuestionIndex = 0;  // Current question index ko 0 se initialize kar raha hai
let illnessDetected = false;  // Illness detect hone ka flag, default false
let chatWindowOpen = false;  // Chat window open hone ka flag, default false

document.getElementById('sendBtn').addEventListener('click', function() {  // Send button par click event listener
    const chatWindow = document.getElementById('chatbotWindow');  // Chat window ko get kar raha hai
    // Chat window ka display toggle kar raha hai
    chatWindow.style.display = chatWindow.style.display === 'none' || chatWindow.style.display === '' ? 'flex' : 'none';
    chatWindowOpen = chatWindow.style.display === 'flex';  // Flag update kar raha hai
});

document.getElementById('sendMessageBtn').addEventListener('click', handleSend);  // Send message button par event listener
document.getElementById('chatInput').addEventListener('keypress', function(event) {  // Chat input par keypress event listener
    if (event.key === 'Enter') {  // Agar Enter key press ki gayi
        event.preventDefault();  // Default action ko prevent kar raha hai
        handleSend();  // Handle send function ko call kar raha hai
    }
});

async function handleSend() {  // Send karne ke liye function
    const userMessage = document.getElementById('chatInput').value.trim();  // User message ko get aur trim kar raha hai
    const chatWindow = document.getElementById('chatBody');  // Chat body ko get kar raha hai

    if (!chatWindowOpen) {  // Agar chat window open nahi hai
        return;  // Function ko end kar do
    }

    if (!userMessage) {  // Agar user message khaali hai
        return;  // Function ko end kar do
    }

    chatWindow.innerHTML += `<div class="message user-message">You: ${sanitizeInput(userMessage)}</div>`;  // User message ko chat window me add kar raha hai
    document.getElementById('chatInput').value = '';  // Input field ko khaali kar raha hai

    const loadingMessage = document.createElement('div');  // Loading message create kar raha hai
    loadingMessage.innerText = 'Bot: ...';  // Loading message set kar raha hai
    chatWindow.appendChild(loadingMessage);  // Loading message ko chat window me add kar raha hai

    try {
        const response = await fetch('/get_response', {  // Server se response fetch kar raha hai
            method: 'POST',  // POST method use kar raha hai
            headers: { 'Content-Type': 'application/json' },  // Content type ko JSON set kar raha hai
            body: JSON.stringify({ message: userMessage })  // User message ko JSON format me send kar raha hai
        });

        if (!response.ok) {  // Agar response theek nahi hai
            throw new Error('Network response was not ok');  // Error throw kar raha hai
        }

        const data = await response.json();  // Response ko JSON format me parse kar raha hai
        chatWindow.removeChild(loadingMessage);  // Loading message ko remove kar raha hai

        const formattedResponse = formatResponse(data.response);  // Response ko format kar raha hai
        typeMessage(formattedResponse, chatWindow);  // Formatted message ko type kar raha hai chat window me

        if (data.response.includes('recommend')) {  // Agar response me 'recommend' shamil hai
            currentQuestionIndex = 0;  // Current question index ko reset kar raha hai
            illnessDetected = false;  // Illness detect flag ko reset kar raha hai
        }
    } catch (error) {  // Agar koi error aata hai
        console.error('Error fetching response:', error);  // Error ko console me log kar raha hai
        chatWindow.removeChild(loadingMessage);  // Loading message ko remove kar raha hai
        chatWindow.innerHTML += `<div class="message bot-message">Bot: Sorry, there was an error processing your request.</div>`;  // Error message show kar raha hai
    }
}

function formatResponse(response) {  // Response format karne ka function
    return response;  // Abhi koi formatting nahi ho rahi hai, bas response return kar raha hai
}

function typeMessage(message, chatWindow) {  // Type karne ka function
    const botMessageDiv = document.createElement('div');  // Bot message div create kar raha hai
    botMessageDiv.className = 'message bot-message';  // Bot message div ko class assign kar raha hai
    chatWindow.appendChild(botMessageDiv);  // Bot message div ko chat window me add kar raha hai

    let index = 0;  // Index ko 0 se initialize kar raha hai
    const typingSpeed = 5;  // Typing speed set kar raha hai

    function type() {  // Typing function
        if (index < message.length) {  // Agar index message ke length se chhota hai
            botMessageDiv.innerHTML += message.charAt(index);  // Character ko add kar raha hai
            index++;  // Index ko increment kar raha hai

            chatWindow.scrollTop = chatWindow.scrollHeight;  // Scroll ko bottom par le ja raha hai

            setTimeout(type, typingSpeed);  // Typing function ko delay ke saath call kar raha hai
        }
    }

    type();  // Typing function ko call kar raha hai
}

function sanitizeInput(input) {  // Input ko sanitize karne ka function
    return input.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');  // Special characters ko replace kar raha hai
}
