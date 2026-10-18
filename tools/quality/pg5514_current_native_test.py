"""Current296 native provenance/generation/count guards; fixtures issue no VM authority."""
import copy
import inspect
import json
import unittest
from pyflakes.api import check,checkPath
import pg5504_current_owned_test as owned_fixture
import pg5508_current_native_catalog as catalog
import pg5510_current_native_qualified as native
import pg5512_current_native_public as public


class Native(unittest.TestCase):
    def test_prerequisites_refuse_foreign_partial_and_boolean_exit(self):
        post={'actualExit':0,'productionSource':native.SOURCE,'all24UnchangedTwice':True,
            'allTenUnitsKernelEmpty':True,'normalNewMetadataScopes':True,'allClientAdvisoryFlock0':True}
        term={'productionSource':native.SOURCE,'genuineRootDone':True,'completionCode':10}
        catalog.prerequisites(post,term)
        for key,value in(('actualExit',False),('actualExit',1),('productionSource','foreign'),('all24UnchangedTwice',False),('allTenUnitsKernelEmpty',False),('normalNewMetadataScopes',False),('allClientAdvisoryFlock0',False)):
            with self.subTest(key=key),self.assertRaises(ValueError):catalog.prerequisites({**post,key:value},term)
        for key,value in(('productionSource','foreign'),('genuineRootDone',False),('completionCode',0)):
            with self.assertRaises(ValueError):catalog.prerequisites(post,{**term,key:value})

    def test_fixture_only_emission_retains_all88_before_and_ten_new_points(self):
        args=owned_fixture.Owned().fixture();values=catalog.role.emit(*args)
        raw=catalog.catalog_source(values['pg5496_parent_receipt.py'],catalog.role.admission.live(),args[0][2]['endMonotonicUs'])
        self.assertEqual(check('SEALS={}\n'+raw,'<nonruntime source-emission native catalog>'),0)
        for marker in(native.SOURCE,catalog.role.BOM,catalog.role.admission.ONCE,catalog.role.admission.before(),
            'all88BeforeCopiesPreserved',"'oldSourceNativeImported':False",'==88',"'pg5496-native-stop-v1'"):
            self.assertIn(marker,raw)
        self.assertNotIn('all80BeforeCopiesPreserved',raw)
        self.assertIn("'replayAllowed':False",inspect.getsource(catalog.TEMPLATE.main))

    def test_actual3896_562_all1664_original_qualification_not_old3791(self):
        full=json.loads((native.W/native.FULL/'manifest.safe.json').read_bytes());q=native.qualify(full)
        self.assertEqual(tuple(q[k]for k in('tests','suites','mainClasses')),(3896,562,1664))
        for key,value in(('tests',3791),('suites',553),('mainClasses',1650),('productionSource','foreign'),
            ('oldNativeImported',True),('staticSixModules',1),('FESFlakyNotRun',1),('F03Accepted',True),('formalAccepted',True)):
            wrong=copy.deepcopy(full);wrong['result'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):native.qualify(wrong)

    def test_complete_server_and_new_only_transport_preserve_hash_join(self):
        raw=native.server();coordinates=native.previous.previous.previous.transport.prior.previous.entry().__globals__['coordinates']
        complete='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="'+'a'*64+'"\n'+inspect.getsource(coordinates)+'\n'+raw
        self.assertEqual(check(complete,'<all1664 same-source native server>'),0)
        for marker in('PG5414-six-v1','source-full-PG5414','PG5510-native-v1',native.SOURCE,"full['tests'] == 3896",
            "len(v['selected']) == 10",'len(streams) == 9',"qualified['jarHashes'][m]","qualified['modules'][m]['coverageXmlSha256']",
            "result['classByteMismatch'] == 0",'NativePointDominanceTest',"'oldNativeImported': False","'formalAccepted': False"):
            self.assertIn(marker,raw)
        for old in('PG5072','PG4968','3791','1650'):self.assertNotIn(old,raw)
        transport=native.source()
        for marker in(native.FULL,catalog.SLOT,native.SLOT,
            'test ! -e /home/mini/schubert-nk-pgpt/transfer/PG5510-native-input-v1.tar',
            'test ! -e /home/mini/schubert-nk-pgpt/runs/PG5510-native-v1'):self.assertIn(marker,transport)

    def test_public_history_preserved_redaction_and_current_F03_not_accepted(self):
        raw=public.source()
        for marker in('PG5510-native-v1','3896','562','1664',"'PMDRaw': 1647","'CheckstyleRaw': 0","'F03Accepted': False",
            "'acceptedLeafDelta': 0","'effortPercent': None","'automaticSourceRebinding': False",
            '7fffab57a567914956b66452e5e54388642efdec','base.redact_report',"native['manifestSha256']","n['xmlHashes'][module]"):
            self.assertIn(marker,raw)
        self.assertNotIn('PG5072-native-v1',raw)
        for item in(catalog,native,public):self.assertEqual(checkPath(item.__file__),0)
        self.assertEqual(checkPath(__file__),0)


if __name__=='__main__':unittest.main()
