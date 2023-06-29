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

function checkPasswordsMatch() {
    var input = document.getElementById('register-password-confirm');
    if (input.value != document.getElementById('register-password').value) {
        input.setCustomValidity('Passwords Must Be Matching');
    } else {
        // Here the inputs match, so reset the error message
        input.setCustomValidity('');
    }
}

function hideFlashMessage() {
  let flashMessage = document.getElementById('flash-message');
  if (flashMessage) {
    flashMessage.classList.add('hide');
    setTimeout(function() {
      flashMessage.style.display = 'none';
    }, 3000); // Change the duration (in milliseconds) as needed
  }
}

// Call the hideFlashMessage function when the page loads
window.addEventListener('DOMContentLoaded', hideFlashMessage);

