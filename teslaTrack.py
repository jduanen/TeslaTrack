#!/usr/bin/env python3
'''
################################################################################
#
# teslaTrack: tool to watch for Tesla state changes
#
# This is to be run on a server and be interacted with via either local CLI or
#  a web-based interface.
# This will issue various types of notifications to interested devices
#
# N.B.
#  * Values given on command line override those in the config file.
#
################################################################################
'''

import argparse
from datetime import datetime
import json
import logging
import multiprocessing as mp
import os
import queue
import signal
import sys
import time

import yaml
import teslapy

from CommandInterpreter import CommandInterpreter
from Tracker import Tracker

from __init__ import * #### FIXME


DEF_CONFIG_FILE = "./teslaTrack.yml"

DEFAULT_CONFIG = {
    'logLevel': "INFO",  #"DEBUG"  #"WARNING"
    'logFile': None  # None means use stdout
}


ci = None
tasks = {}
tesla = None
selectedVehicles = []


def dumpQueue(q):
    ''' Return the contents of a given message queue.
    '''
    result = []
    try:
        msg = q.get(True, 0.1)
        while msg:
            result.append(msg)
            msg = q.get(True, 0.1)
    except queue.Empty:
        pass
    return result

def run(options):
    global ci

    tesla = teslapy.Tesla(options.email)
    vehicles = tesla.vehicle_list()
    for i, v in enumerate(vehicles):
        if v['display_name'] in options.selected:
            selectedVehicles.append(v)
            if (False):  #### FIXME
                v.sync_wake_up()
            if options.verbose:
                dn = v['display_name']
                ## ts = v.last_seen()
                ts = datetime.fromtimestamp(v['drive_state']['timestamp'] / 1000.0)
                bl = v['charge_state']['battery_level']
                print(f"Vehicle #{i}: {dn} last seen at {ts} with {bl}% battery level")

    cmdQs = {}
    respQs = {}
    for name in options.selected:
        cmdQs[name] = mp.Queue()
        respQs[name] = mp.Queue()
        t = Tracker(name, cmdQs[name], respQs[name])
        tasks[name] = mp.Process(target=t.run, args=())
        tasks[name].start()
        logging.info(f"Starting Tracker for {name}")

    if options.interactive:
        print("Starting CLI cmd interpreter")
        respQs['ci'] = mp.Queue()
        ci = CommandInterpreter(selectedVehicles)
        ci.run(cmdQs)
        ci = None

    for taskName, task in tasks.items():
        logging.info(f"Waiting on '{taskName}'")
        task.join()
        logging.debug(f"Results for {task}: {dumpQueue(respQs[taskName])}")

    logging.info("Done")
    return 0

def getOps():
    def signalHandler(sig, frame):
        ''' Catch SIGHUP to force a reload/restart and SIGINT to stop all.""
        '''
        if sig == signal.SIGHUP:
            logging.info("SIGHUP")
            #### TODO stop, reload, and restart everything
        elif sig == signal.SIGINT:
            logging.info("SIGINT")
            if ci:
                ci.terminate()
            for taskName, task in tasks.items():
                logging.info(f"Waiting on '{taskName}'")
                task.join()
                logging.info(f"'{taskName}' stopped")

    usage = f"Usage: {sys.argv[0]} [-v] [-c <configFile>] [-i] [-L <logLevel>] [-l <logFile>] [-s <nameList>] <email>"
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-c", "--configFile", action="store", type=str,
        default=DEF_CONFIG_FILE,
        help="Path to file with configuration information; will be created if doesn't exist")
    ap.add_argument(
        "-i", "--interactive", action="store_true", default=False,
        help="Enable interactive mode")
    ap.add_argument(
        "-L", "--logLevel", action="store", type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level")
    ap.add_argument(
        "-l", "--logFile", action="store", type=str,
        help="Path to location of logfile (create it if it doesn't exist)")
    ap.add_argument(
        "-s", "--select", action="store", type=str,
        help="Comma separated list of names of vehicles to select")
    ap.add_argument(
        "-v", "--verbose", action="count", default=0, help="Print debug info")
    ap.add_argument(
        "email", action="store", type=str,
        help="Email address of registered Tesla account")
    opts = ap.parse_args()

    if not os.path.exists(opts.configFile):
        with open(opts.configFile, "w+") as f:
            f.write("%YAML 1.1\n---\n{}\n")
            if opts.verbose:
                print(f"Creating config file: '{opts.configFile}'")

    with open(opts.configFile, "r") as configFile:
        config = list(yaml.load_all(configFile, Loader=yaml.Loader))[0]
    if opts.verbose > 1:
        print("Config file contents:")
        json.dump(config, sys.stdout, indent=4, sort_keys=True)
        print("")

    # N.B. precedence order: command line options then config file inputs.
    #      if neither given, then propmt user for console input
    opts.config = DEFAULT_CONFIG

    if opts.logLevel:
        config['logLevel'] = opts.logLevel
    if opts.logFile:
        config['logFile'] = opts.logFile
    dictMerge(opts.config, config)
    if opts.verbose:
        print("CONFIG:")
        json.dump(opts.config, sys.stdout, indent=4, sort_keys=True)
        print("")

    if opts.config['logFile'] and not os.path.exists(opts.config['logFile']):
        with open(opts.config['logFile'], "w+") as f:
            if opts.verbose:
                print(f"Creating log file: '{opts.config['logFile']}'")
            f.write("")

    opts.config['level'] = getattr(logging, opts.config['logLevel'], None)
    if not isinstance(opts.config['level'], int):
        fatalError(f"Invalid log level: {opts.config['logLevel']}")
    logging.basicConfig(filename=opts.config.get('logFile', None),
                        level=opts.config['level'])

    opts.selected = []
    if opts.select:
        opts.selected = opts.select.strip().split(',')

    #### FIXME
#    signal.signal(signal.SIGHUP, signalHandler)
    signal.signal(signal.SIGINT, signalHandler)

    if opts.verbose:
        print(f"    Account email:     {opts.email}")
        if opts.selected:
            print(f"    Selected Vehicles: {opts.selected}")
        print(f"    Log level:         {opts.config['logLevel']}")
        if opts.config['logFile']:
            print(f"    Logging to:        {opts.config['logFile']}")
        else:
            print(f"    Logging to stdout")
        if opts.interactive:
            print("    Interactive mode enabled")

    return opts


if __name__ == '__main__':
    opts = getOps()
    r = run(opts)
    sys.exit(r)
