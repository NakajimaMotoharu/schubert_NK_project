import hashlib
import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5420_ownership_whole_public as entry


class WholePublication(unittest.TestCase):
    def test_complete_current3896_only_projection_preserves_original_xml_policy(self):
        raw=entry.export_source()
        self.assertIn('len(all_cases) != 3896',raw);self.assertIn('source-full-PG5414',raw)
        main=entry.main_source()
        for literal in ("r['tests'] == 3896","r['suites'] == 562","r['mainClasses'] == 1664",
            'pg5416-ownership-whole-qualified-v2','pg5420-ownership-case-projection-v1'):
            self.assertIn(literal,main)
        self.assertNotIn('mvn',main)
        raw=('import hashlib,json,re\nfrom pathlib import Path\nimport xml.etree.ElementTree as ET\n'+
            inspect.getsource(entry.previous.previous.qualify_snapshot)+'\n'+
            inspect.getsource(entry.previous.previous.project_xml)+'\n'+raw+'\nprint(json.dumps(export({})))\n')
        self.assertEqual(check(raw,'<original3896 safe projection>'),0)

    def test_new_test_id_labels_never_replace_actual_whole_xml_pass(self):
        cases=[{'class':'fixture.C','caseNameSha256':hashlib.sha256(str(i).encode()).hexdigest(),
            'testId':f'whole{i}','result':'PASS_ORIGINAL_XML','sourceXml':'fixture.xml','xmlSha256':'a'*64} for i in range(3896)]
        labels={'productionCandidateSource':entry.SOURCE,'actualExit':0,'tests':1164,
            'cases':[{'class':'fixture.C','method':str(i),'testId':f'independent{i}','newIndependentCase':True} for i in range(82)]}
        new=[('fixture.C',str(i)) for i in range(82)]
        self.assertEqual(len(entry.new_case_trace(cases,labels,new)),82)
        wrong=dict(labels,productionCandidateSource='foreign')
        with self.assertRaises(ValueError):entry.new_case_trace(cases,wrong,new)
        wrong=[dict(row) for row in cases];wrong[0]['result']='UNKNOWN'
        with self.assertRaises(ValueError):entry.new_case_trace(wrong,labels,new)
        with self.assertRaises(ValueError):entry.new_case_trace(cases[:-1],labels,new)
        with self.assertRaises(ValueError):entry.new_case_trace(cases,labels,new[:-1])
        wrong=dict(labels,cases=[dict(row) for row in labels['cases']]);wrong['cases'][0]['observedInvocation']='0(Path)'
        with self.assertRaises(ValueError):entry.new_case_trace(cases,wrong,new)
        cls='dev.codex.schubert.nk.batch.file.MorningBackupRequestPublicationTest'
        name='mbpub008CompleteOwnerTakesOverDirectoryExactlyOnce'
        aliascases=[dict(row) for row in cases];aliaslabels=dict(labels,cases=[dict(row) for row in labels['cases']]);aliasnew=list(new)
        aliascases[0].update({'class':cls,'caseNameSha256':hashlib.sha256((name+'(Path)').encode()).hexdigest()})
        aliaslabels['cases'][0].update({'class':cls,'method':name,'observedInvocation':name+'(Path)'})
        aliasnew[0]=(cls,name)
        self.assertEqual(len(entry.new_case_trace(aliascases,aliaslabels,aliasnew)),82)
        for path in (entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
