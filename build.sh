#!/usr/bin/env bash
rm -rf build dist
./env/bin/python setup.py py2app --no-strip -A --packages=PyQt4
cp -a assets ./dist/MitmUI.app/Contents/Resources/
cp config.ini ./dist/MitmUI.app/Contents/Resources/
./dist/MitmUI.app/Contents/MacOS/MitmUI
