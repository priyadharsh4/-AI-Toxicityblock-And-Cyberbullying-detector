document.addEventListener('DOMContentLoaded', function() {
    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const tabs = document.querySelectorAll('.tab-content');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.dataset.tab;
            
            navItems.forEach(i => i.classList.remove('active'));
            tabs.forEach(t => t.classList.remove('active'));
            
            item.classList.add('active');
            document.getElementById(targetTab + '-tab').classList.add('active');
        });
    });

    // Analyzer functionality
    const analyzeBtn = document.getElementById('analyzeBtn');
    const voiceBtn = document.getElementById('voiceBtn');
    const commentInput = document.getElementById('commentInput');
    const charCount = document.getElementById('charCount');
    const resultCard = document.getElementById('resultCard');
    const processing = document.getElementById('processing');
    const voiceRecording = document.getElementById('voiceRecording');

    // Character counter
    commentInput.addEventListener('input', () => {
        charCount.textContent = commentInput.value.length;
    });

    // Analyze button
    analyzeBtn.addEventListener('click', async () => {
        const text = commentInput.value.trim();
        if (!text) return shake(commentInput);

        showProcessing();
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text})
            });
            const data = await response.json();
            showResult(data);
        } catch (error) {
            showResult({status: 'error', message: 'Connection failed!'});
        }
    });

    // Voice button (real implementation using Web Speech API)
    voiceBtn.addEventListener('click', () => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert('Speech Recognition not supported in this browser');
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        showVoiceRecording();
        
        recognition.onstart = () => {
            console.log('Voice recognition started');
        };

        recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcriptSegment = event.results[i][0].transcript;
                transcript += transcriptSegment;
            }
            
            if (event.results[0].isFinal) {
                hideVoiceRecording();
                commentInput.value = transcript;
                showProcessing();
                
                // Analyze the recognized text
                fetch('/predict', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: transcript})
                })
                .then(res => res.json())
                .then(data => {
                    showResult(data);
                })
                .catch(error => {
                    showResult({status: 'error', message: 'Connection failed!'});
                });
            }
        };

        recognition.onerror = (event) => {
            hideVoiceRecording();
            alert('Error: ' + event.error);
        };

        recognition.onend = () => {
            hideVoiceRecording();
        };

        recognition.start();
    });

    // Chat functionality
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendChatBtn');
    const chatMessages = document.getElementById('chatMessages');

    sendBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });

    function sendChatMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Add user message (sender A)
        const messageDiv = addChatMessage(text, 'user');
        chatInput.value = '';

        // Analyze in background
        fetch('/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text})
        })
        .then(res => {
            if (!res.ok) throw new Error('Network response was not ok');
            return res.json();
        })
        .then(data => {
            if (data.status === 'toxic' && data.labels && data.labels.length > 0) {
                // Remove toxic message - don't send it
                messageDiv.remove();
            } else {
                // Safe message - add receiver (B) response
                setTimeout(() => {
                    addChatMessage('Got your message: "' + text + '" ✅', 'bot');
                }, 500);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            // If error, treat as safe and add receiver response
            setTimeout(() => {
                addChatMessage('Got your message: "' + text + '" ✅', 'bot');
            }, 500);
        });
    }

    // Voice Chat functionality
    const voiceChatMessages = document.getElementById('voiceChatMessages');
    const startVoiceBtn = document.getElementById('startVoiceBtn');

    startVoiceBtn.addEventListener('click', startVoiceChat);

    function startVoiceChat() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert('Speech Recognition not supported in this browser');
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        startVoiceBtn.disabled = true;
        startVoiceBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        recognition.onstart = () => {
            console.log('Voice chat recording started');
        };

        recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcriptSegment = event.results[i][0].transcript;
                transcript += transcriptSegment;
            }
            
            if (event.results[0].isFinal) {
                startVoiceBtn.disabled = false;
                startVoiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';

                // Add user voice message
                const messageDiv = addVoiceChatMessage(transcript, 'user');

                // Analyze in background
                fetch('/predict', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: transcript})
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'toxic' && data.labels && data.labels.length > 0) {
                        // Remove toxic message
                        messageDiv.remove();
                    } else {
                        // Safe message - add receiver response
                        setTimeout(() => {
                            addVoiceChatMessage('Got your message: "' + transcript + '" ✅', 'bot');
                        }, 500);
                    }
                })
                .catch(error => {
                    // If error, treat as safe
                    setTimeout(() => {
                        addVoiceChatMessage('Got your message: "' + transcript + '" ✅', 'bot');
                    }, 500);
                });
            }
        };

        recognition.onerror = (event) => {
            startVoiceBtn.disabled = false;
            startVoiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            console.error('Voice recognition error:', event.error);
        };

        recognition.onend = () => {
            startVoiceBtn.disabled = false;
            startVoiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        };

        recognition.start();
    }

    function addVoiceChatMessage(text, type) {
        const div = document.createElement('div');
        div.className = `message ${type}-message`;
        div.innerHTML = `<div class="message-content">${text}</div>`;
        voiceChatMessages.appendChild(div);
        voiceChatMessages.scrollTop = voiceChatMessages.scrollHeight;
        return div;
    }

    function addChatMessage(text, type) {
        const div = document.createElement('div');
        div.className = `message ${type}-message`;
        div.innerHTML = `<div class="message-content">${text}</div>`;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return div;
    }

    // Utility functions
    function showProcessing() {
        processing.classList.remove('hidden');
        resultCard.classList.add('hidden');
        voiceRecording.classList.add('hidden');
    }

    function showVoiceRecording() {
        voiceRecording.classList.remove('hidden');
        processing.classList.add('hidden');
        resultCard.classList.add('hidden');
    }

    function hideVoiceRecording() {
        voiceRecording.classList.add('hidden');
    }

    function showResult(data) {
        processing.classList.add('hidden');
        resultCard.classList.remove('hidden');
        
        const isToxic = data.status === 'toxic';
        resultCard.className = `result-card ${isToxic ? 'result-toxic' : 'result-safe'} hidden`;
        
        const labels = data.labels?.length ? data.labels.join(', ') : 'No issues detected';
        const textDisplay = data.text ? `<div style="font-size: 1rem; opacity: 0.8; margin-bottom: 1rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px; word-wrap: break-word;">"${data.text}"</div>` : '';
        
        resultCard.innerHTML = `
            ${textDisplay}
            <div style="font-size: 3rem; margin-bottom: 1rem;">
                ${isToxic ? '⚠️ TOXIC DETECTED' : '✅ SAFE CONTENT'}
            </div>
            <div style="font-size: 1.3rem; opacity: 0.9;">
                Detected: ${labels}
            </div>
        `;
        setTimeout(() => resultCard.classList.remove('hidden'), 100);
    }

    function shake(element) {
        element.style.animation = 'shake 0.5s';
        setTimeout(() => element.style.animation = '', 500);
    }
});
