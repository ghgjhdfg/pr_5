import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os
import time

@pytest.fixture(scope="function")
def driver(request):
    """Фикстура для создания и закрытия браузера"""
    chrome_options = Options()
    
    # Для CI/автоматизации - без графического интерфейса (раскомментировать если нужно)
    # chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-extensions")
    
    # Для отладки
    chrome_options.add_experimental_option("detach", False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Открываем приложение
    app_path = "file:///" + os.path.abspath("../index.html").replace("\\", "/")
    driver.get(app_path)
    time.sleep(1)
    
    yield driver
    
    # Закрываем браузер
    driver.quit()

@pytest.fixture
def test_results():
    """Фикстура для сбора результатов"""
    return []

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook для обработки результатов тестов"""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        item.test_status = "PASSED" if rep.passed else "FAILED"