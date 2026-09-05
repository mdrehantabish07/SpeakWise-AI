// ==================================================
// SPEAKWISE AI - COMPLETE FRONTEND
// ==================================================

const API_URL = "https://speakwise-ai-1.onrender.com";


// ==================================================
// PAGE INFORMATION
// ==================================================

const pageInformation = {

    conversation: {
        title: "Conversation",
        subtitle: "Practice English naturally with SpeakWise AI"
    },

    learning: {
        title: "Learning Assistant",
        subtitle: "Improve your grammar, vocabulary and fluency"
    },

    voice: {
        title: "Voice Practice",
        subtitle: "Practice speaking naturally with your AI partner"
    },

    progress: {
        title: "Progress",
        subtitle: "Track your English learning journey"
    }

};


// ==================================================
// SPEECH RECOGNITION
// ==================================================

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


// ==================================================
// STATE
// ==================================================

let conversationRecognition = null;
let conversationListening = false;

let learningRecognition = null;
let learningListening = false;
let learningFinalTranscript = "";

let voiceRecognition = null;
let voiceListening = false;
let voiceStarting = false;

let aiSpeaking = false;

// Continuous voice conversation
let voiceConversationActive = false;
let voiceConversationHistory = [];
let selectedVoice = null;


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

        activeButton.classList.add(
            "active"
        );

    }


    const info =
        pageInformation[sectionId];


    if (info) {

        const title =
            document.getElementById(
                "pageTitle"
            );

        const subtitle =
            document.getElementById(
                "pageSubtitle"
            );


        if (title) {

            title.textContent =
                info.title;

        }


        if (subtitle) {

            subtitle.textContent =
                info.subtitle;

        }

    }


    if (sectionId === "progress") {

        loadProgress();

    }

}


// ==================================================
// PROFILE
// ==================================================

function openProfile() {

    const modal =
        document.getElementById(
            "profileModal"
        );


    if (!modal) {

        return;

    }


    modal.classList.remove(
        "hidden"
    );


    updateProfileStats();

}


function closeProfile() {

    const modal =
        document.getElementById(
            "profileModal"
        );


    if (!modal) {

        return;

    }


    modal.classList.add(
        "hidden"
    );

}


function updateProfileStats() {

    const sessions =
        document.getElementById(
            "profileSessions"
        );


    if (sessions) {

        sessions.textContent =
            getHistory().length;

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
        document.getElementById(
            "chatInput"
        );


    if (!input) {

        return;

    }


    const message =
        input.value.trim();


    if (!message) {

        return;

    }


    addUserMessage(
        message
    );


    input.value = "";


    const thinking =
        addBotMessage(
            "Thinking... 🤔"
        );


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
                        message: message
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


        addBotMessage(
            answer
        );


        speakText(
            answer
        );

    }

    catch (error) {

        if (thinking) {

            thinking.remove();

        }


        addBotMessage(
            "❌ Unable to connect to SpeakWise backend."
        );


        console.error(
            "Chat error:",
            error
        );

    }

}


// ==================================================
// ADD USER MESSAGE
// ==================================================

function addUserMessage(message) {

    const chatBox =
        document.getElementById(
            "chatBox"
        );


    if (!chatBox) {

        return;

    }


    const div =
        document.createElement(
            "div"
        );


    div.className =
        "user-message";


    div.textContent =
        message;


    chatBox.appendChild(
        div
    );


    chatBox.scrollTop =
        chatBox.scrollHeight;

}


// ==================================================
// ADD BOT MESSAGE
// ==================================================

function addBotMessage(message) {

    const chatBox =
        document.getElementById(
            "chatBox"
        );


    if (!chatBox) {

        return null;

    }


    const div =
        document.createElement(
            "div"
        );


    div.className =
        "bot-message";


    const name =
        document.createElement(
            "div"
        );


    name.className =
        "message-name";


    name.textContent =
        "🤖 SpeakWise";


    const text =
        document.createElement(
            "div"
        );


    text.textContent =
        message;


    div.appendChild(
        name
    );


    div.appendChild(
        text
    );


    chatBox.appendChild(
        div
    );


    chatBox.scrollTop =
        chatBox.scrollHeight;


    return div;

}


// ==================================================
// TEXT TO SPEECH
// ==================================================

function speakText(text) {

    if (
        !("speechSynthesis" in window)
    ) {

        return;

    }


    window.speechSynthesis.cancel();


    const speech =
        new SpeechSynthesisUtterance(
            text
        );


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
// LEARNING ASSISTANT
// ==================================================

async function analyzeSentence() {

    const input =
        document.getElementById(
            "sentenceInput"
        );


    if (!input) {

        return;

    }


    const sentence =
        input.value.trim();


    if (!sentence) {

        alert(
            "Please enter or speak a sentence."
        );

        return;

    }


    const loading =
        document.getElementById(
            "learningLoading"
        );


    const result =
        document.getElementById(
            "result"
        );


    if (loading) {

        loading.classList.remove(
            "hidden"
        );

    }


    if (result) {

        result.classList.add(
            "hidden"
        );

    }


    try {

        console.log(
            "Analyzing:",
            sentence
        );


        const response =
            await fetch(
                `${API_URL}/analyze`,
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        sentence: sentence
                    })

                }
            );


        const data =
            await response.json();


        console.log(
            "Analysis response:",
            data
        );


        if (!response.ok) {

            throw new Error(
                data.message ||
                data.error ||
                "Analysis failed"
            );

        }


        displayAnalysis(
            data
        );


        saveLearningHistory(
            sentence,
            data
        );


        if (loading) {

            loading.classList.add(
                "hidden"
            );

        }


        if (result) {

            result.classList.remove(
                "hidden"
            );

        }


        loadProgress();

    }

    catch (error) {

        if (loading) {

            loading.classList.add(
                "hidden"
            );

        }


        console.error(
            "Analysis error:",
            error
        );


        setHTML(
            "grammarResult",
            `
                <p>
                    ❌ Unable to analyze sentence.
                </p>
            `
        );


        if (result) {

            result.classList.remove(
                "hidden"
            );

        }

    }

}


// ==================================================
// DISPLAY ANALYSIS
// ==================================================

function displayAnalysis(data) {

    const analysis =
        data.analysis || data;


    // ==================================================
    // GRAMMAR
    // ==================================================

    const grammar =
        analysis.grammar || {};


    const errors =
        Array.isArray(
            grammar.errors
        )
            ? grammar.errors
            : [];


    const suggestions =
        Array.isArray(
            grammar.suggestions
        )
            ? grammar.suggestions
            : [];


    const corrections =
        Array.isArray(
            grammar.corrections
        )
            ? grammar.corrections
            : [];


    let grammarHTML =
        "";


    if (errors.length) {

        grammarHTML += `
            <p>
                <strong>⚠️ Errors:</strong>
            </p>
        `;


        errors.forEach(
            error => {

                grammarHTML += `
                    <div class="error-item">
                        ${escapeHTML(error)}
                    </div>
                `;

            }
        );

    }


    if (suggestions.length) {

        grammarHTML += `
            <p>
                <strong>💡 Suggestions:</strong>
            </p>
        `;


        suggestions.forEach(
            suggestion => {

                grammarHTML += `
                    <div class="suggestion-item">
                        ${escapeHTML(
                            suggestion
                        )}
                    </div>
                `;

            }
        );

    }


    if (corrections.length) {

        grammarHTML += `
            <br>
            <strong>
                ✏️ Corrections:
            </strong>
        `;


        corrections.forEach(
            correction => {

                grammarHTML += `
                    <div class="correction-item">
                        → ${escapeHTML(
                            correction
                        )}
                    </div>
                `;

            }
        );

    }


    if (!grammarHTML) {

        grammarHTML = `
            <p>
                ✅ No basic grammar problems detected.
            </p>
        `;

    }


    setHTML(
        "grammarResult",
        grammarHTML
    );


    // ==================================================
    // VOCABULARY
    // ==================================================

    const vocabulary =
        analysis.vocabulary || {};


    const suspicious =
        Array.isArray(
            vocabulary.suspicious_words
        )
            ? vocabulary.suspicious_words
            : [];


    if (suspicious.length) {

        setHTML(
            "vocabularyResult",
            suspicious
                .map(
                    word => `
                        <p>
                            ⚠️ ${escapeHTML(
                                word
                            )}
                        </p>
                    `
                )
                .join("")
        );

    }

    else {

        setHTML(
            "vocabularyResult",
            `
                <p>
                    ✅ No suspicious words detected.
                </p>
            `
        );

    }


    // ==================================================
    // FEATURES
    // ==================================================

    const features =
        analysis.features || {};


    setHTML(
        "featuresResult",
        `
            <p>
                <strong>Word count:</strong>
                ${features.word_count ?? 0}
            </p>

            <p>
                <strong>Unique words:</strong>
                ${features.unique_words ?? 0}
            </p>

            <p>
                <strong>Word diversity:</strong>
                ${features.word_diversity ?? 0}
            </p>

            <p>
                <strong>Average word length:</strong>
                ${features.avg_word_length ?? 0}
            </p>

            <p>
                <strong>Repeated word ratio:</strong>
                ${features.repeated_word_ratio ?? 0}
            </p>

            <p>
                <strong>Long word ratio:</strong>
                ${features.long_word_ratio ?? 0}
            </p>
        `
    );


    // ==================================================
    // FLUENCY
    // ==================================================

    const score =
        analysis.fluency_score ?? 0;


    setHTML(
        "fluencyResult",
        `
            <div class="score">
                ${score}/100
            </div>
        `
    );

}


// ==================================================
// LEARNING VOICE
// ==================================================

function createLearningRecognition() {

    if (!SpeechRecognition) {

        alert(
            "Speech recognition is not supported. Please use Google Chrome."
        );

        return null;

    }


    const recognition =
        new SpeechRecognition();


    recognition.continuous =
        false;


    recognition.interimResults =
        true;


    recognition.lang =
        "en-IN";


    recognition.onstart =
        function() {

            learningListening =
                true;


            const status =
                document.getElementById(
                    "learningVoiceStatus"
                );


            if (status) {

                status.textContent =
                    "🎤 Listening...";

            }

        };


    recognition.onresult =
        function(event) {

            let finalTranscript =
                "";


            let interimTranscript =
                "";


            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                const transcript =
                    event.results[i][0].transcript;


                if (
                    event.results[i].isFinal
                ) {

                    finalTranscript +=
                        transcript;

                }

                else {

                    interimTranscript +=
                        transcript;

                }

            }


            if (finalTranscript) {

                learningFinalTranscript =
                    finalTranscript.trim();

            }


            const input =
                document.getElementById(
                    "sentenceInput"
                );


            if (input) {

                input.value =
                    (
                        learningFinalTranscript ||
                        interimTranscript
                    ).trim();

            }

        };


    recognition.onerror =
        function(error) {

            console.error(
                "Learning recognition error:",
                error
            );


            learningListening =
                false;


            const status =
                document.getElementById(
                    "learningVoiceStatus"
                );


            if (status) {

                status.textContent =
                    "❌ Voice recognition error.";

            }

        };


    recognition.onend =
        function() {

            learningListening =
                false;


            const status =
                document.getElementById(
                    "learningVoiceStatus"
                );


            if (status) {

                status.textContent =
                    "🎤 Ready";

            }

        };


    return recognition;

}


function toggleLearningVoice() {

    if (!SpeechRecognition) {

        alert(
            "Please use Google Chrome for voice recognition."
        );

        return;

    }


    if (
        learningListening &&
        learningRecognition
    ) {

        learningRecognition.stop();

        return;

    }


    learningFinalTranscript =
        "";


    learningRecognition =
        createLearningRecognition();


    if (learningRecognition) {

        try {

            learningRecognition.start();

        }

        catch (error) {

            console.error(
                error
            );

        }

    }

}


// ==================================================
// VOICE PRACTICE
// ==================================================

function detectVoiceLanguage(text) {

    const hindiWords = [
        "hai",
        "ho",
        "haan",
        "nahi",
        "nahin",
        "mujhe",
        "tum",
        "aap",
        "kaise",
        "kaisa",
        "kya",
        "kyun",
        "kyunki",
        "mera",
        "meri",
        "mere",
        "hamara",
        "hum",
        "main",
        "mein",
        "se",
        "ko",
        "ke",
        "ki",
        "ka",
        "me",
        "acha",
        "achha",
        "bahut",
        "bhi",
        "abhi",
        "kal",
        "aaj",
        "chahiye",
        "karna",
        "karo",
        "karta",
        "karte",
        "raha",
        "rahi",
        "hoon",
        "hun",
        "tha",
        "thi",
        "the",
        "gaya",
        "gayi",
        "jao",
        "jaana",
        "bolo",
        "baat",
        "samajh",
        "samjha",
        "sahi",
        "galat"
    ];


    const words =
        text
            .toLowerCase()
            .replace(
                /[^\w\s]/g,
                ""
            )
            .split(
                /\s+/
            );


    const hindiCount =
        words.filter(
            word =>
                hindiWords.includes(
                    word
                )
        ).length;


    if (
        hindiCount >= 2
    ) {

        return "hi";

    }


    return "en";

}


function getPreferredVoice(language) {

    if (
        !("speechSynthesis" in window)
    ) {

        return null;

    }


    const voices =
        window.speechSynthesis.getVoices();


    if (!voices.length) {

        return null;

    }


    if (language === "hi") {

        return (
            voices.find(
                voice =>
                    voice.lang
                        .toLowerCase()
                        .startsWith(
                            "hi"
                        )
            ) ||

            voices.find(
                voice =>
                    voice.name
                        .toLowerCase()
                        .includes(
                            "hindi"
                        )
            ) ||

            null
        );

    }


    return (
        voices.find(
            voice =>
                voice.lang
                    .toLowerCase()
                    .startsWith(
                        "en-in"
                    )
        ) ||

        voices.find(
            voice =>
                voice.lang
                    .toLowerCase()
                    .startsWith(
                        "en"
                    )
        ) ||

        null
    );

}


function createVoiceRecognition() {

    if (!SpeechRecognition) {

        alert(
            "Please use Google Chrome for voice recognition."
        );

        return null;

    }


    const recognition =
        new SpeechRecognition();


    recognition.continuous =
        false;


    recognition.interimResults =
        true;


    recognition.lang =
        "en-IN";


    recognition.onstart =
        function() {

            voiceListening =
                true;

            voiceStarting =
                false;


            const status =
                document.getElementById(
                    "voiceStatus"
                );


            if (status) {

                status.textContent =
                    "🎤 Listening...";

            }


            updateVoiceButton();

        };


    recognition.onresult =
        function(event) {

            let finalTranscript =
                "";


            let interimTranscript =
                "";


            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                const transcript =
                    event.results[i][0].transcript;


                if (
                    event.results[i].isFinal
                ) {

                    finalTranscript +=
                        transcript;

                }

                else {

                    interimTranscript +=
                        transcript;

                }

            }


            const transcriptElement =
                document.getElementById(
                    "voiceTranscript"
                );


            if (transcriptElement) {

                transcriptElement.innerHTML =
                    `
                        <strong>You:</strong>
                        ${escapeHTML(
                            finalTranscript ||
                            interimTranscript
                        )}
                    `;

            }


            if (finalTranscript.trim()) {

                voiceListening =
                    false;


                recognition.stop();


                sendVoiceMessage(
                    finalTranscript.trim()
                );

            }

        };


    recognition.onerror =
        function(error) {

            console.error(
                "Voice recognition error:",
                error
            );


            voiceListening =
                false;

            voiceStarting =
                false;


            updateVoiceButton();


            const status =
                document.getElementById(
                    "voiceStatus"
                );


            if (status) {

                status.textContent =
                    "❌ Voice recognition error.";

            }


            if (
                voiceConversationActive &&
                !aiSpeaking
            ) {

                setTimeout(
                    startVoiceListening,
                    1000
                );

            }

        };


    recognition.onend =
        function() {

            voiceListening =
                false;

            voiceStarting =
                false;


            updateVoiceButton();


            // Do NOT restart here while AI is
            // thinking or speaking.
            if (
                voiceConversationActive &&
                !aiSpeaking
            ) {

                setTimeout(
                    function() {

                        if (
                            voiceConversationActive &&
                            !voiceListening &&
                            !aiSpeaking
                        ) {

                            startVoiceListening();

                        }

                    },
                    500
                );

            }

        };


    return recognition;

}


function startVoiceListening() {

    if (!SpeechRecognition) {

        return;

    }


    if (
        !voiceConversationActive
    ) {

        return;

    }


    if (
        voiceListening ||
        voiceStarting ||
        aiSpeaking
    ) {

        return;

    }


    voiceStarting =
        true;


    if (!voiceRecognition) {

        voiceRecognition =
            createVoiceRecognition();

    }


    if (!voiceRecognition) {

        voiceStarting =
            false;

        return;

    }


    try {

        voiceRecognition.start();

    }

    catch (error) {

        voiceStarting =
            false;

        console.log(
            "Recognition start:",
            error
        );

    }

}


function stopVoiceListening() {

    voiceConversationActive =
        false;


    voiceStarting =
        false;


    if (
        voiceRecognition &&
        voiceListening
    ) {

        try {

            voiceRecognition.stop();

        }

        catch (error) {

            console.log(
                error
            );

        }

    }


    voiceListening =
        false;


    updateVoiceButton();

}


function toggleVoicePractice() {

    if (!SpeechRecognition) {

        alert(
            "Please use Google Chrome for voice recognition."
        );

        return;

    }


    if (
        voiceConversationActive
    ) {

        stopVoiceListening();


        const status =
            document.getElementById(
                "voiceStatus"
            );


        if (status) {

            status.textContent =
                "Voice conversation stopped.";

        }


        return;

    }


    voiceConversationActive =
        true;


    voiceConversationHistory =
        [];


    const transcript =
        document.getElementById(
            "voiceTranscript"
        );


    if (transcript) {

        transcript.innerHTML =
            `
                <strong>
                    🤖 SpeakWise:
                </strong>
                Hi! I'm SpeakWise. Let's practice English together.
                <br><br>
                🎤 I'm listening...
            `;

    }


    const status =
        document.getElementById(
            "voiceStatus"
        );


    if (status) {

        status.textContent =
            "🎤 Listening...";

    }


    updateVoiceButton();


    startVoiceListening();

}


function updateVoiceButton() {

    const button =
        document.getElementById(
            "voiceStartButton"
        );


    if (!button) {

        return;

    }


    if (
        voiceConversationActive
    ) {

        button.textContent =
            "⏹ Stop Speaking";

    }

    else {

        button.textContent =
            "🎤 Start Speaking";

    }

}


function addVoiceHistory(
    role,
    content
) {

    voiceConversationHistory.push({

        role:
            role,

        content:
            content

    });


    voiceConversationHistory =
        voiceConversationHistory.slice(
            -12
        );

}


async function sendVoiceMessage(text) {

    if (!text) {

        return;

    }


    addVoiceHistory(
        "user",
        text
    );


    const status =
        document.getElementById(
            "voiceStatus"
        );


    if (status) {

        status.textContent =
            "🤔 SpeakWise is thinking...";

    }


    const transcript =
        document.getElementById(
            "voiceTranscript"
        );


    if (transcript) {

        transcript.innerHTML =
            `
                <strong>You:</strong>
                ${escapeHTML(text)}
                <br><br>
                <span>
                    🤔 SpeakWise is thinking...
                </span>
            `;

    }


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

                        message:
                            text,

                        history:
                            voiceConversationHistory.slice(
                                0,
                                -1
                            ),

                        language:
                            "auto"

                    })

                }
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            data.success === false
        ) {

            throw new Error(
                data.error ||
                data.message ||
                "Backend error"
            );

        }


        const answer =
            data.response ||
            "Sorry, I didn't catch that. Please say it again.";


        addVoiceHistory(
            "assistant",
            answer
        );


        if (transcript) {

            transcript.innerHTML =
                `
                    <strong>You:</strong>
                    ${escapeHTML(text)}

                    <br><br>

                    <strong>
                        🤖 SpeakWise:
                    </strong>

                    ${escapeHTML(answer)}
                `;

        }


        speakVoiceResponse(
            answer
        );

    }

    catch (error) {

        console.error(
            "Voice AI error:",
            error
        );


        if (status) {

            status.textContent =
                "❌ Unable to connect to SpeakWise.";

        }


        if (
            voiceConversationActive
        ) {

            setTimeout(
                startVoiceListening,
                1200
            );

        }

    }

}


// ==================================================
// AI SPEAKING
// ==================================================

function speakVoiceResponse(text) {

    if (
        !("speechSynthesis" in window)
    ) {

        aiSpeaking =
            false;


        updateVoiceButton();


        if (
            voiceConversationActive
        ) {

            setTimeout(
                startVoiceListening,
                500
            );

        }


        return;

    }


    // Never listen while AI is speaking.
    stopVoiceRecognitionOnly();


    window.speechSynthesis.cancel();


    aiSpeaking =
        true;


    updateVoiceButton();


    const status =
        document.getElementById(
            "voiceStatus"
        );


    if (status) {

        status.textContent =
            "🔊 SpeakWise is speaking...";

    }


    const language =
        detectVoiceLanguage(
            text
        );


    const speech =
        new SpeechSynthesisUtterance(
            text
        );


    speech.lang =
        language === "hi"
            ? "hi-IN"
            : "en-IN";


    selectedVoice =
        getPreferredVoice(
            language
        );


    if (selectedVoice) {

        speech.voice =
            selectedVoice;

    }


    speech.rate =
        0.88;


    speech.pitch =
        1.02;


    speech.volume =
        1;


    speech.onend =
        function() {

            aiSpeaking =
                false;


            updateVoiceButton();


            if (
                voiceConversationActive
            ) {

                if (status) {

                    status.textContent =
                        "🎤 Listening...";

                }


                setTimeout(
                    startVoiceListening,
                    500
                );

            }

            else {

                if (status) {

                    status.textContent =
                        "Voice conversation stopped.";

                }

            }

        };


    speech.onerror =
        function(error) {

            console.log(
                "Speech error:",
                error
            );


            aiSpeaking =
                false;


            updateVoiceButton();


            if (
                voiceConversationActive
            ) {

                setTimeout(
                    startVoiceListening,
                    700
                );

            }

        };


    window.speechSynthesis.speak(
        speech
    );

}


// ==================================================
// VOICE RECOGNITION STOP HELPER
// ==================================================

function stopVoiceRecognitionOnly() {

    if (
        voiceRecognition &&
        voiceListening
    ) {

        try {

            voiceRecognition.stop();

        }

        catch (error) {

            console.log(
                error
            );

        }

    }


    voiceListening =
        false;


    voiceStarting =
        false;

}


// ==================================================
// HISTORY
// ==================================================

function getHistory() {

    try {

        return JSON.parse(
            localStorage.getItem(
                "speakwise_history"
            )
        ) || [];

    }

    catch (error) {

        return [];

    }

}


function saveLearningHistory(
    sentence,
    data
) {

    const analysis =
        data.analysis || {};


    const history =
        getHistory();


    history.unshift({

        sentence:
            sentence,

        fluency:
            analysis.fluency_score ??
            0,

        grammarErrors:
            analysis.grammar?.error_count ??
            0,

        date:
            new Date()
                .toLocaleString()

    });


    localStorage.setItem(
        "speakwise_history",

        JSON.stringify(
            history.slice(
                0,
                50
            )
        )
    );

}


// ==================================================
// PROGRESS
// ==================================================

function loadProgress() {

    const history =
        getHistory();


    const count =
        history.length;


    setText(
        "sentencesPracticed",
        count
    );


    setText(
        "profileSessions",
        count
    );


    if (!count) {

        setText(
            "averageFluency",
            "0"
        );


        setText(
            "grammarScore",
            "0%"
        );


        renderHistory(
            []
        );


        return;

    }


    const totalFluency =
        history.reduce(
            (
                total,
                item
            ) => {

                return total +
                    Number(
                        item.fluency ||
                        0
                    );

            },
            0
        );


    const averageFluency =
        Math.round(
            totalFluency /
            count
        );


    setText(
        "averageFluency",
        averageFluency
    );


    const correct =
        history.filter(
            item =>
                Number(
                    item.grammarErrors ||
                    0
                ) === 0
        ).length;


    const grammarPercentage =
        Math.round(
            (
                correct /
                count
            ) * 100
        );


    setText(
        "grammarScore",
        `${grammarPercentage}%`
    );


    renderHistory(
        history.slice(
            0,
            10
        )
    );

}


// ==================================================
// HISTORY DISPLAY
// ==================================================

function renderHistory(
    history
) {

    const list =
        document.getElementById(
            "historyList"
        );


    if (!list) {

        return;

    }


    if (!history.length) {

        list.innerHTML = `

            <div class="empty-history">

                No practice history yet.

                <br><br>

                Start analyzing sentences to see
                your progress here.

            </div>

        `;


        return;

    }


    list.innerHTML =
        "";


    history.forEach(
        item => {

            const div =
                document.createElement(
                    "div"
                );


            div.className =
                "history-item";


            const sentence =
                document.createElement(
                    "strong"
                );


            sentence.textContent =
                item.sentence;


            const score =
                document.createElement(
                    "span"
                );


            score.textContent =
                `Fluency: ${item.fluency}/100`;


            const date =
                document.createElement(
                    "small"
                );


            date.textContent =
                item.date;


            div.appendChild(
                sentence
            );


            div.appendChild(
                score
            );


            div.appendChild(
                date
            );


            list.appendChild(
                div
            );

        }
    );

}


// ==================================================
// HELPERS
// ==================================================

function setHTML(
    elementId,
    html
) {

    const element =
        document.getElementById(
            elementId
        );


    if (element) {

        element.innerHTML =
            html;

    }

}


function setText(
    elementId,
    text
) {

    const element =
        document.getElementById(
            elementId
        );


    if (element) {

        element.textContent =
            text;

    }

}


function escapeHTML(
    text
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(text);


    return div.innerHTML;

}


// ==================================================
// VOICES READY
// ==================================================

if (
    "speechSynthesis" in window
) {

    window.speechSynthesis.onvoiceschanged =
        function() {

            window.speechSynthesis
                .getVoices();

        };

}


// ==================================================
// START APP
// ==================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        showSection(
            "conversation"
        );


        loadProgress();


        console.log(
            "✅ SpeakWise AI frontend loaded"
        );

    }
);