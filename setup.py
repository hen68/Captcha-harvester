from pythonProject.server import *
from threading import Thread


class Setup:
    def __init__(self, domain: str, host: str, port: int, site_key: str, captcha_type: str):
        self.domain = domain
        self.host = host
        self.port = port
        self.site_key = site_key
        self.captcha_type = captcha_type

    def initialize(self):
        threads = []
        new_harvester = Harvester(self.host, self.port)
        if self.captcha_type == "hcaptcha":
            new_harvester.set_hcatpcha(self.domain, self.site_key)
        elif self.captcha_type == "recaptcha_v2":
            new_harvester.set_recaptcha_v2(self.domain, self.site_key)
        elif self.captcha_type == "recaptcha_v3":
            new_harvester.set_recaptcha_v3(self.domain, self.site_key)

        server = Thread(target=new_harvester.serve, daemon=True)
        browser = new_harvester.launch_browser()
        threads.append(server)
        threads.append(browser)

        for t in threads:
            t.start()

        tokens = new_harvester.get_token_queue()

        while True:
            try:
                token = tokens.get()
                print(token)
            except Exception:
                pass

        for t in threads:
            t.join()


if __name__ == "__main__":
    try:
        start = Setup("www.adidas.pl", '127.0.0.1', 5000, '6LeFl7YUAAAAABUeBMKmWQmNjrfLdppwNKqL26VR', 'recaptcha_v3')
        start.initialize()
    except KeyboardInterrupt:
        pass
