import copy
import json
import unittest
from pathlib import Path
from pyflakes.api import checkPath
import pg5594_current_jdbc_review as entry


class ApprovedJdbcBinding(unittest.TestCase):
    def fixtures(self):
        facts=json.loads((entry.W/'pg5592-current-failure-facts-v1/manifest.safe.json').read_bytes())
        old=json.loads((entry.BASE/'PG5560-snapshot-static-findings-v1/manifest.json').read_bytes());rows=[]
        shapes=facts['results']['SourceJdbcClosePrecedenceInventory']['rows']
        for row in old['findings']:
            if Path(row['sourcePath']).stem not in entry.SPECS or row['rule']not in('DoNotThrowExceptionInFinally','AvoidCatchingGenericException'):continue
            if any(f['path']==row['sourcePath']and int(f['firstLine'])<=int(row['beginline'])<=int(f['lastLine'])for f in shapes):rows.append(copy.deepcopy(row))
        # Synthetic qualification/XML fixtures test the reader only. Never
        # exported or claimed as a real whole, native or production PT result.
        cases=[{'class':'dev.codex.schubert.nk.batch.repository.'+name+'Test','caseNameSha256':entry.sha(method.encode()),'testId':'SYNTHETIC-'+name,'xmlSha256':'e'*64,'result':'PASS_ORIGINAL_XML'}for name,method in entry.SPECS.items()]
        whole={'productionSource':entry.SOURCE,'tests':3905,'mainClasses':1664,'FESFlakyNotRun':0,'allPhysicalMainSha256':facts['identity']['physicalMainSha256']}
        original={'source':entry.SOURCE,'actualExit':0,'findings':rows,'pmd':{'ruleCounts':{'AvoidCatchingGenericException':52}}}
        return original,facts,cases,whole,{'basis':'SYNTHETIC_TEST_ONLY'}

    def test_only_exact_26_and_52_typed_closes_accepted(self):
        rows,count=entry.assess(*self.fixtures())
        self.assertEqual(len(rows),78);self.assertEqual(count['jdbcFinallyAssessed'],26)
        self.assertEqual(count['jdbcSecondaryWarningsAssessed'],52);self.assertEqual(count['distinctGenericCatchSites'],26)
        self.assertEqual(count['genericCatchFactsAloneAccepted'],0)
        self.assertTrue(all(r['status']=='REQUIRED_CONTRACT'for r in rows))

    def test_missing_unknown_source_case_main_hash_or_shape_refused(self):
        for kind in('source','case','main','hash','shape','row'):
            with self.subTest(kind=kind):
                original,facts,cases,whole,design=self.fixtures()
                if kind=='source':whole['productionSource']='old'
                if kind=='case':cases[0]['caseNameSha256']='0'*64
                if kind=='main':whole['allPhysicalMainSha256']=dict(whole['allPhysicalMainSha256']);whole['allPhysicalMainSha256'].pop(next(iter(whole['allPhysicalMainSha256'])))
                if kind=='hash':original['findings'][0]['sourceSha256']='0'*64
                if kind=='shape':facts['results']['SourceJdbcClosePrecedenceInventory']['rows'].pop(0)
                if kind=='row':original['findings'].pop(0)
                with self.assertRaises(ValueError):entry.assess(original,facts,cases,whole,design)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
