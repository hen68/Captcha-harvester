import cgi
from pythonProject.browser import launch
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union
from pythonProject.expiring_queue import ExpiringQueue
import time


@dataclass
class HarvesterData:
    captcha_kind: str
    site_key: str
    domain: str
    tokens: 'ExpiringQueue[int]' = ExpiringQueue(110)


def RequestsHandlerWrapper(domain_cache: Dict[str, HarvesterData] = {}):
    class RequestsHandler(BaseHTTPRequestHandler):
        def render_template(self, message: str = None):

            with open(f'templates/{domain_cache.captcha_kind}.html', "r", encoding='utf-8') as template_file:
                template = template_file.read()
                if message:
                    template = template.replace('{{ message }}', message)
                else:
                    template = template.replace('{{ message }}', "")
                template = template.replace('{{ domain }}', domain_cache.domain)
                template = template.replace('{{ site_key }}', domain_cache.site_key)
                print(template)
                self.wfile.write(template.encode('utf-8'))

        def do_GET(self):
            self.render_template()

        def do_POST(self):

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    "REQUEST_METHOD": "POST",
                    "CONTENT_TYPE": self.headers['Content-Type']
                }
            )
            token = form.getvalue('h-captcha-response') or form.getvalue('g-recaptcha-response')
            if token:
                domain_cache.tokens.put(token)
                self.render_template()
            else:
                self.render_template("Incorrect captcha")

    return RequestsHandler


class Harvester(object):
    def __init__(self, host: str, port: int):
        self.domain_cache: Dict[str, HarvesterData] = {}
        self.host = host
        self.port = port

    def serve(self):
        httpd = ThreadingHTTPServer((self.host, self.port), RequestsHandlerWrapper(self.domain_cache))

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.shutdown()

    def launch_browser(self):
        return launch(self.domain_cache.domain, self.host, self.port)

    def captcha_config(self, domain: str, site_key: str, captcha_kind: str):
        config = HarvesterData(domain=domain, site_key=site_key, captcha_kind=captcha_kind)
        self.domain_cache = config

    def set_hcatpcha(self, domain: str, site_key: str):
        self.captcha_config(domain, site_key, "hcaptcha")

    def set_recaptcha_v2(self, domain: str, site_key: str):
        self.captcha_config(domain, site_key, "recaptcha_v2")

    def set_recaptcha_v3(self, domain: str, site_key: str):
        self.captcha_config(domain, site_key, "recaptcha_v3")

    def get_token_queue(self):
        tokens = self.domain_cache.tokens

        return tokens


