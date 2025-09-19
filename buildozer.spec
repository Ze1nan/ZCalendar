[app]
title = ZCalendar
package.name = zcalendar
package.domain = org.zcalendar

author = © Zeinan
version = 0.4

source.dir = src
source.include_exts = py,png,jpg,kv,atlas,ttf,otf
requirements = python3,kivy,kivymd,kivy_garden.matplotlib,matplotlib,setuptools,pillow

presplash.filename = assets/presplash.png
icon.filename = assets/icon.png

orientation = portrait
fullscreen = 1

osx.python_version = 3
osx.kivy_version = 2.3.1

android.presplash_color = #FFFFFF
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 0
warn_on_root = 0