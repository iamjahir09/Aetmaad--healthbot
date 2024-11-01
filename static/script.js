function toggleDisorderInput() {  
    const yesRadio = document.getElementById('yes');  
    const disorderInput = document.getElementById('disorder');  
    disorderInput.style.display = yesRadio.checked ? 'block' : 'none';  
}

document.getElementById('userForm').addEventListener('submit', function (event) {  
    event.preventDefault();  

    const clientName = document.getElementById('clientName').value;  
    const counsellorName = document.getElementById('counsellorName').value;  
    const mobile = document.getElementById('mobile').value;  
    const height = {  
        feet: document.getElementById('feet').value,  
        inches: document.getElementById('inches').value  
    };  
    const weight = document.getElementById('weight').value;  
    const age = document.getElementById('age').value;  
    const sleepTime = document.getElementById('sleepTime').value;  
    const wakeTime = document.getElementById('wakeTime').value;  
    const location = document.getElementById('location').value;  
    const maritalStatus = document.querySelector('input[name="maritalStatus"]:checked').value;  
    const geneticDisorder = document.querySelector('input[name="genetic_disorder"]:checked').value;  
    const disorder = geneticDisorder === 'Yes' ? document.getElementById('disorderDetail').value : '';  

    const formData = {  
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

    console.log('Form Data:', formData);  

    fetch('/submit_form', {  
        method: 'POST',  
        headers: {
            'Content-Type': 'application/json'  
        },
        body: JSON.stringify(formData)  
    })
    .then(response => response.json())  
    .then(data => {
        alert(data.message);  
        window.location.href = `/chatbot?name=${encodeURIComponent(clientName)}`;  
    })
    .catch(error => console.error('Error:', error));  
});

// Function to send illness data from chat
function sendIllnessData(illness) {
    fetch('/store_illness', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ illness })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
    })
    .catch(error => console.error('Error:', error));
}
