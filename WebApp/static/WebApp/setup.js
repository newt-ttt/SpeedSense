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
});