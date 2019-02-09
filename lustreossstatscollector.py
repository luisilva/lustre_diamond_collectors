#!/usr/bin/python

"""
lustreossstatscollector.py
A script that get the oss counter information from
lctl get_param obdfilter and block read/write
stats from /proc/fs/lustre/obdfilter/*/brw_stats
in order graph it out on graphite
"""

import os
import logging
import diamond.collector
from subprocess import Popen, PIPE


class LustreossStatsCollector(diamond.collector.Collector):
    def collect(self):
        odbfilter = '/usr/sbin/lctl list_param obdfilter.*.stats'
        brw_cmd = 'tail -n11 /proc/fs/lustre/obdfilter/*/brw_stats'
        lctl_cmd = odbfilter.split(" ")
        try:
            odbfilter = Popen(lctl_cmd, stdout=PIPE, stderr=PIPE)
            odbfilter_out, odbfilter_err = odbfilter.communicate()
            if not odbfilter_out and not odbfilter_err:
                self.log.debug("no output or error for lctl command")
            elif not odbfilter_out:
                self.log.debug("no output for lctl command")
            elif odbfilter_err.rstrip():
                self.log.critical("lclt command error: %s" % odbfilter_err)
        except OSError, e:
            self.log.critical("OSError: %s" % e)

        for ost in odbfilter_out.splitlines():
            get_param = "lctl get_param %s" % ost
            get_param_cmd = get_param.split()
            self.log.debug("passing ost parms: %s" % get_param_cmd)
            try:
                ost_stats = Popen(get_param_cmd, stdout=PIPE, stderr=PIPE)
                ost_stat_out, ost_stat_err = ost_stats.communicate()
            except OSError, e:
                self.log.critical("OSError: %s" % e)
            ost_name = ost.split('.')[1].split('-')[1]
            for line in ost_stat_out.splitlines():
                if "read_bytes" in line:
                    bytes_metric = "%s.read_bytes" % ost_name
                    bytes_value = line.split()[1]
                    self.publish(bytes_metric, bytes_value)
                    io_metric = "%s.read_io" % ost_name
                    io_value = line.split()[6]
                    self.publish(io_metric, io_value)
                elif "write_bytes" in line:
                    bytes_metric = "%s.write_bytes" % ost_name
                    bytes_value = line.split()[1]
                    self.publish(bytes_metric, bytes_value)
                    io_metric = "%s.write_io" % ost_name
                    io_value = line.split()[6]
                    self.publish(io_metric, io_value)
        try:
            brw = Popen(brw_cmd, shell=True, stdout=PIPE, stderr=PIPE)
            brw_out, brw_err = brw.communicate()
            if not brw_out and not brw_err:
                self.log.debug("no output or error for lctl command")
            elif not brw_out:
                self.log.debug("no output for lctl command")
            elif brw_err.rstrip():
                self.log.critical("lclt command error: %s" % brw_err)
            ost_stats = {}
            for line in brw_out.splitlines():
                if '==>' in line:
                    heading = line.split("/")[5].split("-")[1] \
                        + "." + line.split("/")[6].strip("<==").strip()
                else:
                    heading = next(os.walk('/proc/fs/lustre/obdfilter/.')
                                   )[1][0].split('-')[1] + '.brw_stats'
                if 'read' in line and 'write' in line:
                    continue
                if '4K:' in line:
                    read_key = heading+'_read_4k'
                    write_key = heading+'_write_4k'
                    ost_stats[read_key] = int(line.split()[1])
                    ost_stats[write_key] = int(line.split()[5])
                if '8K:' in line:
                    read_key = heading+'_read_8k'
                    write_key = heading+'_write_8k'
                    ost_stats[read_key] = int(line.split()[1])
                    ost_stats[write_key] = int(line.split()[5])
                if '16K:' in line:
                    read_key = heading+'_read_16k'
                    write_key = heading+'_write_16k'
                    ost_stats[read_key] = int(line.split()[1])
                    ost_stats[write_key] = int(line.split()[5])
                if '32K:' in line:
                    read_key = heading+'_read_32k'
                    write_key = heading+'_write_32k'
                    ost_stats[read_key] = int(line.split()[1])
                    ost_stats[write_key] = int(line.split()[5])
                if '64K:' in line:
                    read_key = heading+'_read_64k'
                    write_key = heading+'_write_64k'
                    ost_stats[read_key] = int(line.split()[1])
                    ost_stats[write_key] = int(line.split()[5])
                if '128K:' in line:
                    read_key = heading+'_read_128k'
                    write_key = heading+'_write_128k'
                    ost_stats[read_key] = int(line.split()[1])
                    ost_stats[write_key] = int(line.split()[5])
                if '256K:' in line:
                    read_key = heading+'_read_256k'
                    write_key = heading+'_write_256k'
                    ost_stats[read_key] = int(line.split()[1])
                    ost_stats[write_key] = int(line.split()[5])
                if '512K:' in line:
                    read_key = heading+'_read_512k'
                    write_key = heading+'_write_512k'
                    ost_stats[read_key] = int(line.split()[1])
                    ost_stats[write_key] = int(line.split()[5])
                if '1M:' in line:
                    read_key = heading+'_read_1M'
                    write_key = heading+'_write_1M'
                    ost_stats[read_key] = int(line.split()[1])
                    ost_stats[write_key] = int(line.split()[5])
        except OSError, e:
            logger.critical("OSError: %s" % e)

        for metric, value in ost_stats.iteritems():
            self.publish(metric, value)
