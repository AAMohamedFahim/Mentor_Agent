import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10.0.2/dist/mermaid.esm.min.mjs';

document.addEventListener('DOMContentLoaded', function () {
    let cardCount = 0;

    // Function to create a new card
    document.getElementById('sendBtn').addEventListener('click', () => {
        const topic = document.getElementById('topicInput').value;
        if (topic === '') {
            alert('Please enter a topic');
            return;
        }

        // Send the topic to the backend to generate or fetch flowchart data
        fetch('http://0.0.0.0:8000/api/generateFlowchart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic: topic }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === 'success') {
                    
                    createCard(data.topic, data.mermaid_code,data.progeress); // Create new card with the flowchart
                    document.getElementById('topicInput').value = ''; // Clear input field
                } else {
                    alert(data.message);
                }
            })
            .catch((error) => console.error('Error:', error));
    });

    // Function to create and append card
    function createCard(topic, flowchartData,progeress) {
        cardCount++;

        const card = document.createElement('div');
        card.className = 'flowcard';
        card.id = `card-${cardCount}`;

        const deleteIcon = document.createElement('span');
        deleteIcon.className = 'delete-icon';
        deleteIcon.innerHTML = '&times;';
        deleteIcon.onclick = () => deleteCard(card.id, topic);

        const title = document.createElement('h3');
        title.textContent = topic;

        card.appendChild(deleteIcon);
        card.appendChild(title);
        document.getElementById('cardContainer').appendChild(card);

        card.addEventListener('click', () => displayFlowchart(topic, flowchartData,progeress)); // Click to display flowchart
    }

    function displayFlowchart(topic, flowchartData,progeress) {
        const flowchartContainer = document.getElementById('flowchartDisplay');

        // Clear the previous graph content
        flowchartContainer.innerHTML = ''; 

        // Insert Mermaid diagram syntax
        flowchartContainer.innerHTML = `<div class="mermaid">${flowchartData}</div>`; 

        // Reinitialize Mermaid to render the newly added graph
        setTimeout(() => {
            mermaid.init();  // Reinitialize all Mermaid elements on the page after DOM updates
        }, 100);

        // Optionally, log or debug to ensure the right data is coming through
        console.log("Rendering flowchart for topic:", topic);
        console.log("Mermaid Code:", flowchartData);

        // Update progress details or other info
        document.getElementById('progressDetails').innerHTML = progeress;
    }

function deleteCard(cardId, topic) {
    const confirmDelete = confirm('Are you sure you want to delete this topic?');
    if (confirmDelete) {
        fetch(`http://0.0.0.0:8000/api/deleteFlowchart?topic=${encodeURIComponent(topic)}`, {  // Add correct URL
            method: 'DELETE',  // Ensure this is a DELETE request
        })
        .then(response => response.json())  // Parse the response as JSON
        .then(data => {
            if (data.status === 'success') {
                document.getElementById(cardId).remove();  // Remove card from UI
                
                // Check if the current flowchart being displayed is for the deleted topic
                const flowchartTitle = document.querySelector('#flowchartDisplay .mermaid');
                if (flowchartTitle && flowchartTitle.textContent.includes(topic)) {
                    // Clear the flowchart display if it's the current one being displayed
                    clearFlowchartDisplay();
                }
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function clearFlowchartDisplay() {
    document.getElementById('flowchartDisplay').innerHTML = '';  // Clear the flowchart content
    document.getElementById('progressDetails').innerHTML = '';   // Clear the progress details
}

document.getElementById('deleteAllBtn').addEventListener('click', () => {
    const confirmDeleteAll = confirm('Are you sure you want to delete all flowcharts?');
    if (confirmDeleteAll) {
        fetch('http://0.0.0.0:8000/api/deleteAllFlowcharts', {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('cardContainer').innerHTML = '';  // Remove all cards from UI
                clearFlowchartDisplay();  // Clear the flowchart display
                alert(data.message);
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
});


    function loadExistingTopics() {
        fetch('http://0.0.0.0:8000/api/getAllTopics')
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                data.topics.forEach((topic) => {
                    // Fetch the flowchart code for each existing topic
                    fetch(`http://0.0.0.0:8000/api/generateFlowchart`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ topic: topic }),
                    })
                        .then((response) => response.json())
                        .then((data) => {
                            if (data.status === 'success') {
                                createCard(topic, data.mermaid_code); // Create card for each stored topic
                            }
                        });
                });
            })
            .catch((error) => console.error('Error fetching topics:', error)); // Handle any error
    }

    // Load existing topics on page load
    loadExistingTopics();
});
document.addEventListener('DOMContentLoaded', function () {
    const chatbotButton = document.getElementById('chatbotButton');
    const chatbotPopup = document.getElementById('chatbotPopup');
    const closeChatbot = document.getElementById('closeChatbot');
    const chatbotConversation = document.getElementById('chatbotConversation');
    const chatbotInput = document.getElementById('chatbotInput');
    const sendChatbotMessage = document.getElementById('sendChatbotMessage');

    // Toggle chatbot popup
    chatbotButton.addEventListener('click', () => {
        chatbotPopup.style.display = chatbotPopup.style.display === 'block' ? 'none' : 'block';
        if (chatbotPopup.style.display === 'block') {
            loadChatbotHistory();
        }
    });

    // Close chatbot popup
    closeChatbot.addEventListener('click', () => {
        chatbotPopup.style.display = 'none';
    });

    // Send chatbot message
    sendChatbotMessage.addEventListener('click', () => {
        const message = chatbotInput.value;
        if (message) {
            appendUserMessage(message);  // Display user's message in the chat
            sendMessageToBackend(message); // Send to backend
            chatbotInput.value = ''; // Clear input field
        }
    });

    function sendMessageToBackend(message) {
        fetch('http://0.0.0.0:8000/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                appendBotMessage(data.response); // Display bot's response
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function appendUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chatbot-message user-message';  // Optional class for styling user message
        messageDiv.textContent = "You: " + message;
        chatbotConversation.appendChild(messageDiv);
    }

    function appendBotMessage(response) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chatbot-message bot-message';  // Optional class for styling bot message
        messageDiv.textContent = response;
        chatbotConversation.appendChild(messageDiv);
    }

    function loadChatbotHistory() {
        fetch('http://0.0.0.0:8000/api/chatbotHistory')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                chatbotConversation.innerHTML = ''; // Clear current conversation
                data.history.forEach(message => {
                    appendBotMessage(message); // Load previous messages
                });
            }
        })
        .catch(error => console.error('Error loading chatbot history:', error));
    }
});