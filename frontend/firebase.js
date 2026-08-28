// ==================================================
// SPEAKWISE AI - FIREBASE AUTHENTICATION
// Google Login + Mobile OTP
// ==================================================

import {
    initializeApp
} from "https://www.gstatic.com/firebasejs/12.18.0/firebase-app.js";

import {
    getAuth,
    GoogleAuthProvider,
    signInWithPopup,
    signInWithPhoneNumber,
    RecaptchaVerifier,
    onAuthStateChanged,
    signOut
} from "https://www.gstatic.com/firebasejs/12.18.0/firebase-auth.js";


// ==================================================
// FIREBASE CONFIG
// ==================================================

const firebaseConfig = {

    apiKey:
        "AIzaSyAtO5LrW30cMwcc9FrmqlH64z4B1jTS78I",

    authDomain:
        "speakwise-ai-07.firebaseapp.com",

    projectId:
        "speakwise-ai-07",

    storageBucket:
        "speakwise-ai-07.firebasestorage.app",

    messagingSenderId:
        "887934287599",

    appId:
        "1:887934287599:web:1b809625946c4ea60b251a",

    measurementId:
        "G-7CB9DY58M4"
};


// ==================================================
// INITIALIZE
// ==================================================

const app =
    initializeApp(
        firebaseConfig
    );

const auth =
    getAuth(app);

const googleProvider =
    new GoogleAuthProvider();


// ==================================================
// PHONE AUTH STATE
// ==================================================

let recaptchaVerifier =
    null;

let confirmationResult =
    null;


// ==================================================
// AUTH MESSAGE
// ==================================================

function showAuthMessage(message) {

    const element =
        document.getElementById(
            "authMessage"
        );


    if (!element) {

        console.log(message);

        return;

    }


    element.textContent =
        message;


    element.classList.remove(
        "hidden"
    );


    clearTimeout(
        window.authMessageTimer
    );


    window.authMessageTimer =
        setTimeout(
            () => {

                element.classList.add(
                    "hidden"
                );

            },
            5000
        );

}


// ==================================================
// GOOGLE LOGIN
// ==================================================

async function googleLogin() {

    const button =
        document.getElementById(
            "googleLoginButton"
        );


    try {

        if (button) {

            button.disabled =
                true;

            button.innerHTML =
                `
                <span class="google-logo">G</span>
                Signing in...
                `;

        }


        const result =
            await signInWithPopup(
                auth,
                googleProvider
            );


        const user =
            result.user;


        console.log(
            "Google login successful:",
            user
        );


        updateUserUI(
            user
        );


        showAuthMessage(
            `Welcome, ${
                user.displayName ||
                "User"
            }! 🎉`
        );


        closeProfile();

    }

    catch (error) {

        console.error(
            "Google Login Error:",
            error
        );


        if (
            error.code ===
            "auth/popup-closed-by-user"
        ) {

            showAuthMessage(
                "Login window was closed."
            );

        }

        else if (
            error.code ===
            "auth/popup-blocked"
        ) {

            showAuthMessage(
                "Please allow popups for SpeakWise."
            );

        }

        else if (
            error.code ===
            "auth/unauthorized-domain"
        ) {

            showAuthMessage(
                "This website is not authorized in Firebase."
            );

        }

        else {

            showAuthMessage(
                error.message ||
                "Google login failed."
            );

        }

    }

    finally {

        if (button) {

            button.disabled =
                false;

            button.innerHTML =
                `
                <span class="google-logo">G</span>
                <span>Continue with Google</span>
                `;

        }

    }

}


// ==================================================
// CREATE RECAPTCHA
// ==================================================

async function createRecaptcha() {

    const container =
        document.getElementById(
            "recaptcha-container"
        );


    if (!container) {

        throw new Error(
            "reCAPTCHA container not found."
        );

    }


    // If an old verifier exists,
    // remove it first.

    if (recaptchaVerifier) {

        try {

            recaptchaVerifier.clear();

        }

        catch (error) {

            console.log(
                "Old reCAPTCHA cleanup:",
                error
            );

        }


        recaptchaVerifier =
            null;

    }


    container.innerHTML =
        "";


    recaptchaVerifier =
        new RecaptchaVerifier(
            auth,
            "recaptcha-container",
            {

                size:
                    "normal",

                callback:
                    function() {

                        console.log(
                            "reCAPTCHA completed."
                        );

                    },

                "expired-callback":
                    function() {

                        console.log(
                            "reCAPTCHA expired."
                        );

                        showAuthMessage(
                            "reCAPTCHA expired. Please verify again."
                        );

                    }

            }
        );


    await recaptchaVerifier.render();


    return recaptchaVerifier;

}


// ==================================================
// NORMALIZE INDIAN PHONE NUMBER
// ==================================================

function normalizePhoneNumber(
    value
) {

    let phone =
        value
            .trim()
            .replace(
                /[\s()-]/g,
                ""
            );


    // 9876543210
    if (
        /^\d{10}$/.test(
            phone
        )
    ) {

        phone =
            "+91" +
            phone;

    }


    // 919876543210
    else if (
        /^91\d{10}$/.test(
            phone
        )
    ) {

        phone =
            "+" +
            phone;

    }


    return phone;

}


// ==================================================
// SEND OTP
// ==================================================

async function sendOTP() {

    const phoneInput =
        document.getElementById(
            "phoneNumber"
        );


    const sendButton =
        document.getElementById(
            "sendOtpButton"
        );


    const otpSection =
        document.getElementById(
            "otpSection"
        );


    if (!phoneInput) {

        showAuthMessage(
            "Phone number field not found."
        );

        return;

    }


    const phoneNumber =
        normalizePhoneNumber(
            phoneInput.value
        );


    // ==================================================
    // VALIDATION
    // ==================================================

    if (!phoneNumber) {

        showAuthMessage(
            "Please enter your mobile number."
        );

        phoneInput.focus();

        return;

    }


    if (
        !/^\+[1-9]\d{7,14}$/.test(
            phoneNumber
        )
    ) {

        showAuthMessage(
            "Enter a valid number. Example: +91 9876543210"
        );

        phoneInput.focus();

        return;

    }


    try {

        if (sendButton) {

            sendButton.disabled =
                true;

            sendButton.textContent =
                "Sending OTP...";

        }


        showAuthMessage(
            "Complete the reCAPTCHA verification."
        );


        // ==================================================
        // CREATE FRESH RECAPTCHA
        // ==================================================

        const verifier =
            await createRecaptcha();


        // ==================================================
        // SEND OTP
        // ==================================================

        confirmationResult =
            await signInWithPhoneNumber(
                auth,
                phoneNumber,
                verifier
            );


        console.log(
            "OTP successfully sent."
        );


        // ==================================================
        // SHOW OTP
        // ==================================================

        if (otpSection) {

            otpSection.classList.remove(
                "hidden"
            );

        }


        phoneInput.disabled =
            true;


        if (sendButton) {

            sendButton.disabled =
                true;

            sendButton.textContent =
                "OTP Sent ✓";

        }


        showAuthMessage(
            "OTP sent successfully. Check your phone. 📱"
        );


        const otpInput =
            document.getElementById(
                "otpCode"
            );


        if (otpInput) {

            otpInput.focus();

        }

    }

    catch (error) {

        console.error(
            "Send OTP Error:",
            error
        );


        confirmationResult =
            null;


        if (sendButton) {

            sendButton.disabled =
                false;

            sendButton.textContent =
                "Send OTP";

        }


        if (
            error.code ===
            "auth/invalid-phone-number"
        ) {

            showAuthMessage(
                "Invalid mobile number."
            );

        }

        else if (
            error.code ===
            "auth/too-many-requests"
        ) {

            showAuthMessage(
                "Too many attempts. Please try again later."
            );

        }

        else if (
            error.code ===
            "auth/quota-exceeded"
        ) {

            showAuthMessage(
                "SMS quota exceeded. Please try later."
            );

        }

        else if (
            error.code ===
            "auth/captcha-check-failed"
        ) {

            showAuthMessage(
                "reCAPTCHA verification failed. Please try again."
            );

        }

        else {

            showAuthMessage(
                error.message ||
                "Could not send OTP."
            );

        }


        resetRecaptcha();

    }

}


// ==================================================
// VERIFY OTP
// ==================================================

async function verifyOTP() {

    const otpInput =
        document.getElementById(
            "otpCode"
        );


    const verifyButton =
        document.getElementById(
            "verifyOtpButton"
        );


    if (!confirmationResult) {

        showAuthMessage(
            "Please request an OTP first."
        );

        return;

    }


    const code =
        otpInput
            ?.value
            ?.trim() ||
        "";


    if (
        !/^\d{6}$/.test(
            code
        )
    ) {

        showAuthMessage(
            "Please enter the 6-digit OTP."
        );

        otpInput?.focus();

        return;

    }


    try {

        if (verifyButton) {

            verifyButton.disabled =
                true;

            verifyButton.textContent =
                "Verifying...";

        }


        const result =
            await confirmationResult.confirm(
                code
            );


        const user =
            result.user;


        console.log(
            "Phone login successful:",
            user
        );


        updateUserUI(
            user
        );


        showAuthMessage(
            "Mobile login successful! 🎉"
        );


        confirmationResult =
            null;


        resetRecaptcha();


        closeProfile();

    }

    catch (error) {

        console.error(
            "Verify OTP Error:",
            error
        );


        if (verifyButton) {

            verifyButton.disabled =
                false;

            verifyButton.textContent =
                "Verify OTP";

        }


        if (
            error.code ===
            "auth/invalid-verification-code"
        ) {

            showAuthMessage(
                "Incorrect OTP. Please check and try again."
            );

        }

        else if (
            error.code ===
            "auth/code-expired"
        ) {

            showAuthMessage(
                "OTP expired. Please request a new OTP."
            );


            confirmationResult =
                null;


            resetPhoneForm();

        }

        else {

            showAuthMessage(
                error.message ||
                "OTP verification failed."
            );

        }

    }

}


// ==================================================
// RESET RECAPTCHA
// ==================================================

function resetRecaptcha() {

    if (recaptchaVerifier) {

        try {

            recaptchaVerifier.clear();

        }

        catch (error) {

            console.log(
                "reCAPTCHA cleanup:",
                error
            );

        }

    }


    recaptchaVerifier =
        null;


    const container =
        document.getElementById(
            "recaptcha-container"
        );


    if (container) {

        container.innerHTML =
            "";

    }

}


// ==================================================
// RESET PHONE FORM
// ==================================================

function resetPhoneForm() {

    const phoneInput =
        document.getElementById(
            "phoneNumber"
        );


    const otpInput =
        document.getElementById(
            "otpCode"
        );


    const otpSection =
        document.getElementById(
            "otpSection"
        );


    const sendButton =
        document.getElementById(
            "sendOtpButton"
        );


    const verifyButton =
        document.getElementById(
            "verifyOtpButton"
        );


    if (phoneInput) {

        phoneInput.disabled =
            false;

    }


    if (phoneInput) {

        phoneInput.value =
            "";

    }


    if (otpInput) {

        otpInput.value =
            "";

    }


    if (otpSection) {

        otpSection.classList.add(
            "hidden"
        );

    }


    if (sendButton) {

        sendButton.disabled =
            false;

        sendButton.textContent =
            "Send OTP";

    }


    if (verifyButton) {

        verifyButton.disabled =
            false;

        verifyButton.textContent =
            "Verify OTP";

    }


    confirmationResult =
        null;


    resetRecaptcha();

}


// ==================================================
// UPDATE USER UI
// ==================================================

function updateUserUI(
    user
) {

    const name =
        document.getElementById(
            "profileUserName"
        );


    const email =
        document.getElementById(
            "profileUserEmail"
        );


    const avatar =
        document.getElementById(
            "profileAvatar"
        );


    const sidebarName =
        document.getElementById(
            "sidebarUserName"
        );


    const sidebarStatus =
        document.getElementById(
            "sidebarUserStatus"
        );


    const sidebarAvatar =
        document.getElementById(
            "sidebarProfileAvatar"
        );


    // ==================================================
    // GUEST
    // ==================================================

    if (!user) {

        if (name) {

            name.textContent =
                "Guest User";

        }


        if (email) {

            email.textContent =
                "Sign in to save your progress";

        }


        if (avatar) {

            avatar.innerHTML =
                "👤";

        }


        if (sidebarName) {

            sidebarName.textContent =
                "Guest User";

        }


        if (sidebarStatus) {

            sidebarStatus.textContent =
                "Sign in";

        }


        if (sidebarAvatar) {

            sidebarAvatar.innerHTML =
                "👤";

        }


        localStorage.removeItem(
            "speakwise_user"
        );


        return;

    }


    // ==================================================
    // LOGGED IN
    // ==================================================

    const displayName =
        user.displayName ||
        "SpeakWise User";


    const contact =
        user.email ||
        user.phoneNumber ||
        "Signed in";


    if (name) {

        name.textContent =
            displayName;

    }


    if (email) {

        email.textContent =
            contact;

    }


    if (sidebarName) {

        sidebarName.textContent =
            displayName;

    }


    if (sidebarStatus) {

        sidebarStatus.textContent =
            "Signed in";

    }


    if (user.photoURL) {

        const image =
            document.createElement(
                "img"
            );


        image.src =
            user.photoURL;


        image.alt =
            "Profile";


        image.referrerPolicy =
            "no-referrer";


        if (avatar) {

            avatar.innerHTML =
                "";

            avatar.appendChild(
                image
            );

        }


        if (sidebarAvatar) {

            sidebarAvatar.innerHTML =
                "";

            const sideImage =
                image.cloneNode(
                    true
                );


            sidebarAvatar.appendChild(
                sideImage
            );

        }

    }

    else {

        if (avatar) {

            avatar.innerHTML =
                "👤";

        }


        if (sidebarAvatar) {

            sidebarAvatar.innerHTML =
                "👤";

        }

    }


    // ==================================================
    // SAVE USER LOCALLY
    // ==================================================

    localStorage.setItem(

        "speakwise_user",

        JSON.stringify({

            uid:
                user.uid,

            name:
                user.displayName ||
                "",

            email:
                user.email ||
                "",

            phone:
                user.phoneNumber ||
                "",

            photo:
                user.photoURL ||
                ""

        })

    );

}


// ==================================================
// PROFILE
// ==================================================

function openProfile() {

    const modal =
        document.getElementById(
            "profileModal"
        );


    if (modal) {

        modal.classList.remove(
            "hidden"
        );

    }

}


function closeProfile() {

    const modal =
        document.getElementById(
            "profileModal"
        );


    if (modal) {

        modal.classList.add(
            "hidden"
        );

    }

}


// ==================================================
// LOGOUT
// ==================================================

async function logoutUser() {

    try {

        await signOut(
            auth
        );


        updateUserUI(
            null
        );


        resetPhoneForm();


        showAuthMessage(
            "Signed out successfully."
        );

    }

    catch (error) {

        console.error(
            "Logout error:",
            error
        );


        showAuthMessage(
            "Could not sign out."
        );

    }

}


// ==================================================
// AUTH STATE
// ==================================================

onAuthStateChanged(

    auth,

    function(user) {

        console.log(
            "Auth state:",
            user
                ? user.uid
                : "Guest"
        );


        updateUserUI(
            user
        );

    }

);


// ==================================================
// GLOBAL FUNCTIONS
// ==================================================

window.googleLogin =
    googleLogin;

window.sendOTP =
    sendOTP;

window.verifyOTP =
    verifyOTP;

window.logoutUser =
    logoutUser;

window.openProfile =
    openProfile;

window.closeProfile =
    closeProfile;

window.firebaseAuth =
    auth;

window.firebaseApp =
    app;


console.log(
    "✅ SpeakWise Firebase Auth loaded"
);