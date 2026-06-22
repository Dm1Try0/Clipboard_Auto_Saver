import time
import sys
import winsound

try:
    import pyperclip
except ImportError:
    print("Необходимая библиотека не установлена.")
    print("Установите ее командой: pip install pyperclip")
    sys.exit(1)

# Имя файла для сохранения (сформируется при запуске)
OUTPUT_FILE = ""

# Переменная для предотвращения сохранения пустых или дублирующих записей подряд
last_saved_text = None

# Настройка сохранения временных меток (будет задана при запуске)
save_timestamps = True

# Настройка воспроизведения звука (будет задана при запуске)
enable_sound = True

def check_clipboard():
    global last_saved_text, save_timestamps, OUTPUT_FILE, enable_sound
    try:
        # Получаем текст из буфера обмена
        text = pyperclip.paste()
        
        # Если буфер пуст или содержит не текстовые данные
        if not text or text.strip() == "":
            return

        # Если текст совпадает с последним сохраненным, ничего не делаем
        if text == last_saved_text:
            return

        # Записываем в файл в режиме добавления (utf-8)
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            if save_timestamps:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"=== {timestamp} ===\n")
                f.write(text.strip())
                f.write("\n\n") # Разделитель между записями
                print(f"[{timestamp}] Автосохранение (с датой): {text[:50].strip()}...")
            else:
                f.write(text.strip() + "\n")
                print(f"Автосохранение (только текст): {text[:50].strip()}...")
            
        last_saved_text = text
        
        # Короткий и тихий "клик" для подтверждения автосохранения
        if enable_sound:
            winsound.Beep(600, 60)
        
    except Exception as e:
        # Игнорируем временные ошибки блокировки буфера другими программами
        pass

def main():
    global save_timestamps, OUTPUT_FILE, enable_sound
    
    # Формируем уникальное имя файла для этой сессии
    start_time_str = time.strftime("%Y-%m-%d_%H-%M-%S")
    OUTPUT_FILE = f"Saved_{start_time_str}.txt"
    
    print("=== НАСТРОЙКА АВТОСОХРАНЕНИЯ ===")
    choice_time = input("Добавлять дату и разделители к записям? (y/n, по умолчанию 'y'): ").strip().lower()
    save_timestamps = (choice_time != 'n')
    
    choice_sound = input("Включить звуковой сигнал при сохранении? (y/n, по умолчанию 'y'): ").strip().lower()
    enable_sound = (choice_sound != 'n')
    
    print("\n" + "="*45)
    print(f"=== Автоматический мониторинг буфера обмена ===")
    print(f"Режим сохранения: {'С ДАТОЙ И ВРЕМЕНЕМ' if save_timestamps else 'ТОЛЬКО ЧИСТЫЙ ТЕКСТ'}")
    print(f"Звуковой сигнал:  {'ВКЛЮЧЕН' if enable_sound else 'ВЫКЛЮЧЕН'}")
    print(f"Файл сессии:      {OUTPUT_FILE}")
    print(f"Как использовать: Просто копируйте текст (Ctrl+C или ПКМ).")
    print(f"Скрипт сам сохранит каждый новый уникальный фрагмент.")
    print(f"Для выхода закройте это окно или нажмите Ctrl+C здесь.\n")
    
    # Инициализируем стартовое значение буфера, чтобы не сохранять то,
    # что уже лежало в буфере до запуска скрипта
    try:
        last_saved_text = pyperclip.paste()
    except Exception:
        last_saved_text = ""
        
    # Запуск бесконечного цикла опроса буфера обмена раз в 0.6 секунд
    try:
        while True:
            check_clipboard()
            time.sleep(0.6) # Задержка в 0.6 секунды между проверками
    except KeyboardInterrupt:
        print("\nМониторинг остановлен.")

if __name__ == "__main__":
    main()
