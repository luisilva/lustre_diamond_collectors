#!/usr/bin/python

"""
lustremdsstatscollector.py
A script that get the mdt counter information from /proc
in order graph it out on graphite
"""

import os
import sys
import psutil
import logging
import diamond.collector
from subprocess import Popen, PIPE


class LustremdsStatsCollector(diamond.collector.Collector):
    def collect(self):
        """
        Check that mds is designated Controler
        else don't run.
        """
        local_mounts = psutil.disk_partitions()
        MDT_mount = False
        for mount in local_mounts:
            if mount.fstype == 'lustre' and 'mdt' in mount.mountpoint.lower():
                self.log.debug("%s => %s" % (mount.fstype, mount.mountpoint))
                MDT_mount = True
        if  not MDT_mount:
            sys.exit()
        """
        Read mdt stats in and publish them out
        """
        metric_type = 'GAUGE'
        mdt_root_dir = '/proc/fs/lustre/mdt/'
        try:
            mdt_location = os.listdir(mdt_root_dir)
        except IOError, e:
            self.log.debug("No mdt on this host: %s" % e)
            sys.exit()
        for mdt in mdt_location:
            if mdt == 'num_refs':
                continue
            else:
                file_path = "/proc/fs/lustre/mdt/%s/md_stats" % mdt
                with open(file_path) as f:
                    contents = f.readlines()
                    for line in contents:
                        if 'snapshot_time' in line:
                            continue
                        key = str(line.split()[0])
                        value = int(line.split()[1])
                        self.log.debug("publishing: %s => %s" % (key, value))
                        self.publish(key, value, metric_type=metric_type)
