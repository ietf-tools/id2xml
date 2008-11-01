#!/bin/bash
cd /usr/IETF/output/
mv wgchairs wgchairs.yesterday
wget http://www2.ietf.org/MAILING-LISTS/wgchairs
/usr/local/mailman/bin/remove_members --all -n -N wgchairs
/usr/local/mailman/bin/add_members -a n -r /usr/IETF/output/wgchairs wgchairs
