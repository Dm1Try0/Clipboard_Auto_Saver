import os
import re

# Имена файлов для сравнения
OLD_FILE = "ContactsOLD.txt"
NEW_FILE = "Contacts.txt"

# Признаки почтовых доменов для фильтрации
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
    # Проверяем наличие файлов на диске
    if not os.path.exists(OLD_FILE):
        print(f"Ошибка: Старый файл '{OLD_FILE}' не найден.")
        print(f"Создайте файл '{OLD_FILE}' с вашей базой старых контактов для сравнения.")
        input("\nНажмите Enter для выхода...")
        return

    if not os.path.exists(NEW_FILE):
        print(f"Ошибка: Новый файл '{NEW_FILE}' не найден.")
        print(f"Поместите новые данные в файл '{NEW_FILE}'.")
        input("\nНажмите Enter для выхода...")
        return

    print("Считывание и нормализация базы старых контактов...")
    old_contacts = set()
    with open(OLD_FILE, "r", encoding="utf-8") as f:
        for line in f:
            clean = line.strip()
            if clean:
                normalized = normalize_contact(clean)
                old_contacts.add(normalized.lower()) # Сохраняем в нижнем регистре для точного сравнения

    print("Считывание и нормализация новых контактов...")
    new_contacts = []
    seen_new = set() # Чтобы отфильтровать дубли внутри самого нового файла
    
    with open(NEW_FILE, "r", encoding="utf-8") as f:
        for line in f:
            clean = line.strip()
            if clean:
                normalized = normalize_contact(clean)
                # Убираем дубликаты внутри нового файла на лету
                if normalized.lower() not in seen_new:
                    new_contacts.append(normalized)
                    seen_new.add(normalized.lower())

    original_new_count = len(new_contacts)

    # Оставляем только те новые контакты, которых нет в старой базе
    filtered_contacts = [contact for contact in new_contacts if contact.lower() not in old_contacts]
    
    removed_count = original_new_count - len(filtered_contacts)

    # Перезаписываем Contacts.txt отфильтрованными и нормализованными данными
    with open(NEW_FILE, "w", encoding="utf-8") as f_out:
        for contact in filtered_contacts:
            f_out.write(contact + "\n")

    # Выводим отчет в консоль
    print("\n" + "="*45)
    print("=== ОТЧЕТ СРАВНЕНИЯ И ОЧИСТКИ ===")
    print("="*45)
    print(f"База старых записей ({OLD_FILE}): {len(old_contacts)}")
    print(f"Уникальных новых записей:           {original_new_count}")
    print(f"Найдено совпадений (удалено):       {removed_count}")
    print(f"Осталось чистых новых контактов:    {len(filtered_contacts)}")
    print("-" * 45)
    print(f"Файл '{NEW_FILE}' успешно нормализован и обновлен!")
    print("="*45)

    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()
