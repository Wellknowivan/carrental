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

# УБРАЛ устаревшие параметры android.api, android.sdk, android.ndk
# Вместо них p4a (python-for-android) сам выберет подходящие версии

# Разрешения
android.permissions = INTERNET

# Иконка (если есть)
# icon.filename = %(source.dir)s/icon.png

# Заставка (если есть)
# presplash.filename = %(source.dir)s/splash.png

[buildozer]
log_level = 2
warn_on_root = 1
