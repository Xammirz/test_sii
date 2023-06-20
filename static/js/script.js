// Загрузка данных из JSON-файла
fetch('static/data/data.json')
  .then(response => response.json())
  .then(data => {
    // Формируем HTML-код для списка городов
    const citiesHtml = data.cities.map(city => `
      <li>
        <a data-city="${city.id}" class="city icon">
          <span class="icon-text">${city.name}</span>
        </a>
      </li>
    `).join('');

    let selectedSity = null;
    let currentDealer = null;

    // Отображаем список городов на странице
    const citySelection = document.getElementById('city-selection');
    citySelection.innerHTML = citiesHtml;

    // Добавляем обработчик клика на каждую иконку города
    const cityIcons = document.querySelectorAll('.city');
    cityIcons.forEach(icon => {
      icon.addEventListener('click', () => {
        // Получаем значение атрибута data-city у нажатой иконки
        const cityId = icon.getAttribute('data-city');
        selectedSity = cityId;

        // Формируем HTML-код для списка дилеров выбранного города
        const cityDealers = data.dealers[cityId];

        const sortedDealers = sortingDealers(cityDealers);
        const cityName = data.cities.find(city => city.id === selectedSity).name;

        const dealersHtml = sortedDealers.map((dealer) => `
          <div class="dealer" data-id=${dealer.id} data-date=${dealer.last_modified}>
            <h2>${dealer.name}</h2>
            <p>${dealer.address}</p>
            <p><button>Чек-Лист</button></p>
          </div>
        `).join('');

        // Вставляем HTML-код в нужное место на странице
        const dealersListContainer = document.getElementById('dealers-list-container');
        const dealersContainer = document.querySelector('.dealers_container');
        dealersContainer.innerHTML = `
          <div class="city-name">${cityName}</div>
            ${dealersHtml}
        `;

        // Скрываем блок выбора города
        citySelection.style.display = 'none';

        // Показываем список дилеров
        dealersListContainer.style.display = 'flex';

        // Добавляем обработчик клика на кнопку "назад"
        const backToCitiesBtn = document.getElementById('back-to-cities');
        backToCitiesBtn.addEventListener('click', () => {
          // Отображаем блок выбора города
          citySelection.style.display = 'flex';
          // Скрываем список дилеров
          dealersListContainer.style.display = 'none';
        });

        renderChecklist();
        checkingDealers();
      });
    });

    // Функция для удаления состояния галочки из базы данных
    function removeChecklistValue(dealerId, itemId) {
      const data = {
        dealerId: dealerId,
        itemId: itemId
      };

      fetch('http://127.0.0.1:8000/remove_checklist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
        .then(response => {
          if (response.ok) {
            console.log('Checklist value removed successfully from the database');
          } else {
            console.error('Failed to remove checklist value from the database');
          }
        })
        .catch(error => {
          console.error('Error:', error);
        });
    }

    function saveChecklistValue(dealerId, itemId) {
      const data = {
        dealerId: dealerId,
        itemId: itemId
      };
    
      fetch('http://127.0.0.1:8000/save_checklist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
        .then(response => {
          if (response.ok) {
            console.log('Checklist value saved successfully');
            completedTasks.push(itemId);
          } else {
            console.error('Failed to save checklist value');
          }
        })
        .catch(error => {
          console.error('Error:', error);
        });
    }

    let completedTasks = []; // Объявление переменной completedTasks

    function renderChecklist() {
      const dealerIcons = document.querySelectorAll('.dealer');
      dealerIcons.forEach(icon => {
        icon.addEventListener('click', () => {
          const dealerId = icon.dataset.id;
          
          currentDealer = data.dealers[selectedSity].find(dealer => dealer.id === dealerId);
          
          const checklistHtml = currentDealer.checklist.map((item, id) => {
            return `
              <li>
                <input type="checkbox" id="checkbox-${id}" data-dealer-id="${dealerId}" data-item-id="${id}">
                <label for="checkbox-${id}">${item}</label>
              </li>
            `;
          }).join('')
    
          const dealerChecklistContainer = document.getElementById('dealer-checklist-container');
          dealerChecklistContainer.innerHTML = `
          <br> 
          <h1 style="color: black">${currentDealer.name}</h1>
          <p>${currentDealer.address}</p>
            <ul>
              ${checklistHtml}
            </ul>
            <button id="back-to-dealers">Назад</button>
          `;
    
          const dealersListContainer = document.getElementById('dealers-list-container');
          dealersListContainer.style.display = 'none';
    
          dealerChecklistContainer.style.display = 'block';
    
          const backToDealersBtn = document.getElementById('back-to-dealers');
          backToDealersBtn.addEventListener('click', () => {
            dealersListContainer.style.display = 'block';
            dealerChecklistContainer.style.display = 'none';
          });
    
          const checklistItems = dealerChecklistContainer.querySelectorAll('input[type="checkbox"]');
          checklistItems.forEach(item => {
            const dealerId = item.getAttribute('data-dealer-id');
            const itemId =item.getAttribute('data-item-id');
            
            // Восстановление состояния галочек из localStorage при загрузке страницы
            const isChecked = localStorage.getItem(`dealer-${dealerId}-item-${itemId}`) === 'true';
            item.checked = isChecked;

            item.addEventListener('change', () => {
              if (item.checked) {
                saveChecklistValue(dealerId, itemId);
                localStorage.setItem(`dealer-${dealerId}-item-${itemId}`, 'true'); // Сохранение состояния галочки в localStorage
              } else {
                removeChecklistValue(dealerId, itemId);
                localStorage.removeItem(`dealer-${dealerId}-item-${itemId}`); // Удаление состояния галочки из localStorage
              }
            });
          });
          
          // Проверяем и удаляем все состояния галочек, которые были установлены за день
          removeCheckboxStatesAtMidnight();
        });
      });
    }
    
    // Функция для удаления всех галочек из localStorage
    function removeCheckboxStatesAtMidnight() {
      const now = new Date();
      const currentHour = now.getUTCHours() + 3; // Московское время (+3 часа от UTC)
      const currentMinute = now.getUTCMinutes();
    
      // Проверяем, если текущее время равно 12:00 AM (00:00) по московскому времени
      if (currentHour === 0 && currentMinute === 0) {
        // Перебираем все ключи в localStorage
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
    
          // Проверяем, является ли ключ состоянием галочки
          if (key.includes('-item-')) {
            localStorage.removeItem(key); // Удаляем состояние галочки из localStorage
          }
        }
      }
    }
    


function checkingDealers() {
  //ПРоверка даты дилеров
  const dealersEl = document.querySelectorAll('.dealer');
  const currentDate = new Date();
  const maxExpireDay = 6;
  dealersEl.forEach((dealer) => {
	//разница даты дилера от текуший даты
    const dealerDate = new Date(...dealer.dataset.date.split('-').reverse());
	dealerDate.setMonth(dealerDate.getMonth() - 1);
    const diffDate = Math.floor(
      (currentDate - dealerDate) / (1000 * 3600 * 24)
    );
	if(diffDate > maxExpireDay){
		//добавим класс expired в зависимости от даты
		dealer.classList.add('expired')
	}
  });
}

function sortingDealers(dealersArr) {
  //Сортировка дилеров
  const dealers = [...dealersArr];
  dealers.sort((first, second) => {
    const firstDate = new Date(
      ...first.last_modified.split('-').reverse()
    ).getTime();
    const secondDate = new Date(
      ...second.last_modified.split('-').reverse()
    ).getTime();
    return  firstDate - secondDate;
  });
  return dealers;
}
// При загрузке страницы отображаем список городов
// citySelection.style.display = 'block';
const dealersListContainer = document.getElementById('dealers-list-container');
dealersListContainer.style.display = 'none';

// Добавляем обработчик клика на каждого дилера в выбранном городе

  })
  .catch(error => console.error(error));