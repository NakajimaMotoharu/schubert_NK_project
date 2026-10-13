import ast
import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as seal_schema
import pg2458_question_current_owned_sources as owned
import pg2460_question_current_owned_dispatch as dispatch
import pg2464_question_current_owned_post as stopped
import pg2466_question_current_native_catalog as catalog
import pg2468_question_current_native_qualification as qualification


class CurrentClosing(unittest.TestCase):
    def live(self):
        return json.loads((W/'pg2450-question-current-live-binding-v1/manifest.safe.json').read_bytes())

    def test_complete_owned_graph_bind_receipt_last_not_positive_substitution(self):
        state=json.loads((W/'pg2364-current-resume-terminal-v1/manifest.safe.json').read_bytes())['parentState']
        graph=owned.emit(owned.prior.context(),self.live(),state,{})
        self.assertEqual(15,len(graph))
        body='\n'.join(v for n,v in graph.items()if n not in {'pg2458_parent_receipt.py','pg2458_warning_parent_projection.py'})
        for text in [owned.TOOLS,owned.SOURCE,owned.BOM,'0.1.0-PG2428','Pg387TrustedDeployment.STEM="pg2428"','pg2456-question-current-full-seal-v1']:
            self.assertIn(text,body)
        for text in ['3d69f5af','pg2374','Pg2374','pg2126']:self.assertNotIn(text,body)
        receipt=graph['pg2458_parent_receipt.py']
        self.assertIn(self.live()['binding']['activation'],receipt)
        self.assertIn("binding.get('activation') == 'e1429ac8-f3dd-4e8c-83d2-1926c4ba8440'",receipt)

    def test_actual_dispatch_abi_prequal_before_fresh_proof_before_once_stop(self):
        for text in [dispatch.GUEST,dispatch.ARCHIVE,'b2d6f605-61cf-425f-8fbd-12d606f6ee66',owned.SOURCE,owned.BOM,'PG2428']:
            self.assertIn(text,dispatch.STAGE)
        raw=dispatch.run_source();compile(raw,'<whole current owned entry>','exec')
        for text in ['pg2459-frozen-v1.safe.json','pg2460-stage-v1.exit','pg2461-parent-two-source-prequalification-v1','pg2462-newboot-pre-stop-full-v1','Pg2458NativeStop stop']:
            self.assertIn(text,raw)
        self.assertLess(raw.index('PARENT_PREQUAL'),raw.index('fresh = post_payload()'))
        self.assertLess(raw.index('fresh = post_payload()'),raw.index("'Pg2458NativeStop stop'"))

    def test_complete_independent_stopped_post_retained_original_and_no_replay(self):
        fixture=json.loads((W/'pg2281-current-signed-owned-post-v2/manifest.safe.json').read_bytes())
        seals={n:fixture['proofHashes'][n]['sha256']for n in seal_schema.previous.SEALS}
        raw=stopped.emit(seals,owned.prior.context(),self.live())
        self.assertEqual(0,check('HASHES={}\nRECEIPT="actual"\n'+raw,'<whole stopped fixture>'))
        for text in [owned.SOURCE,owned.BOM,owned.TOOLS,'pg2456-question-current-full-seal-v1',stopped.SLOT,'PG2428']:
            self.assertIn(text,raw)
        for n in ast.walk(ast.parse(raw)):
            if isinstance(n,ast.List):
                self.assertFalse({'start','stop','restart','reload','daemon-reload','reset-failed'}&{getattr(v,'value',None)for v in n.elts if isinstance(v,ast.Constant)})

    def test_whole_current_catalog_old16_kept_not_imported_and_nine_latest(self):
        b=self.live()['binding'];raw=catalog.catalog_source("def completed(*args):raise ValueError('body fixture only')",b,b['start']+1800000000)
        self.assertEqual(0,check('SEALS={}\n'+raw,'<complete point fixture>'))
        for text in ['len(old)==16','priorOldSourceSixteenCopiesPreserved','priorOldSourcePointsImported',
            'pg2448-question-current-noargs-once-v1','pg2458-native-stop-v1',owned.SOURCE,
            "issued['ordinaryNoargs']is True",'ROOT_START='+str(b['start'])]:self.assertTrue(text in raw,text)
        for text in ['PG2468-native-v1','source-full-PG2404','runs/PG2404-six-v1','3637',owned.SOURCE,
            'classByteMismatch','NativePointDominance','len(streams)==9','inspectorLatestClosingOnly']:
            self.assertIn(text,qualification.server())
        self.assertIn('pg2405-question-jdbc-full-qualified-v1',qualification.source())
        self.assertEqual(qualification.server(),qualification.entry().__globals__['CODE'])
        for text in ['PG2300','3635','0fd734','PG2384']:self.assertNotIn(text,qualification.server())


if __name__=='__main__':unittest.main()
