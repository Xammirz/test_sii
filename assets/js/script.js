// Загрузка данных из JSON-файла
fetch('data/data.json')
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

// Формируем HTML-код для списка дилеров первого города
const firstCityDealersHtml = data.dealers[data.cities[0].id].map(dealer => `
  <div class="dealer">
    <h2>${dealer.name}</h2>
    <p>${dealer.address}</p>
  </div>
`).join('');

// Отображаем список городов на странице
const citySelection = document.getElementById('city-selection');
citySelection.innerHTML = citiesHtml;

// Добавляем обработчик клика на каждую иконку города
const cityIcons = document.querySelectorAll('.city');
cityIcons.forEach(icon => {
  icon.addEventListener('click', () => {
    // Получаем значение атрибута data-city у нажатой иконки
    const cityId = icon.getAttribute('data-city');

    // Формируем HTML-код для списка дилеров выбранного города
    const dealersHtml = data.dealers[cityId].map(dealer => `
      <div class="dealer">
        <h2>${dealer.name}</h2>
        <p>${dealer.address}</p>
      </div>
    `).join('');

    // Вставляем HTML-код в нужное место на странице
    const dealersListContainer = document.getElementById('dealers-list-container');
    dealersListContainer.innerHTML = `
      <button id="back-to-cities">Back to cities</button>
      ${dealersHtml}
    `;

    // Скрываем блок выбора города
    citySelection.style.display = 'none';

    // Показываем список дилеров
    dealersListContainer.style.display = 'block';

    // Добавляем обработчик клика на кнопку "назад"
    const backToCitiesBtn = document.getElementById('back-to-cities');
    backToCitiesBtn.addEventListener('click', () => {
      // Отображаем блок выбора города
      citySelection.style.display = 'block';
      // Скрываем список дилеров
      dealersListContainer.style.display = 'none';
    });
  });
});

// При загрузке страницы отображаем список городов
citySelection.style.display = 'block';
const dealersListContainer = document.getElementById('dealers-list-container');
dealersListContainer.style.display = 'none';

  })
  .catch(error => console.error(error));