/**
 * DocuAssist AI - Frontend Chat Interface
 * Handles user interactions and API communication
 */

const API_BASE = "http://localhost:8000/api";
let userId = localStorage.getItem("userId") || generateUserId();
let messagesData = [];

// ============== Initialize ==============

document.addEventListener("DOMContentLoaded", () => {
    // Store user ID for tracking
    localStorage.setItem("userId", userId);
    console.log("User ID:", userId);

    // Check system health
    checkSystemHealth();

    // Auto-scroll to bottom when messages load
    const messagesArea = document.getElementById("messages");
    const observer = new MutationObserver(() => {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    });
    observer.observe(messagesArea, { childList: true });

    // Settings listeners
    document.getElementById("showMetrics").addEventListener("change", toggleMetricsUI);
    document.getElementById("showSources").addEventListener("change", toggleSourcesUI);
});

// ============== Query Submission ==============

async function submitQuery(event) {
    event.preventDefault();

    const queryInput = document.getElementById("queryInput");
    const query = queryInput.value.trim();

    if (!query) {
        showToast("Please enter a question", "warning");
        return;
    }

    if (query.length > 1000) {
        showToast("Question is too long (max 1000 characters)", "error");
        return;
    }

    // Clear input
    queryInput.value = "";

    // Add user message to UI
    addMessageToUI(query, "user");

    // Show loading indicator with animated message
    showLoading(true);
    const metricsContainer = document.getElementById("metricsContainer");
    metricsContainer.style.display = "none";

    const loadingId = addLoadingAnimation();

    try {
        // Call API with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 sec timeout

        const response = await fetch(`${API_BASE}/chat/query`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: query,
                user_id: userId
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        // Handle HTTP errors
        if (!response.ok) {
            let errorMessage = "Failed to process query";
            
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (e) {
                // Response wasn't JSON
                errorMessage = `Server error (${response.status}): ${response.statusText}`;
            }

            throw new Error(errorMessage);
        }

        const data = await response.json();

        // Validate response data
        if (!data.response) {
            throw new Error("Invalid response from server");
        }

        // Remove loading animation
        removeLoadingAnimation(loadingId);

        // Add assistant response to UI
        addMessageToUI(data.response, "assistant", data);

        // Store message data
        messagesData.push({
            query_id: data.query_id,
            query: query,
            response: data.response,
            retrieved_documents: data.retrieved_documents,
            metrics: data.metrics
        });

        // Display metrics if enabled
        if (document.getElementById("showMetrics").checked) {
            displayMetrics(data.metrics);
            metricsContainer.style.display = "block";
        }

        // Display sources if enabled
        if (document.getElementById("showSources").checked) {
            displaySources(data.retrieved_documents, data.query_id);
        }

        showToast("Response received successfully", "success");

    } catch (error) {
        console.error("Query error:", error);
        removeLoadingAnimation(loadingId);

        // Handle different error types
        if (error.name === "AbortError") {
            addMessageToUI(
                "Error: Request timed out. The server took too long to respond. Please try again.",
                "error"
            );
            showToast("Request timeout - please try again", "error");
        } else {
            addMessageToUI(
                `Error: ${error.message}. Please try again.`,
                "error"
            );
            showToast(`Error: ${error.message}`, "error");
        }
    } finally {
        showLoading(false);
    }
}

// ============== UI Functions ==============

function addMessageToUI(content, role, data = null) {
    const messagesArea = document.getElementById("messages");

    if (messagesArea.querySelector(".welcome-message")) {
        messagesArea.querySelector(".welcome-message").remove();
    }

    const messageDiv = document.createElement("div");
    messageDiv.className = `message message-${role}`;

    let contentHTML = `<div class="message-content">${escapeHtml(content)}</div>`;

    if (role === "assistant" && data) {
        contentHTML += `
            <div class="message-footer">
                <small>Query ID: ${data.query_id.substring(0, 8)}...</small>
                <button class="feedback-button" onclick="showFeedbackDialog('${data.query_id}')">
                    Rate this response →
                </button>
            </div>
        `;
    }

    messageDiv.innerHTML = contentHTML;
    messagesArea.appendChild(messageDiv);

    // Auto-scroll
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function displayMetrics(metrics) {
    document.getElementById("retrievalLatency").textContent = `${metrics.retrieval_latency_ms.toFixed(2)}ms`;
    document.getElementById("generationLatency").textContent = `${metrics.generation_latency_ms.toFixed(2)}ms`;
    document.getElementById("totalLatency").textContent = `${metrics.total_latency_ms.toFixed(2)}ms`;
    document.getElementById("docCount").textContent = metrics.document_count;
}

function displaySources(documents, queryId) {
    const messagesArea = document.getElementById("messages");

    if (documents.length > 0) {
        const sourceDiv = document.createElement("div");
        sourceDiv.className = "sources-container";

        let sourcesHTML = `<details class="sources-details">
            <summary>📚 Retrieved Documents (${documents.length})</summary>
            <div class="sources-list">`;

        documents.forEach((doc, index) => {
            const score = (doc.relevance_score * 100).toFixed(1);
            sourcesHTML += `
                <div class="source-item">
                    <div class="source-header">
                        <strong>Source ${index + 1}</strong>
                        <span class="relevance-badge">${score}% relevant</span>
                    </div>
                    <p class="source-text">${escapeHtml(doc.text.substring(0, 200))}...</p>
                </div>
            `;
        });

        sourcesHTML += `</div></details>`;
        sourceDiv.innerHTML = sourcesHTML;
        messagesArea.appendChild(sourceDiv);
    }
}

function showLoading(show) {
    document.getElementById("loadingIndicator").style.display = show ? "flex" : "none";
    document.getElementById("sendBtn").disabled = show;
}

function fillQuery(text) {
    document.getElementById("queryInput").value = text;
    document.getElementById("queryInput").focus();
}

function executeQuery(text) {
    // Set the query input and immediately submit
    document.getElementById("queryInput").value = text;
    // Create and dispatch a form submission event
    const form = document.getElementById("queryForm");
    const submitEvent = new Event("submit", { bubbles: true, cancelable: true });
    form.dispatchEvent(submitEvent);
}

function toggleMetricsUI() {
    const container = document.getElementById("metricsContainer");
    if (document.getElementById("showMetrics").checked) {
        if (messagesData.length > 0) {
            container.style.display = "block";
        }
    } else {
        container.style.display = "none";
    }
}

function toggleSourcesUI() {
    const sourcesContainers = document.querySelectorAll(".sources-container");
    sourcesContainers.forEach(el => {
        el.style.display = document.getElementById("showSources").checked ? "block" : "none";
    });
}

// ============== Feedback ==============

function showFeedbackDialog(queryId) {
    const rating = prompt("Rate this response (1-5):", "5");
    if (rating === null) return;

    const ratingNum = parseInt(rating);
    if (isNaN(ratingNum) || ratingNum < 1 || ratingNum > 5) {
        showToast("Please enter a number between 1 and 5", "error");
        return;
    }

    const feedback = prompt("Any additional feedback? (optional):");
    submitFeedback(queryId, ratingNum, feedback);
}

async function submitFeedback(queryId, rating, feedbackText) {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/feedback/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query_id: queryId,
                user_id: userId,
                rating: rating,
                feedback_text: feedbackText || null
            })
        });

        if (!response.ok) {
            let errorMessage = "Failed to submit feedback";
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch (e) {
                errorMessage = `Server error (${response.status})`;
            }
            throw new Error(errorMessage);
        }

        showToast(`Thank you! Your ${rating}-star rating has been recorded.`, "success");
    } catch (error) {
        console.error("Feedback error:", error);
        showToast(`Error: ${error.message}`, "error");
    } finally {
        showLoading(false);
    }
}

// ============== Health Check ==============

async function checkSystemHealth() {
    const maxRetries = 3;
    let retries = 0;

    while (retries < maxRetries) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);

            const response = await fetch(`${API_BASE}/chat/health`, {
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                document.getElementById("systemStatus").className = "status-indicator healthy";
                document.getElementById("statusText").textContent = "Healthy";
                return; // Success, exit
            }
        } catch (error) {
            console.warn(`Health check failed (attempt ${retries + 1}/${maxRetries}):`, error.message);
            retries++;

            if (retries < maxRetries) {
                // Wait before retrying
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    }

    // All retries exhausted
    document.getElementById("systemStatus").className = "status-indicator unhealthy";
    document.getElementById("statusText").textContent = "Offline";
    showToast("System is currently unavailable", "error");
}

// Periodic health checks every 30 seconds
setInterval(checkSystemHealth, 30000);

// ============== Utilities ==============

let loadingAnimationCount = 0;

function addLoadingAnimation() {
    const messagesArea = document.getElementById("messages");
    const loadingDiv = document.createElement("div");
    const loadingId = `loading_${Date.now()}_${loadingAnimationCount++}`;
    loadingDiv.id = loadingId;
    loadingDiv.className = "message message-loading";
    loadingDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <small>AI is thinking...</small>
        </div>
    `;
    messagesArea.appendChild(loadingDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
    return loadingId;
}

function removeLoadingAnimation(loadingId) {
    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) {
        loadingEl.remove();
    }
}

function generateUserId() {
    return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    
    // Limit to 3 toasts max
    const existingToasts = container.querySelectorAll(".toast").length;
    if (existingToasts >= 3) {
        const oldestToast = container.querySelector(".toast");
        if (oldestToast) oldestToast.remove();
    }
    
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("show");
    }, 10);

    const removeTimer = setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 300);
    }, 4000);

    // Allow clicking close button to dismiss
    const closeBtn = toast.querySelector(".toast-close");
    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            clearTimeout(removeTimer);
            toast.classList.remove("show");
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        });
    }
}
