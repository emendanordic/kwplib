# MIT License
#
# Copyright (c) 2016 Emenda Nordic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import collections, logging, os, re, sys
import socket
if sys.version_info >= (3, 0):
    import urllib.parse
    import urllib.request
else:
    import httplib, urllib, urllib2

RE_URL_PATTERN = "^(http[s]?):\/\/([\w.]+)*:([0-9]+)"
RE_API_PATTERN = "^(http[s]?):\/\/([\w.]+)*:([0-9]+)\/review\/api$"

class KwApiCon:
    def __init__(self, url=None, user=None, verbose=False):
        self.url = None
        self.api = None
        self.host = None
        self.port = None

        self.user = None
        self.ltoken = None

        logLevel = logging.INFO
        if verbose:
            logLevel = logging.DEBUG
        logging.basicConfig(level=logLevel,
            format='%(levelname)s:%(asctime)s %(name)s %(message)s',
            datefmt='%Y/%m/%d %H:%M:%S')
        self.logger = logging.getLogger('kwplib')

        self.set_url(url)
        self.set_user(user)


    def set_url(self, url):
        if url:
            self.url = url
            self.api = url + "/review/api"
            self.logger.debug(('Validating URL to api "{0}" with regular'
                ' expression "{1}"...'.format(self.api, RE_API_PATTERN)))
            if not (re.match(RE_API_PATTERN, self.api)):
                sys.exit("URL {} does not match required pattern".format(self.api))
            result = re.search(RE_URL_PATTERN, url)
            self.ssl = (result.group(1) == 'https')
            self.host = result.group(2)
            self.port = result.group(3)
            self.get_ltoken_hash()

    def set_user(self, user):
        if user:
            self.user = user
            self.get_ltoken_hash()


    def get_ltoken_hash(self):
        if (self.host != None and self.port != None and self.user != None):
            self.ltoken = self._get_ltoken_hash()


    def _get_ltoken_hash(self):
        ltoken_path = self._get_ltoken_path()
        with open(ltoken_path, 'r') as f:
            for r in f:
                self.logger.debug('Checking in ltoken line "{0}"'.format(r.strip()))
                rd = r.strip().split(';')
                if rd[0] == self.host and rd[1] == self.port and rd[2] == self.user:
                    return rd[3]
            sys.exit(("Could not find matching ltoken record. Searching for"
                " host '{0}', port '{1}' and user '{2}' in file '{3}'").format(
                    self.host, self.port, self.user, ltoken_path
                ))

    # return ltoken file path or None, if not found
    def _get_ltoken_path(self):
        ltoken_path = os.path.join(os.path.expanduser('~'), ".klocwork", "ltoken")
        if not os.path.exists(ltoken_path):
            sys.exit("Could not find ltoken file '{0}'".format(ltoken_path))
        return ltoken_path

    def execute_query(self, values):
        if not self.ltoken:
            sys.exit(("ltoken hash not set. Please ensure you have provided the"
            " url and user"))
        if not 'action' in values:
            sys.exit("No action specified in values '{0}'".format(values))
        values['user'] = self.user
        values['ltoken'] = self.ltoken
        self.logger.debug('Executing query with values "{0}"'.format(str(values)))
        result = self._query(values)
        self.logger.debug('Returning result with values "{0}"'.format(str(result)))
        return result

    def _query(self, values):
        QueryResponse = collections.namedtuple('QueryResponse', ['response', 'error_msg'])
        try:
            if sys.version_info >= (3, 0):
                data = urllib.parse.urlencode(values).encode("utf-8")
                response = urllib.request.urlopen(self.api, data)
                return response.read().decode("utf-8")
            else:
                data = urllib.urlencode(values)
                request = urllib2.Request(self.api, data)
                response = urllib2.urlopen(request)
                return QueryResponse(response, None)
        except urllib2.HTTPError as e:
            return QueryResponse(None, 'HTTP Connection Error code: ' + str(e.read()))
        except urllib2.URLError as e:
            return QueryResponse(None, 'URL Error: ' +  str(e.reason))
        except httplib.InvalidURL as e:
            return QueryResponse(None, 'Invalid URL Error: ' +  str(e))
        except:
            return QueryResponse(None, 'Error not caught... Something else went wrong.')
