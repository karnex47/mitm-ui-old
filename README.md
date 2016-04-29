# mitm-ui
A GUI implemented with PyQt4 for libmproxy. It does not have all the features of mitmproxy. I built it with fiddler web debugger in mind. The auro responder of fiddler helped me a lot when web developing. Since I didn't find anything thats fiddler-like on OSX, I decided to build one.

# Developement
requirements:
libmproxy, PyQt4/sip

I have setup a virtual env for those to libraires and commited them, Will remove them later

# Build
Have a setup.py and build.sh to be used for py2app. Currently the deployment build is breaking with "Abort trap: 6", but that maybe just my system.
