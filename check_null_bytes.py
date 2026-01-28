# import os

# def clean_file(filepath):
#     """Очистить файл от null байтов"""
#     try:
#         with open(filepath, 'rb') as f:
#             content = f.read()
        
#         # Удалить BOM (Byte Order Mark) и null байты
#         if content.startswith(b'\xff\xfe'):  # UTF-16 LE BOM
#             # Конвертировать из UTF-16 в UTF-8
#             try:
#                 text = content.decode('utf-16-le')
#                 clean_content = text.encode('utf-8')
#             except:
#                 # Если не получается декодировать, просто удалить null байты
#                 clean_content = content.replace(b'\x00', b'')
#         else:
#             # Просто удалить null байты
#             clean_content = content.replace(b'\x00', b'')
        
#         # Сохранить очищенный файл
#         with open(filepath, 'wb') as f:
#             f.write(clean_content)
        
#         print(f"✅ Исправлен: {filepath}")
#         return True
        
#     except Exception as e:
#         print(f"❌ Ошибка при обработке {filepath}: {e}")
#         return False

# # Файлы для исправления
# files_to_fix = [
#     'apps/accounts/urls.py',
#     'apps/accounts/views.py', 
#     'apps/accounts/__init__.py',
#     'apps/accounts/apps.py',  # тоже проверьте
#     'apps/accounts/models.py',  # тоже проверьте
# ]

# print("Исправление файлов с null байтами...")
# print("=" * 50)

# for file in files_to_fix:
#     if os.path.exists(file):
#         clean_file(file)
#     else:
#         print(f"⚠️ Файл не найден: {file}")

# print("=" * 50)
# print("Готово!")

# import os
# import sys

# def find_null_bytes_in_py_files(directory):
#     """Найти все .py файлы с null байтами"""
#     print(f"🔍 Поиск файлов с null байтами в: {directory}")
#     print("-" * 50)
    
#     found_problems = False
    
#     for root, dirs, files in os.walk(directory):
#         # Пропустить виртуальное окружение и другие ненужные папки
#         if 'venv' in root or '__pycache__' in root or '.git' in root:
#             continue
            
#         for file in files:
#             if file.endswith('.py'):
#                 filepath = os.path.join(root, file)
#                 try:
#                     with open(filepath, 'rb') as f:
#                         content = f.read()
#                         if b'\x00' in content:
#                             found_problems = True
#                             print(f"🚨 НАЙДЕНО: {filepath}")
                            
#                             # Посчитать количество null байтов
#                             null_count = content.count(b'\x00')
#                             print(f"   Количество null байтов: {null_count}")
                            
#                             # Показать строки с проблемами
#                             lines = content.split(b'\n')
#                             for i, line in enumerate(lines, 1):
#                                 if b'\x00' in line:
#                                     # Заменить null байты для отображения
#                                     display_line = line.replace(b'\x00', b'[NULL]')
#                                     # Обрезать длинные строки
#                                     if len(display_line) > 100:
#                                         display_line = display_line[:100] + b'...'
#                                     print(f"   Строка {i}: {display_line}")
                            
#                             print()  # Пустая строка между файлами
                            
#                 except Exception as e:
#                     print(f"⚠️ Ошибка при чтении {filepath}: {e}")
    
#     if not found_problems:
#         print("✅ Файлов с null байтами не найдено!")
#     else:
#         print("\n💡 Рекомендации:")
#         print("1. Создайте резервные копии проблемных файлов")
#         print("2. Откройте файлы в Notepad++ или VS Code")
#         print("3. Сохраните заново с кодировкой UTF-8")
#         print("4. Или удалите и создайте файлы заново")

# def check_specific_file(filepath):
#     """Проверить конкретный файл"""
#     print(f"🔍 Проверка файла: {filepath}")
#     try:
#         with open(filepath, 'rb') as f:
#             content = f.read()
            
#         if b'\x00' in content:
#             print(f"🚨 Файл содержит null байты!")
            
#             # Показать содержимое вокруг null байтов
#             null_positions = []
#             pos = content.find(b'\x00')
#             while pos != -1:
#                 null_positions.append(pos)
#                 pos = content.find(b'\x00', pos + 1)
            
#             print(f"   Всего null байтов: {len(null_positions)}")
#             print(f"   Позиции: {null_positions[:10]}")  # Показать первые 10
            
#             # Показать контекст
#             for pos in null_positions[:5]:  # Показать первые 5
#                 start = max(0, pos - 20)
#                 end = min(len(content), pos + 20)
#                 context = content[start:end]
#                 display = context.replace(b'\x00', b'[NULL]')
#                 print(f"   Позиция {pos}: ...{display}...")
                
#         else:
#             print("✅ Файл не содержит null байтов")
            
#     except FileNotFoundError:
#         print(f"❌ Файл не найден: {filepath}")
#     except Exception as e:
#         print(f"⚠️ Ошибка: {e}")

# if __name__ == "__main__":
#     print("=" * 60)
#     print("ПРОВЕРКА NULL БАЙТОВ В ПРОЕКТЕ")
#     print("=" * 60)
    
#     # Проверить весь проект
#     find_null_bytes_in_py_files('.')
    
#     print("\n" + "=" * 60)
#     print("ДОПОЛНИТЕЛЬНЫЕ ПРОВЕРКИ")
#     print("=" * 60)
    
#     # Проверить важные файлы
#     important_files = [
#         'config/__init__.py',
#         'config/settings.py',
#         'manage.py',
#         'menu/apps.py',
#         'orders/apps.py'
#     ]
    
#     for file in important_files:
#         if os.path.exists(file):
#             check_specific_file(file)
#             print()
import os
import shutil

def clean_file(filepath):
    """Очистить файл от null байтов"""
    try:
        # Создать backup
        backup_path = filepath + '.backup'
        shutil.copy2(filepath, backup_path)
        
        # Прочитать и очистить
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Удалить null байты
        clean_content = content.replace(b'\x00', b'')
        
        # Сохранить
        with open(filepath, 'wb') as f:
            f.write(clean_content)
        
        print(f"✅ Очищен: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка с {filepath}: {e}")
        return False

# Файлы, которые точно нужно проверить
files_to_check = [
    'config/urls.py',
    'config/settings.py',
    'config/__init__.py',
    'manage.py',
    
    # Приложения
    'apps/accounts/urls.py',
    'apps/accounts/views.py',
    'apps/accounts/__init__.py',
    'apps/accounts/apps.py',
    'apps/accounts/models.py',
    
    'apps/menu/urls.py',
    'apps/menu/views.py',
    'apps/menu/__init__.py',
    'apps/menu/apps.py',
    
    'apps/orders/urls.py',
    'apps/orders/views.py',
    'apps/orders/__init__.py',
    'apps/orders/apps.py',
    
    'apps/qr_code/urls.py',
    'apps/qr_code/views.py',
    'apps/qr_code/__init__.py',
    'apps/qr_code/apps.py',
    
    'apps/restaurants/urls.py',
    'apps/restaurants/views.py',
    'apps/restaurants/__init__.py',
    'apps/restaurants/apps.py',
]

print("Очистка файлов от null байтов...")
print("=" * 60)

for file in files_to_check:
    if os.path.exists(file):
        clean_file(file)
    else:
        print(f"⚠️ Файл не существует: {file}")

print("=" * 60)
print("Готово! Созданы backup файлы с расширением .backup")