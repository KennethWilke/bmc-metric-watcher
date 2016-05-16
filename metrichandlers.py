def loadavg(graph, last_dataset, data):
    load = data['loadavg'].split()
    metrics = '{0}.cpu.loadavg-1min {1} {2}\n'.format(graph, load[0],
                                                      data['time'])
    metrics += '{0}.cpu.loadavg-5min {1} {2}\n'.format(graph, load[1],
                                                       data['time'])
    metrics += '{0}.cpu.loadavg-15min {1} {2}\n'.format(graph, load[2],
                                                        data['time'])
    procs_running, procs_count = load[3].split('/')
    metrics += '{0}.procs.running {1} {2}\n'.format(graph, procs_running,
                                                    data['time'])
    metrics += '{0}.procs.threads {1} {2}\n'.format(graph, procs_count,
                                                    data['time'])
    return metrics


def meminfo(graph, last_dataset, data):
    metrics = ''
    for line in data['meminfo'].split('\n'):
        if line.startswith('MemTotal:'):
            total = int(line.split()[-2]) * 1024
            metrics += '{0}.memory.total {1} {2}\n'.format(graph, total,
                                                           data['time'])
        elif line.startswith('MemFree:'):
            free = int(line.split()[-2]) * 1024
            metrics += '{0}.memory.free {1} {2}\n'.format(graph, free,
                                                          data['time'])
        elif line.startswith('MemAvailable:'):
            avail = int(line.split()[-2]) * 1024
            metrics += '{0}.memory.available {1} {2}\n'.format(graph, avail,
                                                               data['time'])
    return metrics


def stat(graph, last_dataset, data):
    (user, nice, system, idle, iowait, irq, softirq, steal, guest,
     guest_nice) = [int(x) for x in data['stat'].split('\n')[0].split()[1:]]
    total_time = float(user + nice + system + idle + iowait + irq + softirq +
                       steal + guest + guest_nice)
    metrics = '{0}.cpu.user {1} {2}\n'.format(graph, user / total_time,
                                              data['time'])
    metrics += '{0}.cpu.system {1} {2}\n'.format(graph, system / total_time,
                                                 data['time'])
    metrics += '{0}.cpu.idle {1} {2}\n'.format(graph, idle / total_time,
                                               data['time'])
    metrics += '{0}.cpu.iowait {1} {2}\n'.format(graph, iowait / total_time,
                                                 data['time'])
    metrics += '{0}.cpu.irq {1} {2}\n'.format(graph, irq / total_time,
                                              data['time'])
    metrics += '{0}.cpu.softirq {1} {2}\n'.format(graph, softirq / total_time,
                                                  data['time'])
    return metrics


def interrupts(graph, last_dataset, data):
    interrupt_count = 0
    for line in data['interrupts'].split('\n')[1:-1]:
        interrupt_count += int(line.split()[1])
    data['interrupt_count'] = interrupt_count
    if 'interrupt_count' not in last_dataset:
        return ''

    ips = data['interrupt_count'] - last_dataset['interrupt_count']
    metrics = '{0}.cpu.ips {1} {2}\n'.format(graph, ips, data['time'])

    return metrics


def context_switches(graph, last_dataset, data):
    csps = data['ctx_switches'] - last_dataset['ctx_switches']
    metrics = '{0}.cpu.csps {1} {2}\n'.format(graph, csps, data['time'])

    return metrics


def process_count(graph, last_dataset, data):
    return '{0}.procs.count {1} {2}\n'.format(graph, data['process_count'],
                                              data['time'])


handlers = [loadavg, meminfo, stat, interrupts, context_switches,
            process_count]
