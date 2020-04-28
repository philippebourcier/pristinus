#!/bin/bash

# pre-flight checks
mkdir -p /opt/pristinus/data
chmod 775 /opt/pristinus/data
chgrp www-data /opt/pristinus/data

# closed source thing
if [ -d /opt/pristinus/ledskipper ]; then
  nohup /opt/pristinus/ledskipper/launch.sh &>/dev/null &
  nohup /opt/pristinus/ledskipper/launch-ctrl.sh &>/dev/null &
fi

# this software
/opt/pristinus/pristinus.py -d &>/var/log/pristinus.log &
/opt/pristinus/pristinus-relayd.py -d &>/var/log/pristinus-relayd.log &

