// ============================================================
// SPEAKWISE AI - CONTINUOUS VOICE CONVERSATION
// Hindi + Hinglish + English
// Female AI Voice
// Automatic Turn Taking
// ============================================================


// ============================================================
// API
// ============================================================
const API_URL = "";
// ============================================================
// SPEECH RECOGNITION
// ============================================================

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


// ============================================================
// STATE
// ============================================================

let voiceRecognition = null;

let voiceListening = false;

let voiceStarting = false;

let aiSpeaking = false;

let aiThinking = false;

let conversationActive = false;

let currentTranscript = "";

let conversationHistory = [];


// ============================================================
// LANGUAGE DETECTION
// ============================================================

function detectLanguage(text) {

    if (!text) {
        return "english";
    }


    // Hindi Devanagari
    const hindiScript = /[\u0900-\u097F]/;

    if (hindiScript.test(text)) {
        return "hindi";
    }


    const lower =
        text
            .toLowerCase()
            .trim();


    const hindiWords = [

        "main",
        "mein",
        "mujhe",
        "mujhse",

        "mera",
        "meri",
        "mere",

        "aap",
        "aapko",
        "aapka",
        "aapki",

        "tum",
        "tumhe",
        "tumhara",
        "tumhari",

        "kya",
        "kaise",
        "kaisa",

        "kyun",
        "kyu",

        "hai",
        "ho",
        "haan",

        "nahi",
        "nahin",

        "kar",
        "karo",
        "karna",
        "karni",
        "karne",

        "karta",
        "karti",
        "karte",

        "raha",
        "rahi",
        "rahe",

        "gaya",
        "gayi",
        "gaye",

        "jana",
        "jaana",
        "jao",

        "aana",
        "aao",

        "acha",
        "accha",
        "achha",

        "bahut",
        "bohot",

        "aaj",
        "kal",
        "abhi",

        "baat",
        "bolo",
        "bol",

        "suno",
        "sun",

        "samajh",
        "samajhna",

        "chahiye",

        "pata",
        "lagta",

        "sakta",
        "sakti",
        "sakte",

        "aur",
        "lekin",
        "kyunki",

        "ghar",
        "college",

        "khana",
        "peena",

        "kahan",
        "kab",

        "yaar",
        "yar",

        "theek",
        "thik",

        "mujh",
        "mujhe",

        "ka",
        "ki",
        "ke",

        "se",
        "ko",

        "par",

        "apna",
        "apni",
        "apne",

        "hum",
        "ham",

        "hamara",
        "humara",

        "hamari",
        "humari",

        "kuch",
        "koi",
        "kaise",

        "kyon",
        "kyunki",

        "ab",
        "phir",
        "fir",

        "toh",
        "to",

        "bhi",
        "nahi",

        "mujhko",
        "aapko",

        "dost",
        "bhai",

        "acchi",
        "achhi",

        "karunga",
        "karungi",

        "jaunga",
        "jaungi",

        "aunga",
        "aungi"

    ];


    const words =
        lower
            .replace(
                /[.,!?;:]/g,
                " "
            )
            .split(/\s+/)
            .filter(Boolean);


    let hindiCount = 0;


    words.forEach(
        function(word) {

            if (
                hindiWords.includes(word)
            ) {

                hindiCount++;

            }

        }
    );


    /*
     * If Hindi words are present,
     * classify as Hinglish.
     */

    if (hindiCount >= 1) {

        return "hinglish";

    }


    return "english";
}


// ============================================================
// CREATE SPEECH RECOGNITION
// ============================================================

function createVoicePracticeRecognition() {

    if (!SpeechRecognition) {

        alert(
            "Google Chrome speech recognition is required."
        );

        return null;
    }


    const recognition =
        new SpeechRecognition();


    /*
     * One user turn at a time.
     * After AI finishes speaking,
     * microphone starts again automatically.
     */

    recognition.continuous = false;

    recognition.interimResults = true;


    /*
     * en-IN is used because it generally
     * works better for Indian English,
     * Hinglish and Roman Hindi.
     */

    recognition.lang = "en-IN";


    // ========================================================
    // ON START
    // ========================================================

    recognition.onstart =
        function() {

            voiceStarting = false;

            voiceListening = true;

            updateVoiceButton();

            setVoiceStatus(
                "🎤 Listening... Speak naturally."
            );

        };


    // ========================================================
    // ON RESULT
    // ========================================================

    recognition.onresult =
        function(event) {

            let finalText = "";

            let interimText = "";


            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                const result =
                    event.results[i];


                const text =
                    result[0].transcript;


                if (
                    result.isFinal
                ) {

                    finalText += text;

                }
                else {

                    interimText += text;

                }

            }


            const visibleText =
                (
                    finalText ||
                    interimText
                ).trim();


            // ------------------------------------------------
            // LIVE TRANSCRIPT
            // ------------------------------------------------

            const transcript =
                document.getElementById(
                    "voiceTranscript"
                );


            if (
                transcript &&
                visibleText
            ) {

                transcript.innerHTML =
                    "<strong>You:</strong> " +
                    escapeHTML(
                        visibleText
                    );

            }


            // ------------------------------------------------
            // FINAL SPEECH
            // ------------------------------------------------

            if (
                finalText.trim()
            ) {

                currentTranscript =
                    finalText.trim();


                voiceListening = false;


                try {

                    recognition.stop();

                }
                catch (error) {

                    console.log(
                        "Recognition stop:",
                        error
                    );

                }


                sendVoiceToAI(
                    currentTranscript
                );

            }

        };


    // ========================================================
    // ON END
    // ========================================================

    recognition.onend =
        function() {

            voiceStarting = false;

            voiceListening = false;

            updateVoiceButton();


            console.log(
                "🎤 Recognition ended."
            );


            /*
             * IMPORTANT:
             *
             * Do NOT restart microphone here.
             *
             * AI response will finish first.
             * speech.onend() will start microphone.
             */

        };


    // ========================================================
    // ON ERROR
    // ========================================================

    recognition.onerror =
        function(event) {

            voiceStarting = false;

            voiceListening = false;


            console.log(
                "Speech recognition error:",
                event.error
            );


            updateVoiceButton();


            // ------------------------------------------------
            // MICROPHONE PERMISSION
            // ------------------------------------------------

            if (
                event.error ===
                "not-allowed"
            ) {

                conversationActive = false;


                setVoiceStatus(
                    "❌ Microphone permission is required."
                );


                updateVoiceButton();


                return;

            }


            // ------------------------------------------------
            // NO SPEECH
            // ------------------------------------------------

            if (
                event.error ===
                "no-speech"
            ) {

                if (
                    conversationActive &&
                    !aiSpeaking &&
                    !aiThinking
                ) {

                    setTimeout(
                        function() {

                            startVoiceListening();

                        },
                        700
                    );

                }


                return;

            }


            // ------------------------------------------------
            // ABORTED
            // ------------------------------------------------

            if (
                event.error ===
                "aborted"
            ) {

                return;

            }


            // ------------------------------------------------
            // OTHER ERRORS
            // ------------------------------------------------

            if (
                conversationActive &&
                !aiSpeaking &&
                !aiThinking
            ) {

                setTimeout(
                    function() {

                        startVoiceListening();

                    },
                    1000
                );

            }

        };


    return recognition;
}


// ============================================================
// START USER LISTENING
// ============================================================

function startVoiceListening() {

    if (!conversationActive) {
        return;
    }


    if (aiSpeaking) {
        return;
    }


    if (aiThinking) {
        return;
    }


    if (
        voiceListening ||
        voiceStarting
    ) {
        return;
    }


    voiceRecognition =
        createVoicePracticeRecognition();


    if (!voiceRecognition) {
        return;
    }


    voiceStarting = true;

    voiceListening = true;

    currentTranscript = "";


    updateVoiceButton();


    setVoiceStatus(
        "🎤 Listening... Speak naturally."
    );


    try {

        voiceRecognition.start();

        console.log(
            "🎤 Microphone started."
        );

    }
    catch (error) {

        console.log(
            "Could not start microphone:",
            error
        );


        voiceStarting = false;

        voiceListening = false;


        updateVoiceButton();


        if (
            conversationActive
        ) {

            setTimeout(
                function() {

                    startVoiceListening();

                },
                1000
            );

        }

    }

}


// ============================================================
// STOP USER LISTENING
// ============================================================

function stopVoiceListening() {

    voiceListening = false;

    voiceStarting = false;


    if (
        voiceRecognition
    ) {

        try {

            voiceRecognition.stop();

        }
        catch (error) {

            console.log(
                "Recognition stop:",
                error
            );

        }

    }


    updateVoiceButton();
}


// ============================================================
// START / STOP CONVERSATION
// ============================================================

function toggleVoicePractice() {

    if (!SpeechRecognition) {

        alert(
            "Please use Google Chrome."
        );

        return;
    }


    if (
        conversationActive
    ) {

        stopVoiceConversation();

    }
    else {

        startVoiceConversation();

    }

}


// ============================================================
// START COMPLETE CONVERSATION
// ============================================================

function startVoiceConversation() {

    conversationActive = true;

    aiSpeaking = false;

    aiThinking = false;

    voiceListening = false;

    voiceStarting = false;


    conversationHistory = [];


    updateVoiceButton();


    setVoiceStatus(
        "🤖 SpeakWise is starting..."
    );


    // ========================================================
    // FEMALE AI GREETING
    // ========================================================

    const greeting =
        "Hello! 😊 How are you today?";


    conversationHistory.push({

        role:
            "assistant",

        content:
            greeting

    });


    showVoiceConversation(
        "",
        greeting
    );


    /*
     * AI speaks first.
     *
     * After AI speech ends,
     * microphone automatically starts.
     */

    speakVoiceResponse(
        greeting,
        "english"
    );

}


// ============================================================
// STOP COMPLETE CONVERSATION
// ============================================================

function stopVoiceConversation() {

    conversationActive = false;

    voiceListening = false;

    voiceStarting = false;

    aiSpeaking = false;

    aiThinking = false;


    conversationHistory = [];


    if (
        voiceRecognition
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


    voiceRecognition = null;


    if (
        "speechSynthesis" in window
    ) {

        window.speechSynthesis.cancel();

    }


    updateVoiceButton();


    setVoiceStatus(
        "Conversation stopped."
    );


    const transcript =
        document.getElementById(
            "voiceTranscript"
        );


    if (transcript) {

        transcript.innerHTML =
            "<strong>SpeakWise:</strong> Conversation ended.";

    }

}


// ============================================================
// UPDATE BUTTON
// ============================================================

function updateVoiceButton() {

    const button =
        document.getElementById(
            "voiceStartButton"
        );


    if (!button) {
        return;
    }


    if (aiSpeaking) {

        button.classList.remove(
            "listening"
        );


        button.textContent =
            "🔊 SpeakWise is Speaking...";


        return;

    }


    if (aiThinking) {

        button.classList.remove(
            "listening"
        );


        button.textContent =
            "🤔 Thinking...";


        return;

    }


    if (
        voiceListening ||
        voiceStarting
    ) {

        button.classList.add(
            "listening"
        );


        button.textContent =
            "🎤 Listening...";


        return;

    }


    if (
        conversationActive
    ) {

        button.classList.add(
            "listening"
        );


        button.textContent =
            "🛑 Stop Conversation";


        return;

    }


    button.classList.remove(
        "listening"
    );


    button.textContent =
        "🎤 Start Conversation";

}


// ============================================================
// SEND VOICE TO BACKEND
// ============================================================

async function sendVoiceToAI(text) {

    if (!text) {
        return;
    }


    if (!conversationActive) {
        return;
    }


    stopVoiceListening();


    aiThinking = true;


    updateVoiceButton();


    setVoiceStatus(
        "🤔 SpeakWise is thinking..."
    );


    showVoiceThinking(
        text
    );


    // ========================================================
    // DETECT LANGUAGE
    // ========================================================

    const userLanguage =
        detectLanguage(
            text
        );


    console.log(
        "Detected language:",
        userLanguage
    );


    // ========================================================
    // USER MESSAGE
    // ========================================================

    conversationHistory.push({

        role:
            "user",

        content:
            text

    });


    conversationHistory =
        conversationHistory.slice(
            -12
        );


    // ========================================================
    // BACKEND REQUEST
    // ========================================================

    try {

        const response =
            await fetch(
                `${API_URL}/chat`,
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            message:
                                text,

                            language:
                                userLanguage,

                            history:
                                conversationHistory

                        })

                }
            );


        const data =
            await response.json();


        if (
            !response.ok
        ) {

            throw new Error(

                data.error ||
                data.message ||
                "Backend error"

            );

        }


        if (
            data.success === false
        ) {

            throw new Error(

                data.error ||
                data.message ||
                "AI response failed"

            );

        }


        const answer =
            data.response ||
            "Sorry, I couldn't understand that.";


        // ====================================================
        // AI LANGUAGE
        // ====================================================

        const aiLanguage =
            data.language ||
            detectLanguage(
                answer
            );


        console.log(
            "AI language:",
            aiLanguage
        );


        // ====================================================
        // SAVE AI RESPONSE
        // ====================================================

        conversationHistory.push({

            role:
                "assistant",

            content:
                answer

        });


        conversationHistory =
            conversationHistory.slice(
                -12
            );


        aiThinking = false;


        // ====================================================
        // DISPLAY
        // ====================================================

        showVoiceConversation(
            text,
            answer
        );


        // ====================================================
        // SPEAK
        // ====================================================

        if (
            conversationActive
        ) {

            speakVoiceResponse(
                answer,
                aiLanguage
            );

        }

    }
    catch (error) {

        console.error(
            "Voice AI error:",
            error
        );


        aiThinking = false;


        setVoiceStatus(
            "❌ Unable to connect to SpeakWise."
        );


        // Remove failed user message

        const lastMessage =
            conversationHistory[
                conversationHistory.length - 1
            ];


        if (
            lastMessage &&
            lastMessage.role === "user"
        ) {

            conversationHistory.pop();

        }


        // Keep conversation active

        if (
            conversationActive
        ) {

            setTimeout(
                function() {

                    startVoiceListening();

                },
                1200
            );

        }

    }

}


// ============================================================
// SHOW CONVERSATION
// ============================================================

function showVoiceConversation(
    userText,
    aiText
) {

    const transcript =
        document.getElementById(
            "voiceTranscript"
        );


    if (!transcript) {
        return;
    }


    let html = "";


    if (
        userText
    ) {

        html +=
            "<strong>You:</strong> " +
            escapeHTML(
                userText
            ) +
            "<br><br>";

    }


    if (
        aiText
    ) {

        html +=
            "<strong>🤖 SpeakWise:</strong> " +
            escapeHTML(
                aiText
            );

    }


    transcript.innerHTML =
        html;


    transcript.scrollTop =
        transcript.scrollHeight;

}


// ============================================================
// SHOW THINKING
// ============================================================

function showVoiceThinking(
    text
) {

    const transcript =
        document.getElementById(
            "voiceTranscript"
        );


    if (!transcript) {
        return;
    }


    transcript.innerHTML =

        "<strong>You:</strong> " +

        escapeHTML(
            text
        ) +

        "<br><br>" +

        "<strong>🤖 SpeakWise:</strong> Thinking...";

}


// ============================================================
// GET FEMALE VOICE
// ============================================================

function getFemaleVoice(
    language
) {

    const voices =
        window.speechSynthesis.getVoices();


    if (!voices.length) {

        return null;

    }


    // ========================================================
    // VOICE NAME KEYWORDS
    // ========================================================

    const femaleKeywords = [

        "female",
        "woman",
        "girl",

        "samantha",
        "zira",
        "susan",
        "karen",
        "victoria",

        "heera",
        "lekha",
        "kalpana",

        "google hindi",
        "google uk english female",

        "microsoft zira",
        "microsoft heera",

        "neerja"

    ];


    function isFemaleVoice(
        voice
    ) {

        const name =
            (
                voice.name ||
                ""
            ).toLowerCase();


        return femaleKeywords.some(
            function(keyword) {

                return name.includes(
                    keyword
                );

            }
        );

    }


    // ========================================================
    // HINDI
    // ========================================================

    if (
        language === "hindi"
    ) {

        // First: Hindi + female

        let voice =
            voices.find(
                function(v) {

                    return (
                        v.lang &&
                        v.lang
                            .toLowerCase()
                            .startsWith("hi") &&
                        isFemaleVoice(v)
                    );

                }
            );


        if (voice) {
            return voice;
        }


        // Second: any Hindi voice

        voice =
            voices.find(
                function(v) {

                    return (
                        v.lang &&
                        v.lang
                            .toLowerCase()
                            .startsWith("hi")
                    );

                }
            );


        if (voice) {
            return voice;
        }

    }


    // ========================================================
    // HINGLISH
    // ========================================================

    if (
        language === "hinglish"
    ) {

        // Prefer Hindi female voice

        let voice =
            voices.find(
                function(v) {

                    return (
                        v.lang &&
                        v.lang
                            .toLowerCase()
                            .startsWith("hi") &&
                        isFemaleVoice(v)
                    );

                }
            );


        if (voice) {
            return voice;
        }


        // Any Hindi voice

        voice =
            voices.find(
                function(v) {

                    return (
                        v.lang &&
                        v.lang
                            .toLowerCase()
                            .startsWith("hi")
                    );

                }
            );


        if (voice) {
            return voice;
        }


        // Female Indian English

        voice =
            voices.find(
                function(v) {

                    return (
                        v.lang &&
                        v.lang
                            .toLowerCase() ===
                            "en-in" &&
                        isFemaleVoice(v)
                    );

                }
            );


        if (voice) {
            return voice;
        }

    }


    // ========================================================
    // ENGLISH
    // ========================================================

    if (
        language === "english"
    ) {

        // Female Indian English

        let voice =
            voices.find(
                function(v) {

                    return (
                        v.lang &&
                        v.lang
                            .toLowerCase() ===
                            "en-in" &&
                        isFemaleVoice(v)
                    );

                }
            );


        if (voice) {
            return voice;
        }


        // Any female English voice

        voice =
            voices.find(
                function(v) {

                    return (
                        v.lang &&
                        v.lang
                            .toLowerCase()
                            .startsWith("en") &&
                        isFemaleVoice(v)
                    );

                }
            );


        if (voice) {
            return voice;
        }


        // Any Indian English

        voice =
            voices.find(
                function(v) {

                    return (
                        v.lang &&
                        v.lang
                            .toLowerCase() ===
                            "en-in"
                    );

                }
            );


        if (voice) {
            return voice;
        }

    }


    // ========================================================
    // FINAL FALLBACK
    // ========================================================

    return voices.find(
        function(v) {

            return (
                v.lang &&
                v.lang
                    .toLowerCase()
                    .startsWith("en")
            );

        }
    ) || voices[0];

}


// ============================================================
// AI TEXT TO SPEECH
// ============================================================

function speakVoiceResponse(
    text,
    language
) {

    if (
        !conversationActive
    ) {

        return;

    }


    // --------------------------------------------------------
    // MICROPHONE OFF
    // --------------------------------------------------------

    stopVoiceListening();


    // --------------------------------------------------------
    // SPEECH SUPPORT
    // --------------------------------------------------------

    if (
        !("speechSynthesis" in window)
    ) {

        aiSpeaking = false;


        updateVoiceButton();


        setTimeout(
            function() {

                if (
                    conversationActive
                ) {

                    startVoiceListening();

                }

            },
            500
        );


        return;

    }


    // --------------------------------------------------------
    // STOP PREVIOUS SPEECH
    // --------------------------------------------------------

    window.speechSynthesis.cancel();


    aiSpeaking = true;


    updateVoiceButton();


    setVoiceStatus(
        "🔊 SpeakWise is speaking..."
    );


    // ========================================================
    // CREATE SPEECH
    // ========================================================

    const speech =
        new SpeechSynthesisUtterance(
            text
        );


    // ========================================================
    // LANGUAGE
    // ========================================================

    let detectedLanguage =
        language;


    if (
        !detectedLanguage ||
        detectedLanguage === "auto"
    ) {

        detectedLanguage =
            detectLanguage(
                text
            );

    }


    console.log(
        "TTS language:",
        detectedLanguage
    );


    // ========================================================
    // SELECT FEMALE VOICE
    // ========================================================

    const selectedVoice =
        getFemaleVoice(
            detectedLanguage
        );


    if (
        selectedVoice
    ) {

        speech.voice =
            selectedVoice;


        speech.lang =
            selectedVoice.lang;


        console.log(
            "👩 Female voice selected:",
            selectedVoice.name,
            "|",
            selectedVoice.lang
        );

    }
    else {

        if (
            detectedLanguage ===
            "hindi"
        ) {

            speech.lang =
                "hi-IN";

        }
        else {

            speech.lang =
                "en-IN";

        }

    }


    // ========================================================
    // NATURAL FEMALE VOICE SETTINGS
    // ========================================================

    speech.rate =
        0.88;


    speech.pitch =
        1.08;


    speech.volume =
        1.0;


    // ========================================================
    // SPEECH START
    // ========================================================

    speech.onstart =
        function() {

            aiSpeaking = true;


            updateVoiceButton();


            setVoiceStatus(
                "🔊 SpeakWise is speaking..."
            );

        };


    // ========================================================
    // SPEECH END
    // ========================================================

    speech.onend =
        function() {

            aiSpeaking = false;


            updateVoiceButton();


            if (
                !conversationActive
            ) {

                return;

            }


            /*
             * VERY IMPORTANT:
             *
             * AI finished speaking.
             *
             * Automatically start
             * user's microphone.
             */

            setVoiceStatus(
                "🎤 Listening... Speak naturally."
            );


            setTimeout(
                function() {

                    if (
                        conversationActive &&
                        !aiSpeaking &&
                        !aiThinking &&
                        !voiceListening &&
                        !voiceStarting
                    ) {

                        startVoiceListening();

                    }

                },
                450
            );

        };


    // ========================================================
    // SPEECH ERROR
    // ========================================================

    speech.onerror =
        function(error) {

            console.log(
                "TTS error:",
                error
            );


            aiSpeaking = false;


            updateVoiceButton();


            if (
                conversationActive
            ) {

                setTimeout(
                    function() {

                        startVoiceListening();

                    },
                    700
                );

            }

        };


    // ========================================================
    // SPEAK
    // ========================================================

    window.speechSynthesis.speak(
        speech
    );

}


// ============================================================
// LOAD VOICES
// ============================================================

function loadAvailableVoices() {

    if (
        !("speechSynthesis" in window)
    ) {

        return;

    }


    const voices =
        window.speechSynthesis
            .getVoices();


    console.log(
        "Available voices:",
        voices.length
    );


    voices.forEach(
        function(voice) {

            console.log(
                voice.name,
                "|",
                voice.lang
            );

        }
    );

}


// ============================================================
// VOICES CHANGED
// ============================================================

if (
    "speechSynthesis" in window
) {

    window.speechSynthesis.onvoiceschanged =
        function() {

            loadAvailableVoices();

        };

}


// ============================================================
// STATUS
// ============================================================

function setVoiceStatus(
    text
) {

    const status =
        document.getElementById(
            "voiceStatus"
        );


    if (status) {

        status.textContent =
            text;

    }

}


// ============================================================
// ESCAPE HTML
// ============================================================

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


// ============================================================
// STOP EVERYTHING
// ============================================================

function stopAllVoice() {

    conversationActive = false;

    voiceListening = false;

    voiceStarting = false;

    aiSpeaking = false;

    aiThinking = false;

    conversationHistory = [];


    if (
        voiceRecognition
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


    voiceRecognition = null;


    if (
        "speechSynthesis" in window
    ) {

        window.speechSynthesis.cancel();

    }


    updateVoiceButton();

}


// ============================================================
// PAGE LOAD
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        updateVoiceButton();

        loadAvailableVoices();


        console.log(
            "======================================"
        );

        console.log(
            "SpeakWise AI Voice Conversation Ready"
        );

        console.log(
            "Hindi + Hinglish + English"
        );

        console.log(
            "Female AI Voice Enabled"
        );

        console.log(
            "Automatic Turn Taking Enabled"
        );

        console.log(
            "======================================"

        );

    }
);


// ============================================================
// CLEANUP
// ============================================================

window.addEventListener(
    "beforeunload",
    function() {

        stopAllVoice();

    }
);
