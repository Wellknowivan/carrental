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

# Настройки Android
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

# Разрешения
android.permissions = INTERNET

# Иконка (если есть)
# icon.filename = %(source.dir)s/icon.png

# Заставка (если есть)
# presplash.filename = %(source.dir)s/splash.png

[buildozer]
log_level = 2
warn_on_root = 1
