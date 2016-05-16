#!/usr/bin/env python
import socket
import json
import signal
import sys
import pyuv
from metrichandlers import handlers

try:
    graphite_host = sys.argv[1]
except:
    print "Usage: {0} <graphite_host>".format(sys.argv[0])
    sys.exit(1)


last_datasets = {}

loop = pyuv.Loop.default_loop()
clients = {}

graphite = pyuv.TCP(loop)
server = pyuv.TCP(loop)


def metric_report(client, data, error):
    if data is None:
        client.close()
        if clients[client]['bmc']:
            del last_datasets[clients[client]['bmc']]
        del clients[client]
        return

    data = clients[client]['buffer'] + data
    try:
        data = json.loads(data)
        clients[client]['buffer'] = ''
    except:
        clients[client]['buffer'] += data
        if len(clients[client]['buffer']) > 1000000:
            clients[client]['buffer'] = ''
        return

    bmc = data['bmc']
    clients[client]['bmc'] = bmc
    if bmc not in last_datasets:
        last_datasets[bmc] = data
    else:
        metrics = ''
        graph = 'OpenBMC.{0}'.format(bmc)
        for handler in handlers:
            metrics += handler(graph, last_datasets[bmc], data)
        graphite.write(metrics)
        last_datasets[bmc] = data


def on_connection(handle, error):
    client = pyuv.TCP(handle.loop)
    handle.accept(client)
    clients[client] = {'buffer': '', 'bmc': None}
    client.start_read(metric_report)


def graphite_connected(handle, error):
    server.bind(("0.0.0.0", 1234))
    server.listen(on_connection)


graphite.connect((socket.gethostbyname(graphite_host), 2003),
                 graphite_connected)


def shutdown(handle, signum):
    ''' Handles shutdown signals '''
    for client, client_id in clients.iteritems():
        client.close()
    server.close()
    graphite.close()
    handle.close()

signal_h = pyuv.Signal(loop)
signal_h.start(shutdown, signal.SIGINT)

loop.run()
