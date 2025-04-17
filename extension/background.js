// Обработчик сообщений
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'generateCitation') {
    handleCitationGeneration(request, sendResponse);
    return true; // Необходимо для асинхронного ответа
  }
  
  if (request.action === 'showResult') {
    chrome.action.setPopup({
      tabId: sender.tab.id,
      popup: `popup/popup.html?citation=${encodeURIComponent(request.citation)}`
    });
    chrome.action.openPopup();
  }
});

async function handleCitationGeneration(request, sendResponse) {
  try {
    const response = await fetch('http://localhost:8000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        html: request.html,
        url: request.url,
        saveToBibliography: request.saveToBibliography
      })
    });
    const data = await response.json();
    sendResponse(data);
  } catch (error) {
    sendResponse({ error: error.message });
  }
}