# OpenBMC metric watcher

This repo has two python scripts to collect metrics from [OpenBMC](https://github.com/openbmc/openbmc) and push the results to [Graphite](http://graphite.wikidot.com/).

## Pusher

The pusher script, `metric-pusher.py` is copied onto an OpenBMC instance and pointed to the *metric-funnel* script. The pusher gathers data from various locations in [procfs](http://man7.org/linux/man-pages/man5/proc.5.html) and pushes the data over TCP to the funnel.

Timestamps passed via the system are in unix epoch format, ensure that the OpenBMC instance being tested has the right date and time configured.

## Funnel

The funnel/collector script, `metric-funnel.py` runs on a non-OpenBMC machine and receives the data from one or many *pusher* instances and transforms the data to be pushed into Graphite.


