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
requirements = python3==3.11.0,kivy==2.3.0,Pillow==10.4.0

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

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Android logcat only display python log
android.logcat_python_only = 1

# (bool) Whether to accept any SDK/NDK licenses automatically
android.accept_sdk_license = True

# (str) Android build tools version
android.buildtools = 33.0.2

# (str) The target Android API
android.targetapi = 33

# (str) The Android app name
android.app_name = Melona Wallet

# (str) The Android app icon
android.icon = melona_logo.png

# (str) The Android app presplash
android.presplash = melona_logo.png

# (bool) Enable/disable Android support for multiple screens
android.multiple_screens = True

# (str) The Android window background color
android.window_background_color = #000000
