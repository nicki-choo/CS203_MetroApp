function updateClock() {
  var now = new Date();
  document.getElementById("clock").textContent = now.toLocaleTimeString();
}

// Call the updateClock function every second
setInterval(updateClock, 1000);

// Define a function to handle login button click
function handleLogin() {
  // Redirect the user to the home page
  window.location.href = "index.html";
}

// Add an event listener to the login button
document.getElementById("loginButton").addEventListener("click", handleLogin);

(() => {
  'use strict'

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }

      form.classList.add('was-validated')
    }, false)
  })
})()

setTimeout(function() {
    var flashMessage = document.getElementById('flash-message');
    if (flashMessage) {
      flashMessage.remove();
    }
  }, 5000);

