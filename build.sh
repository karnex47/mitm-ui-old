#!/usr/bin/env bash
rm -rf build dist
./env/bin/python setup.py py2app -A --no-strip --packages=PyQt4
./dist/main.app/Contents/MacOS/main