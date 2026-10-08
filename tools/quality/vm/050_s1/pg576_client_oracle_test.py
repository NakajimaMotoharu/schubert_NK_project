import hashlib
import unittest
from pg576_client_oracle import cookie_identity,body_identity


class Test(unittest.TestCase):
    def setUp(self):
        self.cookie='A'*43
        self.header='SCHUBERT_NK_SESSION='+self.cookie+'; Path=/; Secure; HttpOnly; SameSite=Lax'
        self.token='b'*64
        self.body=('<!doctype html><title>schubert NK - ログイン</title><input type="hidden" name="_csrf" value="'+self.token+'">').encode('utf8')
        self.value={'formatVersion':2,'csrfToken':self.token,'operationTokens':[]}
        self.sha=hashlib.sha256(self.cookie.encode('ascii')).hexdigest()
    def test_literal_cookie_identity_and_strict_flags(self):
        self.assertEqual(cookie_identity([self.header]),self.sha)
        for old,new in [('Secure',''),('HttpOnly',''),('SameSite=Lax','SameSite=Strict'),('Path=/','Path=/foreign'),('SESSION=','OTHER='),('A'*43,'A'*42)]:
            with self.assertRaises(ValueError):cookie_identity([self.header.replace(old,new)])
        for bad in (None,[],[None],[self.header,self.header]):
            with self.assertRaises(ValueError):cookie_identity(bad)
    def test_body_literal_token_and_hash_join_negative(self):
        result=body_identity(self.body,self.value,self.sha,self.sha)
        self.assertEqual(result['receivedBodyBytes'],len(self.body));self.assertTrue(result['csrfMatchesDecryptedSession'])
        self.assertEqual(result['receivedBodySha256'],hashlib.sha256(self.body).hexdigest())
        for body in (None,b'',self.body.replace(b'NK -',b'-'),self.body.replace(self.token.encode(),b'c'*64),self.body+b'<input type="hidden" name="_csrf" value="'+self.token.encode()+b'">'):
            with self.assertRaises(ValueError):body_identity(body,self.value,self.sha,self.sha)
        for bad in (None,{}, {**self.value,'formatVersion':1},{**self.value,'operationTokens':[{}]}):
            with self.assertRaises(ValueError):body_identity(self.body,bad,self.sha,self.sha)
        with self.assertRaises(ValueError):body_identity(self.body,self.value,'c'*64,self.sha)


if __name__=='__main__':unittest.main()
