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
import json
import logging
import multiprocessing as mp
import os
import queue
import signal
import sys
import time

import yaml


# default path to configs file
DEF_CONFIGS_FILE = "./teslaTrack.yml"

DEF_LOG_LEVEL = "WARNING"

DEFAULTS = {
    'logLevel': "INFO",  #"DEBUG"  #"WARNING"
}


def commandInterpreter(trackers, cmds, resps):
    ''' TBD
    '''
    #### TODO implement cmd interpreter and send cmds to running trackers to restart them and change their events
    cmd = ""
    while True:
        line = input("> ")
        words = line.split(' ')
        cmd = words[0].lower().strip()
        args = words[1:]
        if cmd == 'l':
            print(f"Tracking: {trackers.keys()}")
        if cmd == 'p':
            vin = args[0]
            if vin not in trackers:
                print(f"ERROR: VIN '{vin}' not being tracked")
            else:
                print(dumpQueue(resps[vin]))
        if cmd == 'r':
            pass
        if cmd == 's':
            vin = args[0]
            if vin not in trackers:
                print(f"ERROR: VIN '{vin}' not being tracked")
            else:
                cmds[vin].put("STOP")
                #### TODO reread trackers
        elif cmd == 'q':
            print("Exiting...")
            break
        elif cmd == '?' or cmd == 'h':
            print("Help:")
            print("    h: print this help message")
            print("    l: show VINs of cars being tracked")
            print("    p <vin>: print output from car given by <vin>")
            print("    r: stop and restart all trackers, re-reading the configs file")
            print("    s <vin>: stop tracking the car given by <vin>")
            print("    q: quit")
            print("    ?: print this help message")
    return

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
    print("RUN")
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
            for vin in cmdQs:
                logging.debug(f"Stopping: {vin}")
                cmdQs[vin].put("STOP")

    usage = f"Usage: {sys.argv[0]} [-v] [-c <configsFile>] [-d <dbDir>] [-i] [-L <logLevel>] [-l <logFile>] [-p <passwd>] [-s <schemaFile>] [-V <VIN>]"
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-c", "--configsFile", action="store", type=str,
        default=DEF_CONFIGS_FILE, help="path to file with configurations")
    ap.add_argument(
        "-d", "--dbDir", action="store", type=str,
        help="path to a directory that contains the DB files for cars")
    ap.add_argument(
        "-i", "--interactive", action="store_true", default=False,
        help="enable interactive mode")
    ap.add_argument(
        "-L", "--logLevel", action="store", type=str, default=DEF_LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level")
    ap.add_argument(
        "-l", "--logFile", action="store", type=str,
        help="Path to location of logfile (create it if it doesn't exist)")
    ap.add_argument(
        "-p", "--password", action="store", type=str, help="user password")
    ap.add_argument(
        "-s", "--schemaFile", action="store", type=str, default=DEF_SCHEMA_FILE,
        help="path to the JSON Schema file that describes the DB's tables")
    ap.add_argument(
        "-V", "--VIN", action="store", type=str,
        help="VIN of car to use (defaults to all found in config file")
    ap.add_argument(
        "-v", "--verbose", action="count", default=0, help="print debug info")
    opts = ap.parse_args()

    if not os.path.exists(opts.configsFile):
        fatalError(f"Invalid configuration file: {opts.configsFile}")

    #### TODO add check if configs file has proper protections

    with open(opts.configsFile, "r") as confsFile:
        confs = list(yaml.load_all(confsFile, Loader=yaml.Loader))[0]
    if opts.verbose > 3:
        json.dump(confs, sys.stdout, indent=4, sort_keys=True)    #### TMP TMP TMP
        print("")
    #### TODO validate config file against ./configSchema.yml, remove error checks and rely on this

    if opts.logLevel:
        confs['config']['logLevel'] = opts.logLevel
    else:
        if 'logLevel' not in confs['config']:
            confs['config']['logLevel'] = DEF_LOG_LEVEL
    logLevel = confs['config']['logLevel']
    l = getattr(logging, logLevel, None)
    if not isinstance(l, int):
        fatalError(f"Invalid log level: {logLevel}")

    if opts.logFile:
        confs['config']['logFile'] = opts.logFile
    logFile = confs['config'].get('logFile')
    if opts.verbose:
        print(f"Logging to: {logFile}")
    if logFile:
        logging.basicConfig(filename=logFile, level=l)
    else:
        logging.basicConfig(level=l)

    opts.user = confs.get('user')
    if not opts.user:
        input("user: ")
    logging.debug(f"user: {opts.user}")

    # N.B. precedence order: command line options then config file inputs.
    #      if neither given, then propmt user for console input
    if opts.password:
        password = opts.password
    else:
        password = confs.get('passwd')
    if not password:
        password = input("password: ")
    opts.passwd = password

    signal.signal(signal.SIGHUP, signalHandler)
    signal.signal(signal.SIGINT, signalHandler)

    opts.confs = confs

    if opts.verbose:
        print("?")

    return opts


if __name__ == '__main__':
    opts = getOps()
    r = run(opts)
    sys.exit(r)
