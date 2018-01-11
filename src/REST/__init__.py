from json import dumps

from pygments import highlight, lexers, formatters
from robot.api import logger

from .keywords import Keywords


__version__ = '1.0.0.dev5'


class REST(Keywords):

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, url,
                 verify=False,
                 accept="application/json, */*",
                 content_type="application/json",
                 user_agent="Robot Framework RESTinstance",
                 proxies={},
                 schema={}):

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        self.url = url
        self.request = {
            'method': None,
            'endpoint': None,
            'query': {},
            'body': "",
            'headers': {
                'Accept': accept,
                'Content-Type': content_type,
                'User-Agent': user_agent
            },
            'proxies': self.input(proxies),
            'timeout': None,
            'auth': [],
            'cert': None,
            'verify': verify,
            'redirects': True
        }
        self.schema = {
            "exampled": True,
            "version": "draft04",
            "request": {},
            "response": {}
        }
        self.schema.update(self.input(schema))
        self.spec = None
        self.instances = []

    @staticmethod
    def print(json, header="\n", with_colors=True):
        json_data = dumps(json, ensure_ascii=False, indent=4)
        if with_colors:
            json_data = highlight(json_data,
                                  lexers.JsonLexer(),
                                  formatters.TerminalFormatter())
            logger.info("{}{}".format(header, json_data), also_console=True)
        return json
