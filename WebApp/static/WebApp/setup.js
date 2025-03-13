const form = document.getElementById('wifiform-form');
const ssidInput = form.elements['SSID'];
const pwdInput = form.elements['PWD'];

form.addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission
    if (ssidInput.value === '') {
        alert('SSID is required');
        return;
    }

    const formData = new FormData(form);
    fetch('/submit/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });

    fetch("http://192.168.4.1:80/", {
            method: "POST",
            headers: {
                "Content-Type": "text/plain"
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log("Success:", data);
            alert("Connection success, Please reconnect to your home network.")
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Connection failure, Please double check your WiFi credentials.");
        });
});