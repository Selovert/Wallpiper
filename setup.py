"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup
from os import listdir

APP = ['Wallpiper.py']
DATA_FILES = [
  'Settings.xib',
  'Resources/wallpiper.png',
  'Resources/wallpiper@2x.png',
  'Resources/wallpiper-dl.png',
  'Resources/wallpiper-dl@2x.png',
  'Resources/wallpiper-dc.png',
  'Resources/wallpiper-dc@2x.png',
  'Resources/wallpiper-gray.png',
  'Resources/wallpiper-gray@2x.png',
  'Resources/wallpiper-alert.png',
  'Resources/wallpiper-alert@2x.png',
]

for image in listdir('Resources/pipe'):
  DATA_FILES.append('Resources/pipe/' + image)

plist=dict(
        LSUIElement=True,
        NSUserNotificationAlertStyle='banner',
        CFBundleName='Wallpiper',
        CFBundleVersion='0.5.6',
        CFBundleIdentifier='selovert.wallpiper',
        CFBundleSignature='SBLM',
        NSHumanReadableCopyright="Don't steal this code, please.",
        CFBundleGetInfoString='Wallpiper: it downloads wallpapers from somewhere mystical!',
    )
OPTIONS = {
  'iconfile':'Resources/wallpiper.icns',
  'plist': plist
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
