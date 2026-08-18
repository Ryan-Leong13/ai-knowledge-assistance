const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const errorBanner = document.getElementById("error-banner");

function scrollToBottom(){
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function addUserMesssage(text){
    const div = document.createElement("div");
    div.className = "message user";
    div.innerHTML = `<div class = "bubble"></div>`;
    div.querySelector(".bubble").textContent = text;
    chatWindow.appendChild(div);
    scrollToBottom();
}

function addLoadingMessage(){
    const div = document.createElement("div");
    div.className = "message assistant";
    div.innerHTML = `<div class = "bubble loading">Loading...</div>`;
    chatWindow.appendChild(div);
    scrollToBottom();
    return div;
}

function renderAssistantManager(container, answer, sources){
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = answer;
    container.innerHTML = "";
    container.appendChild(bubble);

    if(sources && sources.length > 0){
        const details = document.createElement("details");
        details.className = "sources";
        const summary = document.createElement("summary");
        summary.textContent = `view ${sources.length} source${sources.length > 1 ? "s" : ""}`;
        details.appendChild(summary);

        sources.forEach((src) => {
            const item = document.createElement("div");
            item.className = "source-item";

            const title = document.createElement("div");
            title.className = "source-title";
            title.textContent = src.title;

            const snippet = document.createElement("div");
            snippet.className = "source-snippet";
            
            const preview = src.content.length > 220
                ? src.content.slice(0, 220) + "..."
                : src.content;
            snippet.textContent = preview;

            item.appendChild(title);
            item.appendChild(snippet);
            details.appendChild(item);
        })

        container.appendChild(details);
    }

    scrollToBottom();
}

function showError(message){
    errorBanner.textContent = message;
    errorBanner.hidden = false;
}

function hideError(){
    errorBanner.hidden = true;
}

async function sendMessage(message){
    addUserMesssage(message);
    hideError();

    const loadingContainer = addLoadingMessage();
    sendBtn.disabled = true;
    chatInput.disabled = true;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type" : "application/json"},
            body: JSON.stringify({ message }),
        });

        if(!response.ok){
            let detail = "Something went wrong. Please try again.";
            try {
                const errBody = await response.json();
                if(errBody.detail){
                    detail = typeof errBody.detail === "string"
                        ? errBody.detail
                        : JSON.stringify(errBody.detail);
                }
            } catch (_) {
                // response body wasn't JSON, keep default message
            }
            loadingContainer.remove();
            showError(detail);
            return;
        }

        const data = await response.json();
        renderAssistantManager(loadingContainer, data.answer, data.sources);
    } catch (err) {
        loadingContainer.remove();
        showError("Could not reach the server. Please check your connection and try again");
    } finally {
        sendBtn.disabled = false;
        chatInput.disabled = false;
        chatInput.focus();
    }
}

chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if(!message) return;
    chatInput.value = "";
    sendMessage(message);
});