import copy
import json
import unittest
from pyflakes.api import checkPath
import pg5596_current_factory_scope as entry


class CurrentScope(unittest.TestCase):
    def fixtures(self):
        load=lambda path:json.loads(path.read_bytes())
        scope=load(entry.BASE/'PG5422-factory-whole-scope-v1/manifest.json')
        partition=load(entry.BASE/'PG5410-scope-classification-process-query-v1/manifest.json')
        readonly=load(entry.BASE/'PG5418-readonly-ownership-bytecode-v1/manifest.json')
        monitor=load(entry.W/'pg5568-monitor-bytecode-v3/manifest.safe.json')
        selected=load(entry.W/'pg5566-private-monitor-green-v3/manifest.safe.json')
        # Metadata-only fixture: not an actual whole qualification result.
        whole={'productionSource':entry.SOURCE,'sourceSnapshot':entry.SOURCE,'tests':3905,'suites':563,'mainClasses':1664,
            'FESFlakyNotRun':0,'staticSixModules':0,'allOriginalCaseIdentitiesRetained':True,'allSixFormatBeforeAnyPt':True,
            'oldNativeImported':False,'formalAccepted':False,'allPhysicalMainSha256':copy.deepcopy(selected['physicalMain']['sha256'])}
        return whole,scope,partition,readonly,monitor,selected

    def test_all237_current_source_partition_and_exact_readonly_classes(self):
        value=entry.validate(*self.fixtures())
        self.assertEqual(value['original237Partition'],{'FIXED_LIMITED':236,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':0})
        self.assertEqual(len(value['currentOriginalFactorySourceHashes']),68)
        self.assertEqual(value['readonlyCandidatesUnknown'],0);self.assertFalse(value['newSourceNativeQualified'])
        self.assertFalse(value['wholeHorizontalComplete'])

    def test_wrong_source_incomplete_coverage_proof_or_actual_class_refused(self):
        for kind in('source','tests','format','native','readonly','main','monitor'):
            with self.subTest(kind=kind):
                whole,scope,partition,readonly,monitor,selected=self.fixtures()
                if kind=='source':whole['productionSource']='old'
                if kind=='tests':whole['tests']=3904
                if kind=='format':whole['allSixFormatBeforeAnyPt']=False
                if kind=='native':whole['oldNativeImported']=True
                if kind=='readonly':readonly['classHashes'][next(iter(readonly['classHashes']))]['classSha256']='0'*64
                if kind=='main':whole['allPhysicalMainSha256'].pop(next(iter(whole['allPhysicalMainSha256'])))
                if kind=='monitor':monitor['actualSelectedCases']=71
                with self.assertRaises(ValueError):entry.validate(whole,scope,partition,readonly,monitor,selected)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
