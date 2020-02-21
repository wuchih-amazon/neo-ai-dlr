import logging
import urllib3
import certifi
from .. import config


class RestUrlUtils(object):
    def send(self, message):
        """send data to AWS Rest server"""
        resp_code = 0
        try:
            hrd = {'Content-Type': 'application/x-amz-json-1.1'}
            data = message.encode('utf-8')
            req = urllib3.PoolManager(
                cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            resp = req.request('POST', config.CALL_HOME_URL,
                               headers=hrd, body=data)
            resp_code = resp.status
            logging.info("Response Data:", resp.data)
            logging.info("Response Status:", resp.status)
        except urllib3.exceptions.HTTPError as e:
            print(e)
            logging.exception("rest api error!", exc_info=False)
            resp_code = -1
        except Exception as e:
            print(e)
            logging.exception("rest api miscellaneous error", exc_info=False)
            resp_code = -1
        return resp_code