// ==================================================
// API
// ==================================================

const API_URL = "https://speakwise-ai-1.onrender.com";


// ==================================================
// NAVIGATION
// ==================================================

function showSection(sectionId) {

    document
        .querySelectorAll(".page-section")
        .forEach(section => {
            section.classList.remove("active-section");
        });

    const section =
        document.getElementById(sectionId);

    if (!section) {
        console.log(
            "Section not found:",
            sectionId
        );
        return;
    }

    section.classList.add(
        "active-section"
    );

    document
        .querySelectorAll(".nav-item")
        .forEach(button => {
            button.classList.remove("active");
        });

    const activeButton =
        document.querySelector(
            `.nav-item[data-section="${sectionId}"]`
        );

    if (activeButton) {
        activeButton.classList.add("active");
    }
}


// ==================================================
// CHAT
// ==================================================

function handleChatKey(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();
    }
}


async function sendMessage() {

    const input =
        document.getElementById("chatInput");

    if (!input) {
        return;
    }

    const message =
        input.value.trim();

    if (!message) {
        return;
    }

    addUserMessage(message);

    input.value = "";

    const thinking =
        addBotMessage("Thinking... 🤔");

    try {

        const response =
            await fetch(
                `${API_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message,
                        language: "english",
                        history: []
                    })
                }
            );

        const data =
            await response.json();

        if (thinking) {
            thinking.remove();
        }

        if (!response.ok) {

            throw new Error(
                data.error ||
                data.message ||
                "Server error"
            );
        }

        const answer =
            data.response ||
            "Sorry, I couldn't generate a response.";

        addBotMessage(answer);

        speakText(answer);

    }
    catch (error) {

        if (thinking) {
            thinking.remove();
        }

        console.error(
            "Chat error:",
            error
        );

        addBotMessage(
            "❌ Unable to connect to SpeakWise backend."
        );
    }
}


// ==================================================
// ADD USER MESSAGE
// ==================================================

function addUserMessage(message) {

    const chatBox =
        document.getElementById("chatBox");

    if (!chatBox) {
        return;
    }

    const div =
        document.createElement("div");

    div.className =
        "user-message";

    div.textContent =
        message;

    chatBox.appendChild(div);

    chatBox.scrollTop =
        chatBox.scrollHeight;
}


// ==================================================
// ADD BOT MESSAGE
// ==================================================

function addBotMessage(message) {

    const chatBox =
        document.getElementById("chatBox");

    if (!chatBox) {
        return null;
    }

    const div =
        document.createElement("div");

    div.className =
        "bot-message";

    const name =
        document.createElement("div");

    name.className =
        "message-name";

    name.textContent =
        "🤖 SpeakWise";

    const text =
        document.createElement("div");

    text.textContent =
        message;

    div.appendChild(name);

    div.appendChild(text);

    chatBox.appendChild(div);

    chatBox.scrollTop =
        chatBox.scrollHeight;

    return div;
}


// ==================================================
// TEXT TO SPEECH
// ==================================================

function speakText(text) {

    if (!("speechSynthesis" in window)) {
        return;
    }

    window.speechSynthesis.cancel();

    const speech =
        new SpeechSynthesisUtterance(text);

    speech.lang =
        "en-IN";

    speech.rate =
        0.95;

    speech.pitch =
        1;

    window.speechSynthesis.speak(
        speech
    );
}


// ==================================================
// START APP
// ==================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        showSection("conversation");

        console.log(
            "✅ SpeakWise AI frontend loaded"
        );
    }
);