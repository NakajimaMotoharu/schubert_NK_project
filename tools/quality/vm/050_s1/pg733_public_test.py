"""No publishing authority during tests; exact whitelist/spec/source bindings."""
import unittest
from pg733_public_parent import source


class BindingTest(unittest.TestCase):
    def test_new_receipts_and_no_raw_exports(self):
        raw=source();compile(raw,'<publication bindings>','exec')
        for token in ('PG722-current-native-public-v1','pg730-current-eight-native-v1',
                      '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','RET724001','DONE725001','NAT730001',
                      "'specs':['580','581','582']",'rawSessionsCookiesTokensCredentialsDBBackupsExported'):
            self.assertIn(token,raw)
        for old in ('pg689','pg690','pg692','pg693','pg694','pg696','pg697','pg698','9bd505'):
            self.assertNotIn(old,raw)
        self.assertIn("assert v['actualExit']==0",raw)


if __name__=='__main__':unittest.main()
