[app]
# Название приложения
title = Прокат машинок

# Уникальный идентификатор
package.name = carrental
package.domain = org.example

# Исходный код
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json

# Версия
version = 1.0.0

# Требуемые библиотеки
requirements = python3,kivy

# Ориентация экрана
orientation = portrait

# Полноэкранный режим
fullscreen = 0

# Разрешения
android.permissions = INTERNET

# Указываем версии (опционально)
android.api = 33
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
