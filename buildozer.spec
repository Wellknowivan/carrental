[app]
# Название вашего приложения (как оно будет называться на телефоне)
title = Прокат машинок

# Уникальный идентификатор приложения (можно оставить как есть)
package.name = carrental
package.domain = org.example

# Папка с исходным кодом (текущая папка)
source.dir = .
# Какие расширения файлов включать в сборку
source.include_exts = py,png,jpg,kv,atlas,txt,json

# Версия приложения
version = 1.0.0

# Список необходимых библиотек (вам нужен только kivy)
requirements = python3,kivy

# Ориентация экрана (ваше приложение вертикальное)
orientation = portrait

# Отключаем полноэкранный режим, чтобы видеть строку состояния
fullscreen = 0

# (Опционально) Добавьте эти строки, если будете собирать через WSL
# android.accept_sdk_license = True
# android.api = 33

[buildozer]
log_level = 2