"""Independent literal UI226/SS314 cookie/DOM identity contract. Never exports raw values."""
import hashlib
import html.parser
import http.cookies
import re


def require(value):
    if not value: raise ValueError('independent client contract refused')


class Login(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.csrf=[];self.title=[];self.in_title=False
    def handle_starttag(self, tag, attrs):
        require(len(attrs)==len(dict(attrs)))
        attributes=dict(attrs)
        if tag=='title': self.in_title=True
        if tag=='input'and attributes.get('name')=='_csrf':
            require(attributes.get('type')=='hidden');self.csrf.append(attributes.get('value'))
    def handle_endtag(self, tag):
        if tag=='title':self.in_title=False
    def handle_data(self, data):
        if self.in_title:self.title.append(data)


def cookie_identity(values):
    require(type(values)is list and len(values)==1 and type(values[0])is str)
    jar=http.cookies.SimpleCookie();jar.load(values[0])
    require(set(jar)=={'SCHUBERT_NK_SESSION'})
    cookie=jar['SCHUBERT_NK_SESSION'];raw=cookie.value
    require(re.fullmatch('[A-Za-z0-9_-]{43}',raw)is not None)
    require(cookie['secure']is True and cookie['httponly']is True and cookie['samesite']=='Lax'and cookie['path']=='/'and not cookie['domain']and not cookie['max-age']and not cookie['expires'])
    return hashlib.sha256(raw.encode('ascii')).hexdigest()


def body_identity(body, plaintext, row_hash, cookie_hash):
    require(type(body)is bytes and 0<len(body)<=65536 and type(plaintext)is dict)
    parser=Login();parser.feed(body.decode('utf8'));parser.close()
    require(''.join(parser.title)=='schubert NK - ログイン'and len(parser.csrf)==1)
    token=parser.csrf[0];require(type(token)is str and re.fullmatch('[0-9a-f]{64}',token)is not None)
    require(plaintext.get('formatVersion')==2 and plaintext.get('operationTokens')==[] and plaintext.get('csrfToken')==token)
    require(type(row_hash)is str and row_hash==cookie_hash and re.fullmatch('[0-9a-f]{64}',row_hash)is not None)
    return {'receivedBodyBytes':len(body),'receivedBodySha256':hashlib.sha256(body).hexdigest(),'cookieMatchesUniqueDatabaseSession':True,'csrfMatchesDecryptedSession':True,'approvedTitleMatches':True,'rawValuesExported':False}
