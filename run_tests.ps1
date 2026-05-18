<#
.SYNOPSIS
    Запуск автоматических тестов для Генератора случайного обеда
.DESCRIPTION
    Скрипт устанавливает зависимости, запускает тесты и открывает отчёт
#>

param(
    [switch]$NoReport,
    [switch]$InstallDeps
)

$ErrorActionPreference = "Continue"

# Цвета для вывода
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Cyan = "Cyan"

Write-Host "========================================" -ForegroundColor $Cyan
Write-Host "   Генератор случайного обеда - Тесты   " -ForegroundColor $Cyan
Write-Host "========================================" -ForegroundColor $Cyan

# Получаем путь к папке скрипта
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "`n[1/4] Проверка Python..." -ForegroundColor $Yellow

# Проверка наличия Python
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python не найден"
    }
    Write-Host "✅ $pythonVersion" -ForegroundColor $Green
} catch {
    Write-Host "❌ Python не установлен! Установите Python с python.org" -ForegroundColor $Red
    exit 1
}

# Установка зависимостей
if ($InstallDeps) {
    Write-Host "`n[2/4] Установка зависимостей..." -ForegroundColor $Yellow
    python -m pip install selenium webdriver-manager pytest pytest-html --quiet
    Write-Host "✅ Зависимости установлены" -ForegroundColor $Green
} else {
    Write-Host "`n[2/4] Пропуск установки зависимостей (используйте -InstallDeps для установки)" -ForegroundColor $Yellow
}

# Проверка наличия index.html
Write-Host "`n[3/4] Проверка приложения..." -ForegroundColor $Yellow

if (-not (Test-Path "index.html")) {
    Write-Host "❌ index.html не найден в текущей папке!" -ForegroundColor $Red
    Write-Host "Текущая папка: $ScriptDir" -ForegroundColor $Red
    exit 1
}
Write-Host "✅ index.html найден" -ForegroundColor $Green

# Проверка наличия папки tests
if (-not (Test-Path "tests")) {
    Write-Host "❌ Папка 'tests' не найдена!" -ForegroundColor $Red
    Write-Host "Создайте папку tests и поместите туда test_lunch_generator.py" -ForegroundColor $Yellow
    exit 1
}

# Запуск тестов
Write-Host "`n[4/4] Запуск тестов..." -ForegroundColor $Yellow
Write-Host "----------------------------------------" -ForegroundColor $Cyan

# Переход в папку tests
Push-Location "tests"

# Запуск pytest
pytest test_lunch_generator.py -v --tb=short --html=../report.html --self-contained-html 2>&1

$testExitCode = $LASTEXITCODE

# Возврат в исходную папку
Pop-Location

# Открытие отчёта
if ($NoReport -eq $false) {
    if (Test-Path "report.html") {
        Write-Host "`n📊 Открытие отчёта..." -ForegroundColor $Cyan
        Start-Process "report.html"
    } else {
        Write-Host "`n⚠️ Отчёт не найден: report.html" -ForegroundColor $Yellow
    }
}

# Вывод результата
Write-Host "`n========================================" -ForegroundColor $Cyan
if ($testExitCode -eq 0) {
    Write-Host "✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!" -ForegroundColor $Green
} else {
    Write-Host "❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ" -ForegroundColor $Red
    Write-Host "Проверьте отчёт: report.html" -ForegroundColor $Yellow
}
Write-Host "========================================" -ForegroundColor $Cyan

exit $testExitCode