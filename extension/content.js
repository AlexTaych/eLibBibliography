console.log("Content script loaded!");  // Первая строка в файле

// Создаем и добавляем кнопку на страницу
const citeBtn = document.createElement('img');
citeBtn.id = 'elibraryCiteBtn';
citeBtn.src = chrome.runtime.getURL('assets/images/cite-button.png');
citeBtn.alt = 'Cite';

// Стилизация кнопки с полным размером иконки
Object.assign(citeBtn.style, {
  position: 'fixed',
  top: '20px',
  right: '20px',
  zIndex: '9999',
  objectFit: 'contain',
  cursor: 'pointer',
  transition: 'transform 0.2s',
  filter: 'drop-shadow(0 2px 4px rgba(242, 108, 79, 0.3))',
  border: 'none',
  background: 'transparent'
});

citeBtn.addEventListener('mouseenter', () => {
  citeBtn.style.transform = 'translateY(-2px)';
  citeBtn.style.filter = 'drop-shadow(0 4px 8px rgba(242, 108, 79, 0.4))';
});

citeBtn.addEventListener('mouseleave', () => {
  citeBtn.style.transform = 'translateY(0)';
  citeBtn.style.filter = 'drop-shadow(0 2px 4px rgba(242, 108, 79, 0.3))';
});

citeBtn.addEventListener('click', async () => {
  try {
    const loader = document.createElement('div');
    Object.assign(loader.style, {
      position: 'fixed',
      top: '90px',
      right: '30px',
      width: '30px',
      height: '30px',
      border: '3px solid rgba(242, 108, 79, 0.3)',
      borderTopColor: '#F26C4F',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite',
      zIndex: '9999'
    });
    document.body.appendChild(loader);
    
    const html = document.documentElement.outerHTML;
    const url = window.location.href;
    
    // Получаем сохраненное состояние чекбокса
    const { saveToBibliography = false } = await chrome.storage.local.get('saveToBibliography');
    
    const response = await chrome.runtime.sendMessage({
      action: 'generateCitation',
      html: html,
      url: url,
      saveToBibliography: saveToBibliography  // Передаем текущее состояние
    });
    
    chrome.runtime.sendMessage({
      action: 'showResult',
      citation: response.citation
    });
    
    document.body.removeChild(loader);
  } catch (error) {
    console.error('Ошибка:', error);
  }
});

// Добавляем стиль для анимации
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(style);

document.body.appendChild(citeBtn);