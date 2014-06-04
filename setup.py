"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['Wallpiper.py']
DATA_FILES = ['Settings.xib','Resources/wallpiper.png','Resources/wallpiper-dl.png','Resources/wallpiper-dc.png','Resources/wallpiper-gray.png','Resources/wallpiper-alert.png']
plist=dict(
        LSUIElement=True,
        CFBundleName='Wallpiper',
        CFBundleVersion='0.5.5',
        CFBundleIdentifier='selovert.wallpiper',
        CFBundleSignature='SBLM',
        NSHumanReadableCopyright="Don't steal this code, please. ",
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
