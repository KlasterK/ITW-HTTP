import socket
import threading
import sys
import enum
import asyncio

class EReqMeth(enum.Enum):
    GET     = 'GET'

class Request:
    def __init__(self, url, method = EReqMeth.GET):
        self.url = url
        self.method = method

class Response:
    def __init__(self):
        ...

class HTTPServer:
    routes = {}

    def __init__(self, config: dict):
        addr = (config.get('bind', ''), config.get('port', 80))
        backlog = config.get('backlog', 1000)

        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(addr)
        self.listener.listen(backlog)
    
    def accept(self):
        sock, addr = self.listener.accept()
        data = sock.recv(2 ** 32)
        sock.send(b'HTTP/1.1 501 Not Implemented\r\n\r\n<html><body><p>Hello, ' + addr[0].encode('ASCII') + b':' + repr(addr[1]).encode('ASCII') + b'!</p></body></html>')
        sock.close()
    
    def listen_loop(self):
        while True:
            self.accept()
    
    def main_loop(self):
        threading.Thread(target=self.listen_loop).start()
        print('HTTP Server has started')
        while True:
            s = input()
            if s.startswith('stop'):
                sys.exit(0)
            else:
                print('Unknown command')
    
    def bind(self, url, reg_expr = False):
        def decorator(func):
            self._bind(func, url)
            return func
        return decorator
    
    def _bind(self, func, url):
        self.routes[url] = func

def run(config):
    HTTPServer(config).main_loop()

# if __name__ == '__main__':
#     import launch
#     launch.main_cli()

s='''400 Bad Request («неправильный, некорректный запрос»)[3][4];
401 Unauthorized («не авторизован»)[10];
402 Payment Required («необходима оплата») — зарезервировано для использования в будущем[3];
403 Forbidden («запрещено (не уполномочен)»)[3];
404 Not Found («не найдено»)[3];
405 Method Not Allowed («метод не поддерживается»)[3];
406 Not Acceptable («неприемлемо»)[3];
407 Proxy Authentication Required («необходима аутентификация прокси»)[10];
408 Request Timeout («истекло время ожидания»)[3];
409 Conflict («конфликт»)[3][4];
410 Gone («удалён»)[3];
411 Length Required («необходима длина»)[3];
412 Precondition Failed («условие ложно»)[8][11];
413 Payload Too Large («полезная нагрузка слишком велика»)[3];
414 URI Too Long («URI слишком длинный»)[3];
415 Unsupported Media Type («неподдерживаемый тип данных»)[3];3
416 Range Not Satisfiable («диапазон не достижим»)[12];
417 Expectation Failed («ожидание не оправдалось»)[3];
418 I’m a teapot («я — чайник»);
419 Authentication Timeout (not in RFC 2616) («обычно ошибка проверки CSRF»);
421 Misdirected Request[13];
422 Unprocessable Entity («необрабатываемый экземпляр»);
423 Locked («заблокировано»);
424 Failed Dependency («невыполненная зависимость»);
425 Too Early («слишком рано»);
426 Upgrade Required («необходимо обновление»)[3];
428 Precondition Required («необходимо предусловие»)[14];
429 Too Many Requests («слишком много запросов»)[14];
431 Request Header Fields Too Large («поля заголовка запроса слишком большие»)[14];
449 Retry With («повторить с»)[1];
451 Unavailable For Legal Reasons («недоступно по юридическим причинам»)[15].
499 Client Closed Request (клиент закрыл соединение);
500 Internal Server Error («внутренняя ошибка сервера»)[3];
501 Not Implemented («не реализовано»)[3];
502 Bad Gateway («плохой, ошибочный шлюз»)[3];
503 Service Unavailable («сервис недоступен»)[3];
504 Gateway Timeout («шлюз не отвечает»)[3];
505 HTTP Version Not Supported («версия HTTP не поддерживается»)[3];
506 Variant Also Negotiates («вариант тоже проводит согласование»)[16];
507 Insufficient Storage («переполнение хранилища»);
508 Loop Detected («обнаружено бесконечное перенаправление»)[17];
509 Bandwidth Limit Exceeded («исчерпана пропускная ширина канала»);
510 Not Extended («не расширено»);
511 Network Authentication Required («требуется сетевая аутентификация»)[14];
520 Unknown Error («неизвестная ошибка»)[18];
521 Web Server Is Down («веб-сервер не работает»)[18];
522 Connection Timed Out («соединение не отвечает»)[18];
523 Origin Is Unreachable («источник недоступен»)[18];
524 A Timeout Occurred («время ожидания истекло»)[18];
525 SSL Handshake Failed («квитирование SSL не удалось»)[18];
526 Invalid SSL Certificate («недействительный сертификат SSL»)[18].'''

import re
def repl(match):
    return match[1] + ': \'' + match[2] + '\',\n'

ss = re.sub('(\\d{3})\\s(.*)\\(.*$', repl, s)
with open('ff.txt','w') as f:
    f.write(ss)