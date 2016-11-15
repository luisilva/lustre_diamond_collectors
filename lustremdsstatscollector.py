#!/usr/bin/python

"""
lustremdsstatscollector.py
A script that get the mdt counter information from /proc
in order graph it out on graphite
"""

import os
import logging
import diamond.collector



class LustreMdsStatsCollector(diamond.collector.Collector):
    def collect(self):
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
        mdt_location.remove('num_refs')
        for mdt in mdt_location:
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
