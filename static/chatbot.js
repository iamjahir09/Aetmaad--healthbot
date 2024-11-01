let currentQuestionIndex = 0;  // Current question index
let illnessDetected = false;    // Illness detection status
let chatWindowOpen = false;     // Chat window status
let chatHistory = [];           // Array to store chat messages
let selectedHospital = null;    // Selected hospital for appointment
const apiKey = '0be6c695a36a49269fd62d58d7c2497b'; // Replace with your actual API key

// Predefined healthcare facilities
const healthcareFacilities = {
    "latur": {
        hospitals: [
            { name: "KEM Hospital", address: "Latur, Maharashtra" },
            { name: "Jehangir Hospital", address: "Latur, Maharashtra" },
        ],
        clinics: [
            { name: "Local Clinic 1", address: "Latur, Maharashtra" },
            { name: "Local Clinic 2", address: "Latur, Maharashtra" },
        ]
    },
};

document.addEventListener("DOMContentLoaded", function() {
    const sendBtn = document.getElementById("sendBtn");
    const menuBtn = document.getElementById("menuBtn");
    const slideMenu = document.getElementById("slideMenu");
    const historyMenuBtn = document.getElementById("historyMenuBtn");
    const bookAppointmentMenuBtn = document.getElementById("bookAppointmentMenuBtn");
    const closeMenuBtn = document.getElementById("closeMenuBtn");
    const chatbotWindow = document.getElementById("chatbotWindow");
    const historyWindow = document.getElementById("historyWindow");
    const closeHistoryBtn = document.getElementById("closeHistoryBtn");
    const sendMessageBtn = document.getElementById("sendMessageBtn");
    const chatInput = document.getElementById("chatInput");
    const chatBody = document.getElementById("chatBody");
    const historyBody = document.getElementById("historyBody");
    const clinicWindow = document.getElementById("clinicWindow");
    const closeClinicBtn = document.getElementById("closeClinicBtn");
    const hospitalDropdownContainer = document.getElementById("hospitalDropdownContainer");
    const hospitalDropdown = document.getElementById("hospitalDropdown");
    const detailsWindow = document.getElementById("detailsWindow");
    const detailsBody = document.getElementById("detailsBody");
    const closeDetailsBtn = document.getElementById("closeDetailsBtn");
    const downloadReceiptBtn = document.getElementById("downloadReceiptBtn"); // Added for download receipt
    const bookAppointmentBtn = document.getElementById("bookAppointmentBtn"); // Added for booking appointment

    // Toggle the slide menu
    menuBtn.addEventListener("click", function() {
        slideMenu.style.display = slideMenu.style.display === 'block' ? 'none' : 'block';
    });

    // Close the slide menu
    closeMenuBtn.addEventListener("click", function() {
        slideMenu.style.display = 'none';
    });

    // Handle the history button in the menu
    historyMenuBtn.addEventListener("click", function() {
        showChatHistory();
        slideMenu.style.display = 'none'; // Close menu after selecting
    });

    // Handle the book appointment button in the menu
    bookAppointmentMenuBtn.addEventListener("click", function() {
        getUserArea();
        slideMenu.style.display = 'none'; // Close menu after selecting
    });

    // Close button functionality for history window
    closeHistoryBtn.addEventListener("click", function() {
        historyWindow.style.display = 'none'; // Hide history window
    });

    // Close button functionality for details window
    closeDetailsBtn.addEventListener("click", function() {
        closeDetailsAndReset(); // Close details and reset
    });

    sendBtn.addEventListener("click", function() {
        chatbotWindow.style.display = chatbotWindow.style.display === 'none' || chatbotWindow.style.display === '' ? 'flex' : 'none';
        chatWindowOpen = chatbotWindow.style.display === 'flex';
        if (chatWindowOpen) {
            chatInput.focus();
        }
    });

    sendMessageBtn.addEventListener("click", handleSend);

    chatInput.addEventListener("keypress", function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleSend();
        }
    });

    async function handleSend() {
        const userMessage = chatInput.value.trim();
        const chatWindow = chatBody;

        if (!chatWindowOpen || !userMessage) {
            return;
        }

        chatHistory.push(`User: ${sanitizeInput(userMessage)}`);
        chatWindow.innerHTML += `<div class="message user-message">You: ${sanitizeInput(userMessage)}</div>`;
        chatInput.value = '';

        const loadingMessage = document.createElement('div');
        loadingMessage.innerText = 'Bot: ...';
        chatWindow.appendChild(loadingMessage);

        try {
            const response = await fetch('/get_response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage })
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            chatWindow.removeChild(loadingMessage);
            typeMessage(formatResponse(data.response), chatWindow);
            chatHistory.push(`Bot: ${data.response}`);
        } catch (error) {
            console.error('Error fetching response:', error);
            chatWindow.removeChild(loadingMessage);
            chatWindow.innerHTML += `<div class="message bot-message">Bot: Sorry, there was an error processing your request.</div>`;
        }
    }

    function sanitizeInput(input) {
        return input.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function showChatHistory() {
        historyBody.innerHTML = '';  // Clear current history display
        chatHistory.forEach(msg => {
            const historyMessageElement = document.createElement("div");
            historyMessageElement.classList.add("message");
            historyMessageElement.textContent = msg;
            historyBody.appendChild(historyMessageElement);
        });
        historyWindow.style.display = 'block'; // Show history window
    }

    // Function to get user's area
    function getUserArea() {
        const userArea = prompt("Please enter your area:");
        if (userArea && healthcareFacilities[userArea.toLowerCase()]) {
            populateHospitalDropdown(healthcareFacilities[userArea.toLowerCase()].hospitals);
            hospitalDropdownContainer.style.display = 'block'; // Show dropdown after area entry
        } else {
            alert("No data available for this area.");
            getLocation(); // Fallback to geolocation
        }
    }

    // Function to get user's location
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition, showError);
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    }

    function showPosition(position) {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        showNearbyClinics(lat, lng); // Call to fetch nearby clinics
    }

    function showError(error) {
        switch (error.code) {
            case error.PERMISSION_DENIED:
                alert("User denied the request for Geolocation.");
                break;
            case error.POSITION_UNAVAILABLE:
                alert("Location information is unavailable.");
                break;
            case error.TIMEOUT:
                alert("The request to get user location timed out.");
                break;
            case error.UNKNOWN_ERROR:
                alert("An unknown error occurred.");
                break;
        }
    }

    async function showNearbyClinics(lat, lng) {
        const requestOptions = {
            method: 'GET',
        };

        const url = `https://api.geoapify.com/v2/places?categories=healthcare.hospital&filter=rect:${lng - 0.9},${lat - 0.9},${lng + 0.9},${lat + 0.9}&limit=20&apiKey=${apiKey}`;

        try {
            const response = await fetch(url, requestOptions);
            if (!response.ok) throw new Error('Network response was not ok');

            const clinics = await response.json();
            displayClinics(clinics.features);
        } catch (error) {
            console.error('Error fetching nearby clinics:', error);
            alert('Could not fetch nearby clinics.');
        }
    }

    function displayClinics(clinics) {
        const clinicBody = document.getElementById('clinicBody');
        clinicBody.innerHTML = '';

        if (clinics.length === 0) {
            clinicBody.innerHTML = '<div>No clinics found in your area.</div>';
        } else {
            clinics.forEach(clinic => {
                const clinicDiv = document.createElement('div');
                clinicDiv.innerText = `${clinic.properties.name} - ${clinic.properties.address_line1}`;
                clinicBody.appendChild(clinicDiv);
            });
        }

        clinicWindow.style.display = 'block';
    }

    function populateHospitalDropdown(hospitals) {
        hospitalDropdown.innerHTML = '<option value="">Select a Hospital</option>';
        hospitals.forEach(hospital => {
            const option = document.createElement('option');
            option.value = hospital.name;
            option.textContent = `${hospital.name} - ${hospital.address}`;
            hospitalDropdown.appendChild(option);
        });
    }

    document.getElementById("viewHospitalBtn").addEventListener("click", function() {
        const selectedHospitalName = hospitalDropdown.value;
        if (selectedHospitalName) {
            const hospital = healthcareFacilities["latur"].hospitals.find(h => h.name === selectedHospitalName);
            if (hospital) {
                detailsBody.innerHTML = `Hospital: ${hospital.name}<br>Address: ${hospital.address}`;
                downloadReceiptBtn.style.display = 'block'; // Show download receipt button
                detailsWindow.style.display = 'block'; // Show details window
                selectedHospital = hospital.name; // Set the selected hospital
            }
        } else {
            alert("Please select a hospital from the dropdown.");
        }
    });

    // Book appointment button functionality
    bookAppointmentBtn.addEventListener("click", function() {
        alert("Your appointment has been booked. Please download your receipt.");
        downloadReceiptBtn.style.display = 'block'; // Show download receipt button
    });

    // Download receipt button functionality
    downloadReceiptBtn.addEventListener("click", function() {
        const { jsPDF } = window.jspdf; // Using jsPDF library
        const doc = new jsPDF();
        const receiptContent = `Receipt\n\nAppointment Details:\nHospital: ${selectedHospital}\nDate: ${new Date().toLocaleDateString()}\nThank you for using our service!`;
        
        doc.text(receiptContent, 10, 10);
        doc.save('receipt.pdf'); // File name for the PDF
    });

    function closeDetailsAndReset() {
        detailsWindow.style.display = 'none'; // Hide details window
        hospitalDropdownContainer.style.display = 'none'; // Hide dropdown
        downloadReceiptBtn.style.display = 'none'; // Hide download receipt button
    }

    function typeMessage(message, chatWindow) {
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'message bot-message';
        chatWindow.appendChild(botMessageDiv);

        let index = 0;
        const typingSpeed = 5;

        function type() {
            if (index < message.length) {
                botMessageDiv.innerHTML += message.charAt(index);
                index++;
                chatWindow.scrollTop = chatWindow.scrollHeight;
                setTimeout(type, typingSpeed);
            }
        }

        type();
    }

    function formatResponse(response) {
        return response; // You can modify this to format the response as needed
    }
});
