// ==========================================================================
// ENTERPRISE FAQ PORTAL CONTROLLER (TABS, SEARCH INDEX, BOT FRAMEWORK)
// ==========================================================================

// Global state
let faqDatabase = [];
let activeCategory = 'All';
let currentConfigType = ''; // 'app' or 'bot'

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  loadFaqData();
  setupSearchListeners();
  loadSavedConnections();
});

// 1. Sidebar Tab Navigation
function initNavigation() {
  const navButtons = document.querySelectorAll('.nav-btn');
  
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });
}

function switchTab(tabId) {
  // Update sidebar buttons
  const navButtons = document.querySelectorAll('.nav-btn');
  navButtons.forEach(b => {
    if (b.getAttribute('data-tab') === tabId) {
      b.classList.add('active');
    } else {
      b.classList.remove('active');
    }
  });

  // Toggle tab panels
  const panes = document.querySelectorAll('.tab-pane');
  panes.forEach(pane => {
    if (pane.id === `tab-${tabId}`) {
      pane.classList.add('active');
    } else {
      pane.classList.remove('active');
    }
  });

  // Specific tab loads
  if (tabId === 'powerapp') {
    loadPowerApp();
  } else if (tabId === 'copilot') {
    loadCopilotBot();
  }
}

// 2. Fetch and Render Local FAQ Data
async function loadFaqData() {
  const listContainer = document.getElementById('faq-results-list');
  try {
    const response = await fetch('sample_faqs.json');
    if (!response.ok) throw new Error('Failed to fetch JSON database');
    faqDatabase = await response.json();
    renderFaqs(faqDatabase);
  } catch (err) {
    console.error('Error loading FAQ data:', err);
    if (listContainer) {
      listContainer.innerHTML = `<div class="loading-spinner" style="color:var(--color-error)">
        <i class="fa-solid fa-triangle-exclamation"></i> Error loading FAQ database.
      </div>`;
    }
  }
}

function renderFaqs(items) {
  const listContainer = document.getElementById('faq-results-list');
  if (!listContainer) return;

  if (items.length === 0) {
    listContainer.innerHTML = `<div class="loading-spinner">No FAQ records found matching that query.</div>`;
    return;
  }

  listContainer.innerHTML = items.map(faq => `
    <div class="faq-card" id="faq-${faq.FAQID}">
      <div class="faq-card-header">
        <h3>${faq.Question}</h3>
        <span class="category-tag">${faq.Category}</span>
      </div>
      <div class="faq-card-body">
        ${faq.Answer}
      </div>
      <div class="faq-card-footer">
        <span>Tags: ${faq.Tags.replace(/;/g, ' ')}</span>
        <span>Priority: ${faq.Priority}</span>
      </div>
    </div>
  `).join('');
}

// 3. Search Indexing and Filtering
function setupSearchListeners() {
  const globalSearch = document.getElementById('global-search');
  const categoryPills = document.querySelectorAll('.filter-pill');

  // Text search handler
  if (globalSearch) {
    globalSearch.addEventListener('input', (e) => {
      filterAndSearch(e.target.value, activeCategory);
    });
  }

  // Category filter pills
  categoryPills.forEach(pill => {
    pill.addEventListener('click', () => {
      categoryPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      
      activeCategory = pill.getAttribute('data-category');
      const query = globalSearch ? globalSearch.value : '';
      filterAndSearch(query, activeCategory);
    });
  });
}

function filterAndSearch(query, category) {
  let results = faqDatabase;

  // Filter by category
  if (category !== 'All') {
    results = results.filter(item => item.Category === category);
  }

  // Filter by search query
  if (query.trim() !== '') {
    const term = query.toLowerCase();
    results = results.filter(item => 
      item.Question.toLowerCase().includes(term) ||
      item.Answer.toLowerCase().includes(term) ||
      item.Keywords.toLowerCase().includes(term) ||
      item.Tags.toLowerCase().includes(term)
    );
  }

  renderFaqs(results);
}

// 4. Power Apps Embed Integration
function loadPowerApp() {
  const container = document.getElementById('powerapps-container');
  const savedUrl = localStorage.getItem('powerapps_url');

  if (savedUrl && savedUrl.trim() !== '') {
    container.innerHTML = `
      <iframe src="${savedUrl}" 
              width="100%" 
              height="100%" 
              style="border: none; background: var(--sidebar-bg);" 
              allow="geolocation; microphone; camera">
      </iframe>
    `;
  }
}

// 5. Copilot Studio Webchat Integration
function loadCopilotBot() {
  const container = document.getElementById('webchat-container');
  const secretOrToken = localStorage.getItem('copilot_secret');

  if (secretOrToken && secretOrToken.trim() !== '') {
    container.innerHTML = `<div id="webchat" role="main"></div>`;
    
    // Check if configuration looks like a Direct Line secret or token URL
    let directLineConfig = {};
    if (secretOrToken.startsWith('http')) {
      // Dynamic token URL retrieval (production pattern)
      fetch(secretOrToken)
        .then(res => res.json())
        .then(data => {
          window.WebChat.renderWebChat({
            directLine: window.WebChat.createDirectLine({ token: data.token }),
            locale: 'en-US'
          }, document.getElementById('webchat'));
        })
        .catch(err => {
          container.innerHTML = `<div class="loading-spinner" style="color:var(--color-error)">
            <i class="fa-solid fa-triangle-exclamation"></i> Error fetching Bot Token. Please check URL configuration.
          </div>`;
        });
    } else {
      // Straight Secret key mapping (sandbox pattern)
      window.WebChat.renderWebChat({
        directLine: window.WebChat.createDirectLine({ secret: secretOrToken }),
        locale: 'en-US'
      }, document.getElementById('webchat'));
    }
  }
}

// 6. Local Configuration Modal Functions
function showConfigPrompt(type) {
  currentConfigType = type;
  const modal = document.getElementById('config-modal');
  const title = document.getElementById('modal-title');
  const label = document.getElementById('input-label');
  const input = document.getElementById('config-value');

  if (type === 'app') {
    title.innerText = 'Configure Power Apps IFrame Connection';
    label.innerText = 'Power Apps Play Web Link (e.g., https://apps.powerapps.com/play/...)';
    input.value = localStorage.getItem('powerapps_url') || '';
  } else if (type === 'bot') {
    title.innerText = 'Configure Copilot Studio Connection';
    label.innerText = 'Direct Line Secret Key OR Token API Endpoint';
    input.value = localStorage.getItem('copilot_secret') || '';
  }

  if (modal) modal.classList.add('active');
}

function closeModal() {
  const modal = document.getElementById('config-modal');
  if (modal) modal.classList.remove('active');
}

function saveConnectionConfig() {
  const inputVal = document.getElementById('config-value').value;
  
  if (currentConfigType === 'app') {
    localStorage.setItem('powerapps_url', inputVal);
    loadPowerApp();
  } else if (currentConfigType === 'bot') {
    localStorage.setItem('copilot_secret', inputVal);
    loadCopilotBot();
  }

  closeModal();
}

function loadSavedConnections() {
  // If keys already exist, clear placeholder text immediately on screen visibility
  const savedApp = localStorage.getItem('powerapps_url');
  const savedBot = localStorage.getItem('copilot_secret');

  if (savedApp) loadPowerApp();
  if (savedBot) loadCopilotBot();
}
