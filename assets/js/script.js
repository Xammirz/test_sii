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

let selectedSity = null;
console.log(data);
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
    const dealersHtml = cityDealers.map((dealer , id) => `
      <div class="dealer" data-id=${id}>
        <h2>${dealer.name}</h2>
        <p>${dealer.address}</p>
        <p><button>Чек-Лист</button></p>
      </div>
    `).join('');


    // Вставляем HTML-код в нужное место на странице
    const dealersListContainer = document.getElementById('dealers-list-container');
	const dealersContainer = document.querySelector('.dealers_container');
	dealersContainer.innerHTML = `${dealersHtml}`;

    // Скрываем блок выбора города
    citySelection.style.display = 'none';

    // Показываем список дилеров
    dealersListContainer.style.display = 'flex'; // delete

    // Добавляем обработчик клика на кнопку "назад"
    const backToCitiesBtn = document.getElementById('back-to-cities');
    backToCitiesBtn.addEventListener('click', () => {
      // Отображаем блок выбора города
      citySelection.style.display = 'flex';
      // Скрываем список дилеров
      dealersListContainer.style.display = 'none';
    });
renderChecklist();
  });
});

function renderChecklist(){
	console.log(data);
	const dealerIcons = document.querySelectorAll('.dealer');
	let currentDealer = null;
	dealerIcons.forEach(icon => {
		icon.addEventListener('click', () => {
		// Получаем идентификаторы города и дилера
		const dealerId = icon.getAttribute('data-id');

		currentDealer = data.dealers[selectedSity];
		currentDealer = currentDealer[dealerId]
		console.log(currentDealer);
	
		// Формируем HTML-код для чеклиста выбранного дилера
		const checklistHtml = currentDealer.checklist.map((item , id) => `
		<li><input type="checkbox" id="${id}"><label for="${id}">${item}</label></li>
		`).join('');
		// Вставляем HTML-код в нужное место на странице
		const dealerChecklistContainer = document.getElementById('dealer-checklist-container');
		dealerChecklistContainer.innerHTML = `
		  <h2>${currentDealer.name}</h2>
		  <p>${currentDealer.address}</p>
		  <ul>
			${checklistHtml}
		  </ul>
		  <button id="back-to-dealers">Back to dealers</button>
		`;
		// Скрываем список дилеров
		dealersListContainer.style.display = 'none';
	
		// Показываем чеклист выбранного дилера
		dealerChecklistContainer.style.display = 'block';
	
		// Добавляем обработчик клика на кнопку "назад"
		const backToDealersBtn = document.getElementById('back-to-dealers');
		backToDealersBtn.addEventListener('click', () => {
		  // Отображаем список дилеров
		  dealersListContainer.style.display = 'block';
		  // Скрываем чеклист выбранного дилера
		  dealerChecklistContainer.style.display = 'none';
		});
	  });
	});
}
// При загрузке страницы отображаем список городов
// citySelection.style.display = 'block';
const dealersListContainer = document.getElementById('dealers-list-container');
dealersListContainer.style.display = 'none';

// Добавляем обработчик клика на каждого дилера в выбранном городе

  })
  .catch(error => console.error(error));