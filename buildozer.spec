[app]

# (str) Title of your application
title = Melona Wallet

# (str) Package name
package.name = melonawallet

# (str) Package domain (needed for android/ios packaging)
package.domain = org.melona

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (do not include any folder)
source.include_exts = py,png,jpg,jpeg,kv,atlas

# (list) Application requirements
requirements = python3,kivy,pillow

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (str) Icon of the application
icon.filename = melona_logo.png

# (str) Presplash of the application
presplash.filename = melona_logo.png

# (str) Android API to use (Android version)
android.api = 33

# (str) Minimum Android API
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (str) Screen orientation
android.orientation = portrait

# (bool) Enable/disable Android fullscreen
fullscreen = 0

# (bool) Enable/disable Android keep screen on
android.keep_screen_on = 0
