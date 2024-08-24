function submitForm(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                window.location.href = '/'; // Redirect to home or another page after successful sign-in/sign-up
            }
        })
        .catch(error => console.error('Error:', error));
}