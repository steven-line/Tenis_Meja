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


document.addEventListener("DOMContentLoaded", () => {
    const addMoreButton = document.getElementById("add-more");
    const uploadContainer = document.getElementById("upload-container");

    if (!addMoreButton) {
        console.error("Elemen #add-more tidak ditemukan di DOM.");
    }
    if (!uploadContainer) {
        console.error("Elemen #upload-container tidak ditemukan di DOM.");
    }

    if (addMoreButton && uploadContainer) {
        addMoreButton.addEventListener("click", () => {
            const newUploadItem = document.createElement("div");
            newUploadItem.classList.add("upload-item");

            newUploadItem.innerHTML = `
                <label for="image-title">Judul Gambar:</label>
                <input type="text" name="image_title[]" required>

                <label for="image-description">Deskripsi Gambar:</label>
                <textarea name="description[]" required></textarea>

                <label for="image-file">Pilih Gambar:</label>
                <input type="file" name="image_file[]" accept="image/*" required>

                <button type="button" class="btn-remove">Hapus</button>
            `;

            const removeButton = newUploadItem.querySelector(".btn-remove");
            removeButton.addEventListener("click", () => {
                uploadContainer.removeChild(newUploadItem);
            });

            uploadContainer.appendChild(newUploadItem);
        });
    }
});

