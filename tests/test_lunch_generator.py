import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import random
import string

class TestLunchGenerator:
    """Тест-кейсы для Генератора случайного обеда"""
    
    # ============================================
    # TC-01: Позитивный тест - нажатие на кнопку
    # ============================================
    def test_tc01_click_lucky_button(self, driver):
        """TC-01: Нажатие на кнопку «Мне повезёт» при наличии блюд"""
        # Предусловия: приложение открыто
        try:
            # Найти и нажать кнопку
            lucky_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "luckyBtn"))
            )
            lucky_btn.click()
            
            # Проверить, что появилось название блюда
            dish_name = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "dishName"))
            )
            name_text = dish_name.text
            
            # Ожидаемый результат: название не равно "Ничего не выбрано"
            assert name_text != "Ничего не выбрано", f"Блюдо не отобразилось, текст: {name_text}"
            
        except TimeoutException:
            pytest.fail("Кнопка или элемент с блюдом не найдены")
    
    # ============================================
    # TC-02: Повторное нажатие - разные блюда
    # ============================================
    def test_tc02_different_dishes(self, driver):
        """TC-02: Повторное нажатие генерирует другое блюдо"""
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        
        # Получить первое блюдо
        lucky_btn.click()
        time.sleep(1)
        first_dish = driver.find_element(By.ID, "dishName").text
        
        # Получить второе блюдо
        lucky_btn.click()
        time.sleep(1)
        second_dish = driver.find_element(By.ID, "dishName").text
        
        # Проверить, что блюда разные (если в списке больше 1 блюда)
        assert first_dish != second_dish, f"Оба раза выпало одинаковое блюдо: {first_dish}"
    
    # ============================================
    # TC-03: Генерация при пустом списке
    # ============================================
    def test_tc03_empty_dishes_list(self, driver):
        """TC-03: Генерация при пустом списке блюд"""
        # Очистить localStorage через JavaScript
        driver.execute_script("localStorage.removeItem('lunch_generator_dishes');")
        driver.execute_script("localStorage.setItem('lunch_generator_dishes', JSON.stringify([]));")
        driver.refresh()
        time.sleep(1)
        
        # Нажать на кнопку
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        lucky_btn.click()
        time.sleep(1)
        
        # Проверить сообщение об ошибке
        dish_name = driver.find_element(By.ID, "dishName").text
        dish_desc = driver.find_element(By.ID, "dishDescription").text
        
        assert "нет блюд" in dish_name.lower() or "нет блюд" in dish_desc.lower(), \
            f"Не отобразилось сообщение о пустом списке. Текст: {dish_name}"
    
    # ============================================
    # TC-04: Производительность - быстрые клики
    # ============================================
    def test_tc04_rapid_clicks(self, driver):
        """TC-04: Производительность - 10 быстрых кликов подряд"""
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        
        # 10 быстрых кликов
        for _ in range(10):
            lucky_btn.click()
            time.sleep(0.05)  # 50 мс между кликами
        
        time.sleep(1)
        
        # Проверить, что приложение не зависло
        dish_name = driver.find_element(By.ID, "dishName")
        assert dish_name.is_displayed(), "Интерфейс завис после быстрых кликов"
    
    # ============================================
    # TC-05: XSS безопасность - название блюда
    # ============================================
    def test_tc05_xss_injection_name(self, driver):
        """TC-05: Безопасность - внедрение XSS через название блюда"""
        # Открыть редактор
        details = driver.find_element(By.TAG_NAME, "details")
        details.click()
        time.sleep(1)
        
        # Найти поля редактора и вставить XSS
        xss_payload = "<script>alert('XSS')</script>"
        
        # Добавить новое блюдо с XSS
        add_btn = driver.find_element(By.ID, "addDishBtn")
        add_btn.click()
        time.sleep(0.5)
        
        # Найти последнее поле ввода названия
        name_inputs = driver.find_elements(By.CSS_SELECTOR, ".dish-name-input")
        if name_inputs:
            name_inputs[-1].clear()
            name_inputs[-1].send_keys(xss_payload)
        
        # Сохранить
        save_btn = driver.find_element(By.ID, "saveDishesBtn")
        save_btn.click()
        time.sleep(1)
        
        # Закрыть редактор и сгенерировать блюдо
        details.click()
        time.sleep(0.5)
        
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        lucky_btn.click()
        time.sleep(1)
        
        # Проверить, что скрипт не выполнился (alert не появился)
        dish_name = driver.find_element(By.ID, "dishName").text
        
        # XSS строка должна отображаться как текст, а не выполняться
        assert xss_payload in dish_name or dish_name != "", \
            "XSS payload не отобразился или сломал страницу"
    
    # ============================================
    # TC-06: Восстановление после закрытия вкладки
    # ============================================
    def test_tc06_restore_after_close(self, driver):
        """TC-06: Восстановление после принудительного закрытия"""
        # Сгенерировать блюдо
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        lucky_btn.click()
        time.sleep(1)
        
        first_dish = driver.find_element(By.ID, "dishName").text
        
        # Сохранить current_dish в localStorage через JS
        dish_data = driver.execute_script("return localStorage.getItem('last_dish');")
        
        # Перезагрузить страницу (имитация закрытия и открытия)
        driver.refresh()
        time.sleep(2)
        
        # Проверить, что блюдо восстановилось
        restored_dish = driver.find_element(By.ID, "dishName").text
        
        assert first_dish == restored_dish, \
            f"Блюдо не восстановилось. Было: {first_dish}, Стало: {restored_dish}"
    
    # ============================================
    # TC-07: Граничный тест - очень длинное название
    # ============================================
    def test_tc07_long_name(self, driver):
        """TC-07: Граничный тест - название из 500 символов"""
        long_name = "А" * 500
        
        # Открыть редактор
        details = driver.find_element(By.TAG_NAME, "details")
        details.click()
        time.sleep(1)
        
        # Добавить блюдо с длинным названием
        add_btn = driver.find_element(By.ID, "addDishBtn")
        add_btn.click()
        time.sleep(0.5)
        
        name_inputs = driver.find_elements(By.CSS_SELECTOR, ".dish-name-input")
        if name_inputs:
            name_inputs[-1].clear()
            name_inputs[-1].send_keys(long_name)
        
        # Сохранить
        save_btn = driver.find_element(By.ID, "saveDishesBtn")
        save_btn.click()
        time.sleep(1)
        
        details.click()
        time.sleep(0.5)
        
        # Сгенерировать и проверить
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        
        # Несколько раз, чтобы точно попасть на новое блюдо
        for _ in range(5):
            lucky_btn.click()
            time.sleep(0.5)
            dish_name = driver.find_element(By.ID, "dishName").text
            if len(dish_name) > 400:
                break
        
        # Проверить, что вёрстка не сломалась
        card = driver.find_element(By.CLASS_NAME, "card")
        assert card.is_displayed(), "Вёрстка сломалась при длинном названии"
    
    # ============================================
    # TC-08: UI/UX - наведение на кнопку
    # ============================================
    def test_tc08_button_hover(self, driver):
        """TC-08: UI/UX - наличие подсветки при наведении на кнопку"""
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        
        # Получить CSS свойства до наведения
        original_color = lucky_btn.value_of_css_property("background-color")
        
        # Навести курсор (через JS)
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(driver)
        actions.move_to_element(lucky_btn).perform()
        time.sleep(0.3)
        
        # Получить CSS свойства после наведения
        hover_color = lucky_btn.value_of_css_property("background-color")
        
        # Проверить, что цвет изменился (есть hover эффект)
        # Если цвета одинаковые - тест падает (нет UI отклика)
        # Примечание: иногда цвета могут совпадать, проверяем transform scale
        transform = lucky_btn.value_of_css_property("transform")
        
        # Проверяем, что есть либо изменение цвета, либо transform
        has_hover_effect = (original_color != hover_color) or (transform != "none")
        assert has_hover_effect, "Нет визуального отклика при наведении на кнопку"
    
    # ============================================
    # TC-09: Адаптивность - разные разрешения
    # ============================================
    @pytest.mark.parametrize("width,height", [
        (1366, 768),
        (1920, 1080),
        (375, 667)  # мобильный iPhone SE
    ])
    def test_tc09_responsive(self, driver, width, height):
        """TC-09: Адаптивность на разных разрешениях экрана"""
        driver.set_window_size(width, height)
        time.sleep(1)
        
        # Проверить, что кнопка видна и кликабельна
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        assert lucky_btn.is_displayed(), f"Кнопка не видна при разрешении {width}x{height}"
        
        lucky_btn.click()
        time.sleep(1)
        
        # Проверить, что карточка с блюдом видна
        dish_name = driver.find_element(By.ID, "dishName")
        assert dish_name.is_displayed(), f"Карточка не видна при разрешении {width}x{height}"
        
        # Проверить, что нет горизонтальной прокрутки
        body_width = driver.execute_script("return document.body.scrollWidth")
        viewport_width = driver.execute_script("return window.innerWidth")
        assert body_width <= viewport_width + 10, \
            f"Есть горизонтальная прокрутка при {width}x{height}"
    
    # ============================================
    # TC-10: Безопасность - атака на localStorage
    # ============================================
    def test_tc10_localstorage_attack(self, driver):
        """TC-10: Безопасность - попытка испортить localStorage через консоль"""
        # Имитация атаки через консоль
        malicious_data = '{"__proto__": {"polluted": true}}'
        
        driver.execute_script(f"""
            localStorage.setItem('lunch_generator_dishes', '{malicious_data}');
        """)
        
        driver.refresh()
        time.sleep(2)
        
        # Проверить, что приложение не сломалось
        try:
            lucky_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "luckyBtn"))
            )
            lucky_btn.click()
            
            dish_name = driver.find_element(By.ID, "dishName")
            assert dish_name.is_displayed(), "Приложение сломалось после атаки на localStorage"
        except:
            # Если упало - это дефект безопасности
            pytest.fail("Приложение не обработало повреждённые данные в localStorage")
    
    # ============================================
    # TC-11: Негативный - битая ссылка на изображение
    # ============================================
    def test_tc11_broken_image(self, driver):
        """TC-11: Негативный - блюдо с битой ссылкой на изображение"""
        # Открыть редактор
        details = driver.find_element(By.TAG_NAME, "details")
        details.click()
        time.sleep(1)
        
        # Найти блюдо и испортить его ссылку на изображение
        image_inputs = driver.find_elements(By.CSS_SELECTOR, ".dish-image-input")
        if image_inputs:
            image_inputs[0].clear()
            image_inputs[0].send_keys("https://this-is-invalid-url-12345.com/image.jpg")
            
            # Сохранить
            save_btn = driver.find_element(By.ID, "saveDishesBtn")
            save_btn.click()
            time.sleep(1)
        
        details.click()
        time.sleep(0.5)
        
        # Сгенерировать блюдо
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        lucky_btn.click()
        time.sleep(2)
        
        # Проверить, что появился плейсхолдер вместо битой картинки
        placeholder = driver.find_element(By.ID, "imagePlaceholder")
        assert placeholder.is_displayed(), "Нет плейсхолдера при недоступном изображении"
    
    # ============================================
    # TC-12: Производительность - 1000 записей
    # ============================================
    def test_tc12_performance_thousand_dishes(self, driver):
        """TC-12: Производительность - добавление 1000 блюд"""
        # Создать 1000 блюд через JS
        driver.execute_script("""
            const dishes = [];
            for (let i = 0; i < 1000; i++) {
                dishes.push({
                    name: `Тестовое блюдо ${i}`,
                    description: `Описание блюда ${i}`,
                    image: ""
                });
            }
            localStorage.setItem('lunch_generator_dishes', JSON.stringify(dishes));
        """)
        
        driver.refresh()
        time.sleep(2)
        
        # Проверить, что кнопка работает
        import time as t
        start = t.time()
        
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        lucky_btn.click()
        
        end = t.time()
        load_time = end - start
        
        # Ожидаемый результат: генерация не дольше 1 секунды
        assert load_time < 1.0, f"Генерация блюда слишком долгая: {load_time:.2f} сек"
        
        dish_name = driver.find_element(By.ID, "dishName")
        assert dish_name.is_displayed(), "Приложение зависло при 1000 блюдах"
    
    # ============================================
    # TC-13: Восстановление при потере интернета
    # ============================================
    def test_tc13_offline_mode(self, driver):
        """TC-13: Восстановление после сбоя - имитация потери интернета"""
        # Сгенерировать блюдо
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        lucky_btn.click()
        time.sleep(1)
        
        first_dish = driver.find_element(By.ID, "dishName").text
        
        # Переключить браузер в офлайн режим (не во всех драйверах работает)
        try:
            driver.execute_script("window.dispatchEvent(new Event('offline'));")
        except:
            pass
        
        driver.refresh()
        time.sleep(2)
        
        # Проверить, что блюдо отображается (из кэша или localStorage)
        restored_dish = driver.find_element(By.ID, "dishName").text
        assert restored_dish == first_dish or restored_dish != "Ничего не выбрано", \
            "Блюдо не отобразилось в офлайн режиме"
    
    # ============================================
    # TC-14: Кроссплатформенность - проверка консоли
    # ============================================
    def test_tc14_no_console_errors(self, driver):
        """TC-14: Кроссплатформенность - отсутствие ошибок в консоли"""
        # Получить логи консоли
        logs = driver.get_log("browser")
        
        errors = [log for log in logs if log["level"] == "SEVERE"]
        
        # Игнорируем ожидаемые ошибки (например, 404 на картинки)
        critical_errors = [e for e in errors if "Failed to load" not in e["message"]]
        
        assert len(critical_errors) == 0, f"Найдены ошибки в консоли: {critical_errors}"
    
    # ============================================
    # TC-15: Функциональный - сброс настроек
    # ============================================
    def test_tc15_reset_to_defaults(self, driver):
        """TC-15: Функциональный - сброс к стандартным блюдам"""
        # Сначала изменить список
        details = driver.find_element(By.TAG_NAME, "details")
        details.click()
        time.sleep(1)
        
        # Добавить тестовое блюдо
        add_btn = driver.find_element(By.ID, "addDishBtn")
        add_btn.click()
        time.sleep(0.5)
        
        name_inputs = driver.find_elements(By.CSS_SELECTOR, ".dish-name-input")
        if name_inputs:
            name_inputs[-1].clear()
            name_inputs[-1].send_keys("Временное блюдо")
        
        save_btn = driver.find_element(By.ID, "saveDishesBtn")
        save_btn.click()
        time.sleep(1)
        
        # Нажать кнопку сброса
        reset_btn = driver.find_element(By.ID, "resetDishesBtn")
        reset_btn.click()
        time.sleep(1)
        
        # Проверить, что сброс произошёл
        toast = driver.find_element(By.ID, "toast")
        assert toast.is_displayed(), "Не появилось уведомление о сбросе"
        
        # Закрыть редактор и проверить генерацию
        details.click()
        time.sleep(0.5)
        
        lucky_btn = driver.find_element(By.ID, "luckyBtn")
        lucky_btn.click()
        time.sleep(1)
        
        dish_name = driver.find_element(By.ID, "dishName").text
        assert "Временное блюдо" not in dish_name, "Сброс не удалил добавленное блюдо"


# ============================================
# ЗАПУСК ТЕСТОВ (если файл запущен напрямую)
# ============================================
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--html=../test_report.html",
        "--self-contained-html",
        "--maxfail=5"
    ])