function toggleDisorderInput() {  // Genetic disorder input ko toggle karne ka function
    const yesRadio = document.getElementById('yes');  // Yes radio button ko get kar raha hai
    const disorderInput = document.getElementById('disorder');  // Disorder input field ko get kar raha hai
    // Agar Yes radio checked hai, toh disorder input ko block dikhayega, nahi toh none
    disorderInput.style.display = yesRadio.checked ? 'block' : 'none';
}

document.getElementById('userForm').addEventListener('submit', function (event) {  // Form submit hone par event listener
    event.preventDefault();  // Default form submission ko prevent kar raha hai

    const clientName = document.getElementById('clientName').value;  // Client name ko get kar raha hai
    const counsellorName = document.getElementById('counsellorName').value;  // Counsellor name ko get kar raha hai
    const mobile = document.getElementById('mobile').value;  // Mobile number ko get kar raha hai
    const height = {  // Height ko object me store kar raha hai
        feet: document.getElementById('feet').value,
        inches: document.getElementById('inches').value
    };
    const weight = document.getElementById('weight').value;  // Weight ko get kar raha hai
    const age = document.getElementById('age').value;  // Age ko get kar raha hai
    const sleepTime = document.getElementById('sleepTime').value;  // Sleep time ko get kar raha hai
    const wakeTime = document.getElementById('wakeTime').value;  // Wake time ko get kar raha hai
    const location = document.getElementById('location').value;  // Location ko get kar raha hai
    const maritalStatus = document.querySelector('input[name="maritalStatus"]:checked').value;  // Marital status ko get kar raha hai
    const geneticDisorder = document.querySelector('input[name="genetic_disorder"]:checked').value;  // Genetic disorder ko get kar raha hai
    // Agar genetic disorder 'Yes' hai, toh disorder ko get kar raha hai, nahi toh khaali
    const disorder = geneticDisorder === 'Yes' ? document.getElementById('disorder').value : '';

    const formData = {  // Form data ko ek object me store kar raha hai
        clientName,
        counsellorName,
        mobile,
        height,
        weight,
        age,
        sleepTime,
        wakeTime,
        location,
        maritalStatus,
        geneticDisorder,
        disorder
    };

    fetch('/submit_form', {  // Form data ko server par send kar raha hai
        method: 'POST',  // POST method use kar raha hai
        headers: {
            'Content-Type': 'application/json'  // Content type ko JSON set kar raha hai
        },
        body: JSON.stringify(formData)  // Form data ko JSON format me send kar raha hai
    })
    .then(response => response.json())  // Response ko JSON format me parse kar raha hai
    .then(data => {
        alert(data.message);  // Response message ko alert kar raha hai
        
        // User ko chatbot page par redirect kar raha hai
        window.location.href = `/chatbot?name=${encodeURIComponent(clientName)}`;
    })
    .catch(error => console.error('Error:', error));  // Error ko console me log kar raha hai
});
