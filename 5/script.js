// Стандартный набор блюд
const DEFAULT_DISHES = [
    {
        name: "🍝 Спагетти Карбонара",
        description: "Классическая итальянская паста с беконом, яйцом и пармезаном",
        image: "https://cdnn21.img.ria.ru/images/07e9/02/0b/1998618624_5:0:1456:816_1920x1080_80_0_0_fd9023dc32c1e49515893197df667e83.jpg"
    },
    {
        name: "🥗 Цезарь с курицей",
        description: "Свежий салат с курицей-гриль, пармезаном и соусом Цезарь",
        image: "https://avatars.mds.yandex.net/i?id=8465a205c6dc1908268dffc4bb9d9cc3_l-5227767-images-thumbs&n=13"
    },
    {
        name: "🍜 Том Ям с креветками",
        description: "Острый тайский суп с креветками, грибами и ароматной зеленью",
        image: "https://avatars.mds.yandex.net/i?id=9578c94c51e5581a2beec59e6244314d_l-10841731-images-thumbs&n=13"
    },
    {
        name: "🍔 Двойной чизбургер",
        description: "Сочная котлета, двойной чеддер, карамелизированный лук и соус барбекю",
        image: "https://i.pinimg.com/originals/53/19/3f/53193f657d64ead03047760a538c7f89.jpg?nii=t"
    },
    {
        name: "🍣 Филадельфия ролл",
        description: "Лосось, сливочный сыр, огурец и авокадо в рисе с нори",
        image: "https://seo.mybox.ru/upload/medialibrary/blog-pictures/rolly-filadelfiya-reczept/rolly-filadelfiya.jpg"
    },
    {
        name: "🥘 Рисотто с грибами",
        description: "Кремовое ризотто с белыми грибами и трюфельным маслом",
        image: "https://avatars.mds.yandex.net/get-vertis-journal/4465444/eb5e2d98-7ee2-4031-a15b-0f86452416cd.jpg/1600x1600"
    },
    {
        name: "🍲 Борщ со сметаной",
        description: "Традиционный украинский борщ с пампушками и чесноком",
        image: "https://cdn.food.ru/unsigned/fit/640/480/ce/0/czM6Ly9tZWRpYS9waWN0dXJlcy8yMDI0MDMzMS9iOU1jZTguanBlZw.jpg"
    },
    {
        name: "🥑 Салат с киноа и авокадо",
        description: "Полезный салат с киноа, авокадо, огурцом и лимонной заправкой",
        image: "https://www.koolinar.ru/all_image/article/6/6683/article-8b9748d0-3bc2-4b0f-a69f-2d4dc318360c_large.jpg"
    }
];

// Ключ для localStorage
const STORAGE_KEY = 'lunch_generator_dishes';

// Глобальные переменные
let dishes = [];
let currentDish = null;

// DOM элементы
const luckyBtn = document.getElementById('luckyBtn');
const dishNameEl = document.getElementById('dishName');
const dishDescriptionEl = document.getElementById('dishDescription');
const dishImageEl = document.getElementById('dishImage');
const imagePlaceholder = document.getElementById('imagePlaceholder');
const dishesEditor = document.getElementById('dishesEditor');
const toast = document.getElementById('toast');

// Загрузка блюд из localStorage или использование стандартных
function loadDishes() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
        try {
            dishes = JSON.parse(stored);
            if (!dishes || dishes.length === 0) {
                dishes = [...DEFAULT_DISHES];
            }
        } catch(e) {
            dishes = [...DEFAULT_DISHES];
        }
    } else {
        dishes = [...DEFAULT_DISHES];
    }
}

// Сохранение блюд в localStorage
function saveDishes() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dishes));
    showToast('Список блюд сохранён!');
    renderEditor();
    
    // Если текущее блюдо было удалено или изменено, обновляем отображение
    if (currentDish) {
        const stillExists = dishes.some(d => d.name === currentDish.name);
        if (!stillExists && dishes.length > 0) {
            generateRandomDish();
        } else if (stillExists) {
            // Обновляем описание на случай изменения
            const updated = dishes.find(d => d.name === currentDish.name);
            if (updated) {
                displayDish(updated);
            }
        }
    }
}

// Отображение блюда на главном экране
function displayDish(dish) {
    currentDish = dish;
    dishNameEl.textContent = dish.name;
    dishDescriptionEl.textContent = dish.description;
    
    // Работа с изображением
    if (dish.image && dish.image.trim() !== '') {
        dishImageEl.src = dish.image;
        dishImageEl.classList.add('loaded');
        dishImageEl.onerror = () => {
            // Если картинка не загрузилась, показываем плейсхолдер
            dishImageEl.classList.remove('loaded');
            imagePlaceholder.style.display = 'flex';
        };
        dishImageEl.onload = () => {
            dishImageEl.classList.add('loaded');
            imagePlaceholder.style.display = 'none';
        };
    } else {
        dishImageEl.classList.remove('loaded');
        imagePlaceholder.style.display = 'flex';
    }
}

// Генерация случайного блюда
function generateRandomDish() {
    if (!dishes || dishes.length === 0) {
        dishNameEl.textContent = '😢 Нет блюд';
        dishDescriptionEl.textContent = 'Добавьте блюда в настройках';
        dishImageEl.classList.remove('loaded');
        imagePlaceholder.style.display = 'flex';
        return;
    }
    
    const randomIndex = Math.floor(Math.random() * dishes.length);
    const selectedDish = dishes[randomIndex];
    displayDish(selectedDish);
}

// Отображение редактора списка блюд
function renderEditor() {
    if (!dishesEditor) return;
    
    dishesEditor.innerHTML = '';
    
    dishes.forEach((dish, index) => {
        const editorItem = document.createElement('div');
        editorItem.className = 'dish-editor-item';
        editorItem.innerHTML = `
            <input type="text" class="dish-name-input" value="${escapeHtml(dish.name)}" placeholder="Название блюда" data-index="${index}" data-field="name">
            <textarea class="dish-desc-input" placeholder="Описание блюда" data-index="${index}" data-field="description">${escapeHtml(dish.description)}</textarea>
            <input type="text" class="dish-image-input" value="${escapeHtml(dish.image || '')}" placeholder="URL изображения" data-index="${index}" data-field="image">
            <button class="remove-dish-btn" data-index="${index}">🗑️ Удалить</button>
        `;
        dishesEditor.appendChild(editorItem);
    });
    
    // Добавляем обработчики для всех полей
    document.querySelectorAll('.dish-name-input, .dish-desc-input, .dish-image-input').forEach(input => {
        input.addEventListener('change', (e) => {
            const index = parseInt(e.target.dataset.index);
            const field = e.target.dataset.field;
            if (!isNaN(index) && dishes[index]) {
                dishes[index][field] = e.target.value;
            }
        });
    });
    
    document.querySelectorAll('.remove-dish-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(btn.dataset.index);
            if (!isNaN(index) && dishes[index]) {
                dishes.splice(index, 1);
                renderEditor();
                if (dishes.length === 0) {
                    dishNameEl.textContent = '🍽️ Нет блюд';
                    dishDescriptionEl.textContent = 'Добавьте блюда в настройках';
                    dishImageEl.classList.remove('loaded');
                    imagePlaceholder.style.display = 'flex';
                } else if (currentDish) {
                    const stillExists = dishes.some(d => d.name === currentDish.name);
                    if (!stillExists) {
                        generateRandomDish();
                    }
                }
            }
        });
    });
}

// Сброс к стандартным блюдам
function resetToDefaults() {
    dishes = JSON.parse(JSON.stringify(DEFAULT_DISHES));
    saveDishes();
    generateRandomDish();
    showToast('Сброшено к стандартным блюдам');
}

// Вспомогательная функция для экранирования HTML
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Показать всплывающее уведомление
function showToast(message) {
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2000);
}

// Восстановление последнего блюда при загрузке
function restoreLastDish() {
    const lastDish = localStorage.getItem('last_dish');
    if (lastDish) {
        try {
            const parsed = JSON.parse(lastDish);
            if (parsed && parsed.name) {
                displayDish(parsed);
                return;
            }
        } catch(e) {}
    }
    // Если нет сохранённого блюда или оно невалидно
    if (dishes.length > 0) {
        generateRandomDish();
    }
}

// Сохранить текущее блюдо перед закрытием
function saveCurrentDish() {
    if (currentDish) {
        localStorage.setItem('last_dish', JSON.stringify(currentDish));
    }
}

// Инициализация приложения
function init() {
    loadDishes();
    restoreLastDish();
    renderEditor();
    
    // Обработчик кнопки "Мне повезёт"
    if (luckyBtn) {
        luckyBtn.addEventListener('click', generateRandomDish);
    }
    
    // Кнопки в редакторе
    const addBtn = document.getElementById('addDishBtn');
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            dishes.push({
                name: 'Новое блюдо',
                description: 'Описание нового блюда',
                image: ''
            });
            renderEditor();
            showToast('Добавлено новое блюдо, нажмите Сохранить');
        });
    }
    
    const saveBtn = document.getElementById('saveDishesBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveDishes);
    }
    
    const resetBtn = document.getElementById('resetDishesBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetToDefaults);
    }
    
    // Сохранение последнего блюда перед уходом со страницы
    window.addEventListener('beforeunload', saveCurrentDish);
}

// Запуск приложения после загрузки DOM
document.addEventListener('DOMContentLoaded', init);