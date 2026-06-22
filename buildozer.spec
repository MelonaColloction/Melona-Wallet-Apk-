[app]

title = Melona Wallet
package.name = melonawallet
package.domain = org.melona

version = 1.0.0

# ✅ این خط رو اضافه کن یا عوض کن
requirements = python3==3.11.0,kivy==2.2.1,pillow

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

icon.filename = melona_logo.png
presplash.filename = melona_logo.png

android.api = 33
android.minapi = 21
android.ndk = 25b

android.orientation = portrait

source.include_exts = py,png,jpg,jpeg,kv,atlas

fullscreen = 0
