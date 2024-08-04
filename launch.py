import argparse
import os
import json
import re
import importlib

def parse_config(cfg):
    try:
        return json.loads(re.sub('//.*', '', cfg))
    except json.JSONDecodeError:
        with open(cfg) as file:
            return json.loads(re.sub('//.*', '', file.read()))

def main_cli():
    if not (os.path.exists('config.json') and os.path.isfile('config.json')):
        with open('config.json', 'w') as file:
            file.write('{}')
    
    parser = argparse.ArgumentParser(add_help=False, description='Launch a simple HTTP server.')
    parser.add_argument('-?', '--help', action='help', help='Show usage and quit')
    parser.add_argument('-v', '--version', action='store_true', help='Show version and quit')
    parser.add_argument('-c', '--config', action='append', help='Replace `config.json` with the specified string or file')
    parser.add_argument('-m', '--mergeconfig', action='store_true', help='Merge configs instead of replacung')

    args = parser.parse_args()
    if args.version:
        return print('Version 1.1')
    if args.config == None:
        args.config = []
    args.config.insert(0, 'config.json')

    config = {} if args.mergeconfig else parse_config(args.config[-1])
    if args.mergeconfig:
        for cfg in ['config.json'] + args.config:
            config.update(parse_config(cfg))
    
    main = importlib.import_module('main')
    main.run(config)

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    main_cli()