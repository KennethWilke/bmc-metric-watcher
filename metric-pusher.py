#!/usr/bin/env python
import socket
import json
import sys
import time
import os


try:
    bmc_id = sys.argv[1]
    endpoint_host = sys.argv[2]
except:
    print 'Usage: {0} <instance name> <funnel host> [port]'.format(sys.argv[0])
    sys.exit(1)

try:
    endpoint_port = sys.argv[3]
except:
    endpoint_port = 1234

print "Pushing data to {0}:{1}".format(endpoint_host, endpoint_port)


version = ''
build = ''

with open('/etc/os-release') as osrelease:
    data = osrelease.read()
    for line in data.split('\n'):
        if line.startswith('VERSION_ID='):
            version = line[len('VERSION_ID='):]
        elif line.startswith('BUILD_ID='):
            build = line[len('BUILD_ID='):]

funnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
funnel.connect((endpoint_host, endpoint_port))

current_time = time.time()

while True:
    metrics = {'time': int(current_time),
               'version': version,
               'build': build,
               'bmc': bmc_id,
               'ctx_switches': 0}

    for procfile in ['loadavg', 'meminfo', 'stat', 'interrupts']:
        with open('/proc/{0}'.format(procfile)) as info:
            metrics[procfile] = info.read()

    # Aggregate context switch count from all the running processes
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    metrics['process_count'] = len(pids)
    for pid in pids:
        try:
            with open('/proc/{0}/status'.format(pid)) as pidstats:
                for line in pidstats.read().split('\n'):
                    if line.startswith('voluntary_ctxt_switches:'):
                        metrics['ctx_switches'] += int(line.split()[-1])
                    elif line.startswith('nonvoluntary_ctxt_switches:'):
                        metrics['ctx_switches'] += int(line.split()[-1])
        except:
            print 'Failed to get ctx switch count for pid {0}'.format(pid)
    try:
        funnel.send(json.dumps(metrics))
    except:
        print "Failed to send data to funnel, trying again..."
        funnel.close()
        funnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            funnel.connect((endpoint_host, endpoint_port))
        except:
            print 'Failed to connect to funnel'
    current_time = time.time()
    wait_time = 1.0 - (current_time - int(current_time))
    time.sleep(wait_time)
