#!/bin/sh

# Python
echo installing Python scripts into bin
cp -u python/*.py bin/
cp -ur python/templates bin/
cp -ur python/static bin/

# Crash Avoid
echo installing crashavoid into bin
cp crashavoid/dist/Release/GNU-Linux/crashavoid bin/

# Drive Control Service
echo installing Drive Control Service
cp -u services/drivecontrol /etc/init.d/drivecontrol
chmod +x /etc/init.d/drivecontrol
chown root:root /etc/init.d/drivecontrol
update-rc.d drivecontrol defaults
update-rc.d drivecontrol enable

# Drive Control UI Service
echo installing Drive Control UI Service
cp -u services/drivecontrolui /etc/init.d/drivecontrolui
chmod +x /etc/init.d/drivecontrolui
chown root:root /etc/init.d/drivecontrolui
#update-rc.d drivecontrolui defaults
#update-rc.d drivecontrolui enable

# Crash Avoid Service
echo installing Crash Avoid Service
cp -u services/crashavoid /etc/init.d/crashavoid
chmod +x /etc/init.d/crashavoid
chown root:root /etc/init.d/crashavoid
#update-rc.d crashavoid defaults
#update-rc.d crashavoid enable
