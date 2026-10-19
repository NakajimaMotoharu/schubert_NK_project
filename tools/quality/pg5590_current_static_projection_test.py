import copy
import json
import unittest
from pyflakes.api import check,checkPath
import pg5590_current_static_projection as entry


class CurrentFindingBindings(unittest.TestCase):
    def fixtures(self):
        maps=entry.load_fixed(*entry.PREPARED['map']);fields=entry.load_fixed(*entry.PREPARED['fields'])
        raw=json.loads((entry.BASE/'PG5560-snapshot-static-findings-v1/manifest.json').read_bytes())
        rows=[copy.deepcopy(r)for r in raw['findings']if r['rule']in('UseConcurrentHashMap','AvoidFieldNameMatchingMethodName')]
        index={(r['sourcePath'],r['beginline']):r for r in fields['fields']}
        for row in rows:
            if row['rule']=='AvoidFieldNameMatchingMethodName':row['sourceSha256']=index[(row['sourcePath'],row['beginline'])]['currentSourceSha256']
        # Deliberately synthetic XML references for pure tool tests only. Not an
        # actual qualification, public result, or production-coverage input.
        cases=[{'class':'fixture.'+name,'result':'PASS_ORIGINAL_XML','testId':'SYNTHETIC-'+name,'xmlSha256':'e'*64}for name in {r['relatedTestClass']for r in maps['sourceContexts']}]
        selected=json.loads((entry.W/'pg5566-private-monitor-green-v3/manifest.safe.json').read_bytes())
        return rows,cases,{'allPhysicalMainSha256':selected['physicalMain']['sha256']},maps,fields

    def test_exact_21_contexts_and_64_inspected_not_waived(self):
        rows,cases,whole,maps,fields=self.fixtures();entry.bind_prepared(rows,cases,whole,maps,fields)
        self.assertEqual(sum(r['status']=='CONTEXT_NOT_APPLICABLE'for r in rows),21)
        inspected=[r for r in rows if r['status']=='INSPECTED_PENDING_DISPOSITION']
        self.assertEqual(len(inspected),64);self.assertTrue(all(r['dispositionAccepted']is False for r in inspected))
        self.assertEqual(sum(r['compilerFacts']['ownerKind']=='ENUM'for r in inspected),48)
        self.assertEqual(sum(r['compilerFacts']['ownerKind']=='THROWABLE'for r in inspected),16)

    def test_unknown_missing_or_changed_context_cannot_inherit_review(self):
        for kind in('coordinate','hash','missing','class','oldcase','sourceMirror'):
            with self.subTest(kind=kind):
                rows,cases,whole,maps,fields=self.fixtures()
                if kind=='coordinate':rows[0]['beginline']='999999'
                if kind=='hash':rows[0]['sourceSha256']='0'*64
                if kind=='missing':rows.pop()
                if kind=='class':whole['allPhysicalMainSha256'][next(iter(maps['witnesses'].values()))['actualCompiledClassSha256'].keys().__iter__().__next__()]='0'*64
                if kind=='oldcase':cases[0]['result']='SKIPPED'
                if kind=='sourceMirror':fields['all849SourceHashes'][next(iter(fields['all849SourceHashes']))]='0'*64
                with self.assertRaises(ValueError):entry.bind_prepared(rows,cases,whole,maps,fields)

    def test_no_unknown_whole_or_inferred_success(self):
        with self.assertRaises(ValueError):entry.project({}, {}, [], {'productionSource':'old'}, {}, {})
        with self.assertRaises(ValueError):entry.suite_refs([],['MissingTest'])
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)
        raw=entry.collect_source();self.assertEqual(check(raw,'<original report metadata>'),0)
        self.assertIn('runs/PG5578-monitor-static-v1/pmd.xml',raw)
        self.assertIn('runs/PG5578-monitor-static-input-v1/candidate/',raw)
        self.assertNotIn('PG5424',raw)


if __name__=='__main__':unittest.main()
