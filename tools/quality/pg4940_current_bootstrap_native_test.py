"""Full current native factory namespaces, genuine-pair monotonicity and no old source credit."""
import inspect
import unittest
from pyflakes.api import check,checkPath
import pg4940_current_bootstrap_catalog as catalog
import pg4942_current_bootstrap_native as native
import pg4944_current_bootstrap_public as public


class Native(unittest.TestCase):
    def test_complete_current_all1647_two_pair_server(self):
        raw=native.server()
        coordinates=native.previous.previous.transport.prior.previous.entry().__globals__['coordinates']
        complete='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="'+('a'*64)+'"\n'+inspect.getsource(coordinates)+'\n'+raw
        self.assertEqual(0,check(complete,'<actual current two-pair CRC server>'))
        for text in ('PG4844-six-v1','PG4942-native-v1','3761',"len(v['selected'])==12",'NativePointDominance',"'currentNativeStreams':10,'validatedNativePoints':12"):
            self.assertIn(text,raw)
        for old in ('PG4694','PG4782','PG4926','3739'):self.assertNotIn(old,raw)
        self.assertIn("['result']",native.source());self.assertIn('len(catalog[\'selected\'])!=12',native.source())
        self.assertIn('test ! -e /home/mini/schubert-nk-pgpt/transfer/PG4942-native-input-v1.tar',native.source())

    def test_redaction_exact_current_and_no_acceptance_promotion(self):
        raw=public.source()
        for text in ("n['currentNativeStreams'] == 10","n['validatedNativePoints'] == 12",'PG4942-native-v1','3761','551','1647',"'PMDRaw': 1655","'CheckstyleRaw': 0","'acceptedLeafDelta': 0","'effortPercent': None",'7fffab57a567914956b66452e5e54388642efdec'):
            self.assertIn(text,raw)
        self.assertNotIn('PG4926-native-v1',raw)
        self.assertEqual(native.SOURCE,public.SOURCE)
        for path in (catalog.__file__,native.__file__,public.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
