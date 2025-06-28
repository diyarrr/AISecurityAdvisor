document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const loginContainer = document.getElementById('login-container');
  const chatContainer = document.getElementById('chat-container');
  const userInfo = document.getElementById('user-info');
  const userIdInput = document.getElementById('user-id-input');
  const loginButton = document.getElementById('login-button');
  const chatMessages = document.getElementById('chat-messages');
  const userInput = document.getElementById('user-input');
  const sendButton = document.getElementById('send-button');
  const rankNumber = document.getElementById('rank-number');
  const rankName = document.getElementById('rank-name');
  const xpProgress = document.getElementById('xp-progress');
  const currentXp = document.getElementById('current-xp');
  const nextRankXp = document.getElementById('next-rank-xp');
  const xpNotification = document.getElementById('xp-notification');
  const xpGained = document.getElementById('xp-gained');
  
  // Templates
  const userMessageTemplate = document.getElementById('user-message-template');
  const botMessageTemplate = document.getElementById('bot-message-template');
  const rankUpNotificationTemplate = document.getElementById('rank-up-notification-template');
  
  // User data
  let userData = null;
  
  // API URL - change this to your backend URL
  const API_URL = '/api';

  function parseMarkdown(text) {
  return marked.parse(text);
}
  
  // Initialize event listeners
  function init() {
      loginButton.addEventListener('click', handleLogin);
      userIdInput.addEventListener('keypress', function(e) {
          if (e.key === 'Enter') {
              handleLogin();
          }
      });
      
      sendButton.addEventListener('click', sendMessage);
      userInput.addEventListener('keypress', function(e) {
          if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
          }
      });
      
      // Check for existing session
      const savedUserId = localStorage.getItem('chatbot_user_id');
      if (savedUserId) {
          userIdInput.value = savedUserId;
          handleLogin();
      }
  }
  
  // Handle login
  async function handleLogin() {
      const userId = userIdInput.value.trim();
      if (!userId) {
          alert('Please enter a User ID');
          return;
      }
      
      try {
          const response = await fetch(`${API_URL}/login`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ user_id: userId }),
              credentials: 'include'
          });
          
          if (!response.ok) {
              throw new Error('Login failed');
          }
          
          const data = await response.json();
          userData = data.user;
          
          // Save user ID to local storage
          localStorage.setItem('chatbot_user_id', userId);
          
          // Show chat interface
          loginContainer.classList.add('hidden');
          chatContainer.classList.remove('hidden');
          userInfo.classList.remove('hidden');
          
          // Update user info display
          updateUserInfoDisplay();
          
      } catch (error) {
          console.error('Error during login:', error);
          alert('Failed to log in. Please try again.');
      }
  }
  
  // Send message to chatbot
  async function sendMessage() {
      const message = userInput.value.trim();
      if (!message) return;
      
      // Add user message to chat
      addMessageToChat('user', message);
      
      // Clear input
      userInput.value = '';
      
      // Add loading indicator
      const loadingMessage = addMessageToChat('bot', 'Thinking...');
      
      try {
          const response = await fetch(`${API_URL}/chat`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ query: message }),
              credentials: 'include'
          });
          
          if (!response.ok) {
              throw new Error('Failed to get response');
          }
          
          const data = await response.json();
          
          // Remove loading message
          loadingMessage.remove();
          
          // Add bot response to chat
          const botMessage = addMessageToChat('bot', data.answer);

          // After bot response
        if (data.followup_question) {
        const quizElement = addMessageToChat('bot', data.followup_question);
        setupQuizInteraction(quizElement, data.followup_question);
        }
          
          if (!data.restricted) {
    // Save old XP and rank
    const oldXp = userData.xp;
    const oldRank = userData.rank;

    // Update user data
    if (data.user) {
        userData = data.user;
        updateUserInfoDisplay();

        // Show XP gained difference only
        const gained = userData.xp - oldXp;
        if (gained !== 0) {
            showXpNotification(gained);
        }

        // Show rank up if needed
        if (userData.rank > oldRank) {
            showRankUpNotification(userData.rank, userData.rank_name);
        }
    }
}

          
      } catch (error) {
          console.error('Error sending message:', error);
          loadingMessage.querySelector('.message-content').textContent = 'Sorry, there was an error processing your request. Please try again.';
      }
  }
  
  // Add message to chat
  function addMessageToChat(sender, content) {
      const template = sender === 'user' ? userMessageTemplate : botMessageTemplate;
      const messageElement = document.importNode(template.content, true).firstElementChild;
      messageElement.querySelector('.message-content').innerHTML = parseMarkdown(content);
      
      chatMessages.appendChild(messageElement);
      
      // Scroll to bottom
      chatMessages.scrollTop = chatMessages.scrollHeight;
      
      return messageElement;
  }
  
  // Update user info display
  function updateUserInfoDisplay() {
      if (!userData) return;
      
      rankNumber.textContent = userData.rank;
      rankName.textContent = userData.rank_name;
      currentXp.textContent = userData.xp;
      
      // Handle next rank info
      if (userData.next_rank && userData.next_rank.threshold !== 'N/A') {
          nextRankXp.textContent = userData.next_rank.threshold;
          
          // Calculate XP progress percentage
          const currentXpVal = userData.xp;
          const prevRankThreshold = userData.rank > 1 ? calculatePreviousRankThreshold(userData.rank) : 0;
          const nextRankThreshold = userData.next_rank.threshold;
          
          const range = nextRankThreshold - prevRankThreshold;
          const progress = ((currentXpVal - prevRankThreshold) / range) * 100;
          
          xpProgress.style.width = `${progress}%`;
      } else {
          nextRankXp.textContent = "MAX";
          xpProgress.style.width = "100%";
      }
  }
  
  // Calculate previous rank threshold
  function calculatePreviousRankThreshold(rank) {
      // These should match the thresholds in the User class on the backend
      const thresholds = {
          1: 0,
          2: 100,
          3: 250,
          4: 500,
          5: 1000
      };
      
      return thresholds[rank - 1] || 0;
  }
  
  // Show XP notification
  function showXpNotification(points) {
  xpGained.textContent = `${points > 0 ? "+" : ""}${points}`;
  xpNotification.classList.remove('hidden');

  setTimeout(() => {
    xpNotification.classList.add('hidden');
  }, 3000);
}

  
  // Show rank up notification
  function showRankUpNotification(newRank, newRankName) {
      const notificationElement = document.importNode(rankUpNotificationTemplate.content, true).firstElementChild;
      notificationElement.querySelector('.new-rank-number').textContent = newRank;
      notificationElement.querySelector('.new-rank-name').textContent = newRankName;
      
      chatMessages.appendChild(notificationElement);
      
      // Scroll to show the notification
      chatMessages.scrollTop = chatMessages.scrollHeight;
  }

 function setupQuizInteraction(quizElement, quizText) {
  const lines = quizText.split('\n');

  // Extract the answer line and remove it
  const answerLineIndex = lines.findIndex(line => line.toLowerCase().startsWith("answer:"));
  const correctAnswer = answerLineIndex !== -1
    ? lines[answerLineIndex].replace(/answer:/i, "").trim().toLowerCase()
    : null;

  if (!correctAnswer) return;

  // Remove the answer and options lines from visible content
  const cleanedLines = lines
    .filter(line => 
      !line.toLowerCase().startsWith("answer:") &&
      !line.toLowerCase().startsWith("options:") &&
      !/^[a-d]\)/i.test(line.trim())
    );

  const messageContent = quizElement.querySelector('.message-content');
  messageContent.innerHTML = parseMarkdown(cleanedLines.join('\n'));

  // Render the answer buttons
  const optionLines = lines.filter(line => /^[a-d]\)/i.test(line.trim()));

  optionLines.forEach(line => {
    const btn = document.createElement('button');
    btn.className = 'quiz-option';
    btn.textContent = line.trim();
    btn.addEventListener('click', () => {
      handleQuizAnswer(line.trim().toLowerCase(), correctAnswer, btn);
    });
    messageContent.appendChild(btn);
  });
  // Add "I don't want to answer" button
const skipBtn = document.createElement('button');
skipBtn.className = 'quiz-option skip-button';
skipBtn.textContent = "I don't want to answer";
skipBtn.addEventListener('click', () => {
  // Disable all quiz buttons
  const allButtons = messageContent.querySelectorAll('button.quiz-option');
  allButtons.forEach(btn => btn.disabled = true);
});
messageContent.appendChild(skipBtn);

}


async function handleQuizAnswer(selected, correct, button) {
  try {
    const response = await fetch(`${API_URL}/quiz`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ answer: selected, correct_answer: correct })
    });

    const data = await response.json();

    const allButtons = button.parentElement.querySelectorAll('button');

    if (data.correct) {
      showXpNotification(data.xp_gained);
      button.classList.add("correct");
    } else {
      showXpNotification(data.xp_gained);
      button.classList.add("incorrect");

      // Highlight the correct button
      allButtons.forEach(btn => {
        if (btn.textContent.trim().toLowerCase() === correct) {
          btn.classList.add("correct");
        }
      });
    }

    // Update user info if needed
    if (data.user) {
      const oldRank = userData.rank;
      userData = data.user;
      updateUserInfoDisplay();

      if (userData.rank > oldRank) {
        showRankUpNotification(userData.rank, userData.rank_name);
      }
    }

    // Disable all buttons
    allButtons.forEach(btn => btn.disabled = true);

  } catch (error) {
    console.error("Quiz answer error:", error);
  }
}



  
  // Initialize the app
  init();
});