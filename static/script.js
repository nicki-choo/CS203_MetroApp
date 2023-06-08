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

// Function to show flash message
function showFlashMessage(message) {
  // Create a flash message element
  var flashMessage = document.createElement('div');
  flashMessage.className = 'flash-message';
  flashMessage.textContent = message;

  // Append the flash message to the document body
  document.body.appendChild(flashMessage);

  // Set timeout to hide the flash message after 3 seconds
  setTimeout(function() {
    flashMessage.style.display = 'none';
  }, 3000);
}

// Get the flash message from the HTML element
var flashMessage = document.getElementById('flash-message');

// Check if a flash message exists
if (flashMessage) {
  // Get the message content
  var message = flashMessage.textContent.trim();

  // Show the flash message
  showFlashMessage(message);
}

