#!/usr/bin/env bash
rm -rf build dist
./env/bin/python setup.py py2app --no-strip --packages=PyQt4 >> build.log
./dist/MitmUI.app/Contents/MacOS/MitmUI