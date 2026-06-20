[app]

title = Melona Wallet
package.name = melonawallet
package.domain = org.melona

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas

requirements = python3==3.11.0,kivy==2.2.1,Pillow==10.0.0

version = 1.0.0

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

icon.filename = melona_logo.png
presplash.filename = melona_logo.png

android.api = 33
android.minapi = 21
android.ndk = 25b
android.buildtools = 33.0.2
android.targetapi = 33

android.orientation = portrait
fullscreen = 0
android.keep_screen_on = 0

android.logcat_filters = *:S python:D
android.logcat_python_only = 1
android.accept_sdk_license = True

android.multiple_screens = True
android.window_background_color = #000000

android.app_name = Melona Wallet
android.icon = melona_logo.png
android.presplash = melona_logo.png
