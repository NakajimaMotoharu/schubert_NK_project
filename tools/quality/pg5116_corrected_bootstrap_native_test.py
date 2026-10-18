"""All1650 same-source factory, both independent point dominances, redaction/no promotion."""
import inspect
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg5110_corrected_bootstrap_catalog as catalog
import pg5112_corrected_bootstrap_native as native
import pg5114_corrected_bootstrap_public as public


class CurrentNative(unittest.TestCase):
    def test_actual_new20_catalog_and_full_metadata_namespace(self):
        prior,points=catalog.prerequisites()
        self.assertEqual(10,len(prior['selected']))
        self.assertEqual(2,len(points))
        self.assertTrue(points[0]['relative'].endswith('.closing.exec'))
        self.assertTrue(points[1]['relative'].endswith('.terminal.exec'))
        raw=catalog.payload()
        self.assertEqual(0,check(raw,'<complete exact current12point catalog>'))
        for text in ("'currentPhysicalNative':88","len(points)==12",catalog.post.role.SOURCE,"'oldSourceNativeImported':False"):
            self.assertTrue(text in raw,text)

    def test_failed_foreign_or_uncaptured_post_refuses_before_catalog(self):
        real=Path.read_bytes;where=catalog.post.role.W/catalog.post.SLOT/'manifest.safe.json'
        original=json.loads(real(where))
        for kind in ('foreign','failed','uncaptured','wrongphysical','bool'):
            value=json.loads(json.dumps(original))
            if kind=='foreign':value['source']='foreign'
            if kind=='failed':value['actualExit']=1
            if kind=='uncaptured':value['result']['capturedNormal20VerifiedBeforeCurrent']=False
            if kind=='wrongphysical':value['result']['nativePhysicalFiles']=87
            if kind=='bool':value['actualExit']=False
            with self.subTest(kind=kind),patch.object(Path,'read_bytes',lambda p:json.dumps(value).encode()if p==where else real(p)):
                with self.assertRaises(ValueError):catalog.prerequisites()

    def test_complete_current_server_both_pairs_and_original_whole_paths(self):
        raw=native.server()
        coordinates=native.previous.previous.previous.transport.prior.previous.entry().__globals__['coordinates']
        complete='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="'+('a'*64)+'"\n'+inspect.getsource(coordinates)+'\n'+raw
        self.assertEqual(0,check(complete,'<all1650 two-pair native server>'))
        for text in ('PG4968-six-v1','PG5112-native-v1','3791',"len(v['selected']) == 12",'NativePointDominanceTest',
                     "'currentNativeStreams': 10", "'validatedNativePoints': 12", "'bootstrapCapturedNormal20Qualified': True",
                     "'oldNativeImported': False", "'formalAccepted': False",'bootstrap_early_index','early_index'):
            self.assertTrue(text in raw,text)
        for old in ('PG5072','PG4926','PG4844','3761','1647'):self.assertTrue(old not in raw,old)
        transport=native.source()
        self.assertTrue("len(catalog['selected'])!=12"in transport)
        self.assertTrue("['result']"in transport)
        self.assertTrue('test ! -e /home/mini/schubert-nk-pgpt/transfer/PG5112-native-input-v1.tar'in transport)

    def test_current_redaction_and_historical_acceptance_not_rebound(self):
        raw=public.source()
        for text in ("n['currentNativeStreams'] == 10", "n['validatedNativePoints'] == 12",'PG5112-native-v1',
                     '3791','553','1650',"'PMDRaw': 1657", "'CheckstyleRaw': 0", "'F03Accepted': False",
                     "'acceptedLeafDelta': 0", "'effortPercent': None",'7fffab57a567914956b66452e5e54388642efdec','base.redact_report'):
            self.assertTrue(text in raw,text)
        self.assertEqual(native.SOURCE,public.SOURCE)
        for path in (catalog.__file__,native.__file__,public.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
