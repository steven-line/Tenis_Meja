// Forum: Add messages dynamically
function postMessage() {
    const input = document.getElementById("forumInput").value;
    const messages = document.getElementById("forumMessages");

    if (input.trim()) {
        const newMessage = document.createElement("p");
        newMessage.textContent = input;
        messages.appendChild(newMessage);
        document.getElementById("forumInput").value = ""; // Clear input
    } else {
        alert("Please write something before posting.");
    }
}

// Login: Simple validation
function loginUser() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if (username === "admin" && password === "1234") {
        alert("Login successful!");
        return true;
    } else {
        alert("Invalid username or password.");
        return false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector(".schedule-table");
    if (table) {
        table.classList.add("fade-in");
    }
});

