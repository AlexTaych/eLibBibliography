document.addEventListener('DOMContentLoaded', async () => {
  const citationResult = document.getElementById('citationResult');
  const copyBtn = document.getElementById('copyBtn');
  const clearBtn = document.getElementById('clearBtn');
  const saveCheckbox = document.getElementById('saveCheckbox');
  
  // Загружаем сохраненное состояние чекбокса (по умолчанию false)
  const { saveToBibliography = false } = await chrome.storage.local.get('saveToBibliography');
  saveCheckbox.checked = saveToBibliography;
  
  // Сохраняем состояние при изменении чекбокса
  saveCheckbox.addEventListener('change', async () => {
    await chrome.storage.local.set({ saveToBibliography: saveCheckbox.checked });
  });

  // Получаем цитату из URL
  const urlParams = new URLSearchParams(window.location.search);
  const citation = urlParams.get('citation');
  
  if (citation) {
    citationResult.textContent = decodeURIComponent(citation);
  } else {
    citationResult.textContent = 'Ошибка: не удалось получить данные';
    citationResult.classList.add('error');
  }
  
  // Кнопка копирования (без изменений)
  copyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(citationResult.textContent);
    } catch (err) {
      console.error('Ошибка копирования:', err);
    }
  });
  
  // Кнопка очистки библиографии (без изменений)
  clearBtn.addEventListener('click', async () => {
    try {
      const response = await fetch('http://localhost:8000/clean', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await response.json();
      if (data.success) {
        citationResult.textContent = 'Библиография очищена';
      }
    } catch (error) {
      console.error('Ошибка при очистке библиографии:', error);
      citationResult.textContent = 'Ошибка при очистке библиографии';
    }
  });
});