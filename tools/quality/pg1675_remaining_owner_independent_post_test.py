"""Independent readonly post bindings and digest type/shape refusal."""
import unittest
from pyflakes.api import check
import pg1675_remaining_owner_independent_post as p


class IndependentPostTest(unittest.TestCase):
    def test_full_actual_scope_and_readonly(self):
        raw=p.payload('a'*64)
        self.assertEqual(0,check(raw,'<full current independent post>'))
        for text in ['len(rows)==24',"len(data['artifacts'])==187","lines[-2:]==[b'0',b'0']","fresh['native']==native",'soleOwnerIndependentPost',"not pathlib.Path('/proc/291213').exists()"]:
            self.assertIn(text,raw)
        for text in ['pidfd_send_signal','os.kill(','pg_terminate_backend']:self.assertNotIn(text,raw)

    def test_unknown_fresh_refused_before_connection(self):
        for value in [None,True,0,'','a'*63,'A'*64,'g'*64,'a'*65]:
            with self.assertRaises(ValueError):p.payload(value)

    def test_actual_interrupted_source_is_not_success(self):
        self.assertEqual('8a5b856fc239b72a65aed0710212ee4829d78a8914d7734dd3dc5abee387bc26',p.qualify_interrupted_reap())


if __name__=='__main__':unittest.main()
