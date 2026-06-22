import os
import re
import time

# Имя входного файла
INPUT_FILE = "Contacts.txt"

# Регулярное выражение для поиска полноценных e-mail адресов
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

# Признаки почтовых доменов для "неполных" записей (например, @gmail, @mail.ru)
MAIL_DOMAINS = ['@gmail', '@mail', '@yandex', '@rambler', '@outlook', '@yahoo', '@proton', '@bk.ru', '@list.ru', '@inbox.ru']

def normalize_contact(line):
    line_strip = line.strip()
    line_lower = line_strip.lower()
    
    if not line_strip:
        return line_strip
        
    # Сразу пропускаем другие контакты, чтобы не сломать их форматирование
    if "@" in line_lower and any(domain in line_lower for domain in MAIL_DOMAINS):
        return line_strip
    if "discord" in line_lower:
        return line_strip
    if "vk.com" in line_lower or "vk.ru" in line_lower:
        return line_strip

    # 1. Поиск веб-версий Telegram с хешем (например, web.telegram.org/k/#@username)
    web_tg_match = re.search(r'telegram\.org/[^\s#?]+/#[@]?([a-zA-Z0-9_]{4,32})', line_strip, re.IGNORECASE)
    if web_tg_match:
        return f"https://t.me/{web_tg_match.group(1)}"
        
    # 2. Поиск стандартных ссылок t.me/username или telegram.me/username
    link_match = re.search(r'(?:t\.me|telegram\.me)/([a-zA-Z0-9_]{4,32})', line_strip, re.IGNORECASE)
    if link_match:
        return f"https://t.me/{link_match.group(1)}"

    # 3. Поиск юзернейма с символом @ (например, "tg - @username" или "тг @username")
    at_match = re.search(r'@([a-zA-Z0-9_]{4,32})', line_strip)
    if at_match:
        # Проверяем, что это не email (простая проверка на отсутствие точки в домене)
        after_at = line_strip.split("@")[-1]
        if not ("." in after_at and len(after_at) < 10):
            return f"https://t.me/{at_match.group(1)}"

    # 4. Префиксы tg/тг с последующим юзернеймом (например, "tg username" или "тг: username")
    prefix_match = re.search(r'\b(?:tg|тг)\b\s*[-:/]*\s*([a-zA-Z0-9_]{4,32})', line_strip, re.IGNORECASE)
    if prefix_match:
        return f"https://t.me/{prefix_match.group(1)}"

    # 5. Если строка начинается с @ и является валидным юзернеймом
    if line_strip.startswith("@"):
        username = line_strip[1:].strip()
        if re.match(r'^[a-zA-Z0-9_]{4,32}$', username):
            return f"https://t.me/{username}"

    # Если это не распознано как Telegram, возвращаем исходную строку
    return line_strip

def main():
    # Проверяем, существует ли входной файл
    if not os.path.exists(INPUT_FILE):
        print(f"Ошибка: Файл '{INPUT_FILE}' не найден.")
        print(f"Пожалуйста, создайте файл '{INPUT_FILE}' в этой папке и поместите туда контакты.")
        input("\nНажмите Enter для выхода...")
        return

    print(f"Чтение контактов из '{INPUT_FILE}'...")

    # Используем множества (set) для автоматического удаления дубликатов
    telegrams = set()
    discords = set()
    mails = set()
    vks = set()
    others = set()

    total_lines_count = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            clean_line = line.strip()
            if not clean_line:
                continue
            
            total_lines_count += 1
            
            # Нормализуем контакт перед определением категории и добавлением
            normalized = normalize_contact(clean_line)

            # 1. Проверяем на принадлежность к почте (Email)
            is_email = EMAIL_PATTERN.search(normalized)
            is_partial_mail = any(domain in normalized.lower() for domain in MAIL_DOMAINS)
            
            if is_email or is_partial_mail:
                mails.add(normalized)
                continue

            # 2. Проверяем Discord
            if "discord.gg" in normalized.lower() or "discord.com" in normalized.lower():
                discords.add(normalized)
                continue

            # 3. Проверяем ВКонтакте (VK)
            if "vk.com" in normalized.lower() or "vk.ru" in normalized.lower():
                vks.add(normalized)
                continue

            # 4. Проверяем Telegram
            # Если строка содержит t.me, telegram.me или начинается с @ (и это не email)
            if "t.me" in normalized.lower() or "telegram.me" in normalized.lower() or normalized.startswith("@"):
                telegrams.add(normalized)
                continue

            # 5. Все остальное
            others.add(normalized)

    # Форматируем текущее время для имени файлов
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

    # Функция для записи результатов в файл
    def write_to_file(filename_prefix, items):
        if not items:
            return None
        filename = f"{filename_prefix}_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as out:
            # Сортируем для удобства чтения
            for item in sorted(items):
                out.write(item + "\n")
        return filename

    # Записываем отсортированные контакты
    tg_file = write_to_file("Telegram", telegrams)
    ds_file = write_to_file("Discord", discords)
    mail_file = write_to_file("Mail", mails)
    vk_file = write_to_file("VK", vks)
    other_file = write_to_file("Others", others)

    # Объединяем все уникальные контакты для перезаписи исходного файла
    all_unique_contacts = sorted(list(telegrams | discords | mails | vks | others))
    
    # Перезаписываем исходный файл Contacts.txt, оставляя только уникальные записи
    with open(INPUT_FILE, "w", encoding="utf-8") as f_out:
        for item in all_unique_contacts:
            f_out.write(item + "\n")

    duplicates_removed = total_lines_count - len(all_unique_contacts)

    # Выводим отчет в консоль
    print("\n" + "="*35)
    print("=== ОТЧЕТ О СОРТИРОВКЕ ===")
    print("="*35)
    print(f"Всего строк обработано: {total_lines_count}")
    print(f"Уникальных контактов:   {len(all_unique_contacts)}")
    print(f"Удалено дубликатов:     {duplicates_removed}")
    print("-"*35)
    
    if tg_file:
        print(f"Telegram:   {len(telegrams)} конт. -> '{tg_file}'")
    if ds_file:
        print(f"Discord:    {len(discords)} конт. -> '{ds_file}'")
    if mail_file:
        print(f"Mail/Email: {len(mails)} конт. -> '{mail_file}'")
    if vk_file:
        print(f"VKontakte:  {len(vks)} конт. -> '{vk_file}'")
    if other_file:
        print(f"Остальное:  {len(others)} конт. -> '{other_file}'")

    print(f"\nИсходный файл '{INPUT_FILE}' успешно нормализован и очищен!")
    print("\nСортировка успешно завершена!")
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()
