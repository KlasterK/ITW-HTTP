import sys
import enum
import asyncio
import time
import aiofiles
import re
import os

import aiofiles.base

class EReqMeth(enum.Enum):
    GET     = 'GET'
    HEAD    = 'HEAD'

METH_DICT = {}
for meth in EReqMeth.__members__:
    METH_DICT[meth.encode('ascii')] = EReqMeth.__members__[meth]

class Request:
    def __init__(self, url, method = EReqMeth.GET):
        self.url = url
        self.method = method

class Response:
    def __init__(self, status_code, content):
        self.sc = status_code
        self.content = content

    def to_bytes(self):
        return

class HTTPServer:
    routes = {}
    re_routes = {}

    def __init__(self, config: dict):
        bind = config.get('bind', '')
        port = config.get('port', 80)

        self.sc_redirects = config.get('status_codes_content', {})
        self.timestamp_format = config.get('timestamp_format', '[%d.%m.%Y %H:%M:%S]')
        self.server = asyncio.start_server(self.serve, port=80)
        
    async def serve(self, reader: asyncio.streams.StreamReader, writer: asyncio.streams.StreamWriter):
        addr = writer.get_extra_info('peername', ('UNKNOWN', 0))
        self.log('New connection from ' + addr[0] + ':' + str(addr[1]))

        line = await reader.readuntil(b'\r\n')
        line = line.split()
        try:
            method = METH_DICT[line[0]]
        except KeyError:
            return self.status_close(writer, 501)
        except IndexError:
            return self.status_close(writer, 400)
        self.log('First line: ' + str(line))
        
        url = line[1].split(b'?', 1)
        path = b'data' + url[0]
        if b'.kaccess' in path or b'..' in path or b'~' in path:
            return self.status_close(writer, 403)
        if os.path.exists(path) and os.path.isfile(path):
            writer.write(b'HTTP/1.1 200 OK')
            if method == EReqMeth.GET:
                writer.write(b'\r\n\r\n')
                async with aiofiles.open(path, 'rb') as file:
                    writer.write(await file.read())
            return writer.close()
        else:
            self.status_close(writer, 404)
    
    async def run(self):
        asyncio.create_task(self.server)
        await self._run()

    async def _run(self):
        self.log('HTTP Server has started')

        while True:
            s = await aiofiles.stdin.readline()

            if s.startswith('stop'):
                self.server.close()
            
            elif s:
                self.log('Unknown command was entered')
    
    def bind(self, url, reg_expr = False):
        def decorator(func):
            self._bind(func, url, reg_expr)
            return func
        return decorator
    
    def _bind(self, func, url, reg_expr):
        if reg_expr:
            self.routes[url] = func
        else:
            self.re_routes[re.compile(url)] = func

    def log(self, text):
        print(time.strftime(self.timestamp_format), text)
    
    def status_close(self, writer, status, content = None):
        status_desc = str(status).encode('ascii') + b' ' + SC_DESC.get(status, SC_DESC[...])
        if not content:
            try:
                content = self.sc_redirects[str(status)].encode('utf-8', 'replace')
                if os.path.exists(path := b'data' + content) and os.path.isfile(path):
                    with open(path, 'rb') as file:
                        content = file.read()
            except KeyError:
                content = b'<html><head><title>' + status_desc + b'</title><style>html{background-color:whitesmoke;}' \
                          b'body{margin:1em auto;padding:1em;background-color:white;max-width:800px;text-align:center;}</style></head>' \
                          b'<body><h1>' + status_desc + b'</h1><p>You were served by HTTP Server by KlasterK</p></body></html>'
        writer.write(b'HTTP/1.1 ' + status_desc + b'\r\n\r\n' + content)
        writer.close()
    
    def kaccess_prepare(self, url):
        if os.path.exists(path := os.path.dirname(b'data' + url) + b'/.kaccess') and os.path.isfile(path):
            with open(path, 'rb') as file:
                for line_index, line in enumerate(file.readlines(), 1):
                    line = line.split(b'#', 1)[0].strip().split()
                    if line[0][:2] == b're':
                        match = re.match(line[2:], url)
                    else:
                        match = line[0] == url
                    if not match:
                        continue
                    if len(line) < 3:
                        if line[1][0] == b'3':
                            self.log(f'Error in \'{path}\', line {line_index}: redirect found, but redirect address - not')
                            continue
                        
            return None
        return None

def run(config):
    asyncio.run(HTTPServer(config).run())
    #HTTPServer(config).run()

if __name__ == '__main__':
    import launch
    launch.main_cli()

# Auxiliary Data

SC_DESC = {
    ...: b'Unknown Status Code',
    100: b'Continue',
    101: b'Switching Protocols',
    102: b'Processing',
    103: b'Early Hints',
    200: b'OK',
    201: b'Created',
    202: b'Accepted',
    203: b'Non-Authoritative Content',
    204: b'No Content',
    205: b'Reset Content',
    206: b'Partial Content',
    207: b'Multi-Status',
    208: b'Already Reported',
    226: b'IM Used',
    300: b'Multiple Choices',
    301: b'Moved Permanently',
    302: b'Found',
    303: b'See Other',
    304: b'Not Modified',
    305: b'Use Proxy',
    307: b'Temporary Redirect',
    308: b'Permanent Redirect',
    400: b'Bad Request',
    401: b'Unauthorized',
    402: b'Payment Required',
    403: b'Forbidden',
    404: b'Not Found',
    405: b'Method Not Allowed',
    406: b'Not Acceptable',
    407: b'Proxy Authentication Required',
    408: b'Request Timeout',
    409: b'Conflict',
    410: b'Gone',
    411: b'Length Required',
    412: b'Precondition Failed',
    413: b'Payload Too Large',
    414: b'URI Too Long',
    415: b'Unsupported Media Type',
    416: b'Range Not Satisfiable',
    417: b'Exceptation Failed',
    418: b'I\'m a teapot',
    419: b'Authentication Timeout',
    421: b'Misdirected Request',
    422: b'Unprocessable Entity',
    423: b'Locked',
    424: b'Failed Dependency',
    425: b'Too Early',
    426: b'Update REquired',
    428: b'Precondition Requiired',
    429: b'Too Many Requests',
    431: b'Request Header Fields Too Large',
    449: b'Retry With',
    451: b'Unavaible For Legal Reasons',
    499: b'Clkent Closed Request',
    500: b'Internal Server Error',
    501: b'Not Implemented',
    502: b'Bad Gateway',
    503: b'Service Unavailable',
    504: b'Gtaway Timeout',
    505: b'HTTP Version Not Supported',
    506: b'Variant Also Negotiates',
    507: b'Insuffient Storage',
    508: b'Loop Detected',
    509: b'Badwith Limit Exceeded',
    510: b'Not Extended',
    511: b'Network Authentication Required',
}