#!/usr/bin/env python3

"""Get the last version of a repository in an DockerHub account."""

import argparse
import json
import logging
import subprocess

ACCOUNT = 'markrtuttle'
LATEST = 'latest'
QUERY = 'https://registry.hub.docker.com/v2/repositories/{account}/{repo}/tags'

################################################################

def create_parser():
    parser = argparse.ArgumentParser(
        description='Get last version in a DockerHub repository.'
    )
    parser.add_argument(
        '--account',
        default=ACCOUNT,
        help='DockerHub account.'
    )
    parser.add_argument(
        '--repository',
        required=True,
        help='DockerHub repository (image) in DockerHub account.'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output.'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Debugging output.'
    )
    return parser

################################################################

def configure_logging(verbose, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(levelname)s: %(message)s')
    elif verbose:
        logging.basicConfig(level=logging.INFO,
                            format='%(levelname)s: %(message)s')
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s')

################################################################

def integer(string):
    try:
        return int(string)
    except ValueError:
        return None

def integer_tags(tags):
    return [tag
            for tag in tags
            if all([integer(string) is not None for string in tag.split('.')])]

def integer_tag_key(tag):
    return [integer(string) for string in tag.split('.')]

def docker_response(account, repository):
    cmd = ['curl', '-L', QUERY.format(account=account, repo=repository)]
    logging.debug("Query '%s'", ' '.join(cmd))
    data = subprocess.run(cmd, text=True, capture_output=True, check=True)
    logging.debug("Query output: %s", data.stdout)
    return data.stdout

def docker_tags(response):
    return {tag['name']: tag['images'][0]['digest']
            for tag in json.loads(response)['results']}

def last_tag(tags):
    tags = sorted(integer_tags(tags), key=integer_tag_key, reverse=True)
    if not tags:
        return LATEST
    return tags[0]

def main():
    args = create_parser().parse_args()
    configure_logging(args.verbose, args.debug)

    tags = docker_tags(docker_response(args.account, args.repository))
    last = last_tag(tags)
    if tags[last] != tags[LATEST]:
        logging.warning("Last version %s is the latest image.", last)
        logging.warning("%s digest: %s...", last, tags[last][:40])
        logging.warning("%s digest: %s...", LATEST, tags[LATEST][:40])
    logging.info("Last %s digest: %s...", last, tags[last][:40])
    print(last)

if __name__ == "__main__":

    main()
