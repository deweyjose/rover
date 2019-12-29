#!/bin/sh

# Crash Avoid
echo installing crashavoid into bin
cp crashavoid/dist/Release/GNU-Linux/crashavoid bin/

# Crash Avoid Service
echo installing Crash Avoid Service
cp -u services/crashavoid /etc/init.d/crashavoid
chmod +x /etc/init.d/crashavoid
chown root:root /etc/init.d/crashavoid
#update-rc.d crashavoid defaults
#update-rc.d crashavoid enable
