#!/usr/bin/python3
# coding: utf-8

import argparse
import datetime as dt
import ftplib
import signal
import sys
import time
from colorama import Fore

## Global variables
init_time = None
outfile = None

def ctrl_c(sig, frame):
    global init_time
    sys.stderr.write('\n[+] Exiting...\n')
    end_time = time.perf_counter()
    time_message = f"Elapsed time: {end_time - init_time:.3f} s"
    date_message = f"End time: {dt.datetime.now().strftime('%F %T')}"
    print(time_message)
    print(date_message)
    if outfile:
        outfile.write(time_message + '\n')
        outfile.write(date_message + '\n')
        outfile.flush()
        outfile.close()
    sys.exit(1)

def connect(target:str,
            port:int,
            username:str,
            password:str,
            verbose:int) -> bool:
    ftp = ftplib.FTP()
    if verbose > 2:
        ftp.set_debuglevel(2)
    elif verbose > 1:
        ftp.set_debuglevel(1)
    found = False
    try:
        ftp.connect(target, port, timeout=0.1)
        ftp.login(username, password)
        found = True
        print(f"{Fore.GREEN}Found: {username} - {password}{Fore.RESET}")
    except Exception as e:
        if args.verbose > 0:
            print(f"{Fore.RED}Failed: {username} - {password}{Fore.RESET}")
    return found

def main(args):
    global init_time
    signal.signal(signal.SIGINT, ctrl_c)

    message = f"Start time: {dt.datetime.now().strftime('%F %T')}"
    if not args.quiet:
        print(message)
    if args.output:
        try:
            global outfile
            outfile = open(args.output, 'w+')
            outfile.write(message + '\n')
            outfile.flush()
        except Exception as e:
            raise Exception(str(e))

    if args.userlist:
        with open(args.userlist, 'r') as ulist:
            usernames = list(map(str.strip, ulist.readlines()))
            if usernames[-1] == '':
                usernames.pop()
    elif args.username:
        usernames = [args.username]

    if args.passlist:
        with open(args.passlist, 'r') as plist:
            passwords = list(map(str.strip, plist.readlines()))
            if passwords[-1] == '':
                passwords.pop()
    elif args.password:
        passwords = [args.password]

    init_time = time.perf_counter()
    success = False
    for username in usernames:
        for password in passwords:
            success = connect(args.target, args.port, username, password, args.verbose)
            if success:
                creds_message = f"Found: {username} - {password}"
                if outfile:
                    outfile.write(creds_message + '\n')
                    outfile.flush()
                if args.forcequit:
                    break
        if success and args.forcequit:
            break
    end_time = time.perf_counter()

    time_message = f"Elapsed time: {end_time - init_time:.3f} s"
    date_message = f"End time: {dt.datetime.now().strftime('%F %T')}"
    if not args.quiet:
        print(time_message)
        print(date_message)
    if args.output:
        outfile.write(time_message + '\n')
        outfile.write(date_message + '\n')
        outfile.flush()

    if args.output:
        outfile.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type=str, help="Target URL/IP")
    parser.add_argument('port', type=int, help="Target port", default=21)
    parser.add_argument('-u', '--username', type=str, help="Username")
    parser.add_argument('-U', '--userlist', type=str, help="Username list file")
    parser.add_argument('-p', '--password', type=str, help="Password")
    parser.add_argument('-P', '--passlist', type=str, help="Password list file")
    parser.add_argument('-f', dest='forcequit', action='store_true', help="Quit on success")
    parser.add_argument('-v', '--verbose', action='count', default=0, help="Verbose mode")
    parser.add_argument('-q', '--quiet', action='store_true', help="Don't show date and performance messages")
    parser.add_argument('-o', '--output', type=str, help="Output file")
    # Parsing
    args = parser.parse_args()
    # Incompatibilities
    if args.username and args.userlist:
        error_message = f"Only one of -u or -U should be specified"
        raise ArgumentTypeError(error_message)
    if args.password and args.passlist:
        error_message = f"Only one of -p or -P should be specified"
        raise ArgumentTypeError(error_message)
    # Requirements
    if not (args.username or args.userlist):
        error_message = f"Either -u or -U should be specified"
        raise ArgumentTypeError(error_message)
    if not (args.password or args.passlist):
        error_message = f"Either -p or -P should be specified"
        raise ArgumentTypeError(error_message)
    # Calling the main function
    main(args)
