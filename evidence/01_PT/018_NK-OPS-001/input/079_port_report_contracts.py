"""Independent metadata contracts, no Product imports or execution."""
from pathlib import Path
import copy,datetime,hashlib,io,json,platform,unittest
from pmo_port_report import project_port,render_port

TARGET='dev/codex/schubert/nk/sample/Thing'
EXPECT=dict(source='1'*40,tests=2,physical=1,four=[9,2,1,4])
def fixture():
    return dict(actualExit=0,failures=0,errors=0,skipped=0,aborted=0,tests=2,testClasses=1,source='1'*40,productionCoreMain='2'*40,selectedTestMethods=[['sample.Contract','first'],['sample.Contract','second']],oldExecUnion=False,manualCoverageExclusions=[],heldFourProbeHits={n:0 for n in ['a','b','c','d']},physicalHashes={TARGET:'a'*64},coverage={TARGET:{k:dict(covered=v,missed=0) for k,v in [('LINE',9),('METHOD',2),('CLASS',1),('BRANCH',4),('INSTRUCTION',30)]}},abstractInterfacesNoExecutableMethods=[],compilerGeneratedNoCodeClasses=[])
class Contracts(unittest.TestCase):
    def test_literal_counters_and_method_identity_projection(self):
        p=project_port(fixture(),EXPECT);self.assertEqual(dict(LINE=9,METHOD=2,CLASS=1,BRANCH=4),p['fourCounters']);self.assertEqual(2,p['tests']);self.assertFalse(p['qualificationTransferred'])
    def test_bad_or_missing_terminal_counts_never_pass(self):
        for k in ['actualExit','failures','errors','skipped','aborted']:
            for value in [1,None,False]:
                m=fixture();m[k]=value
                with self.assertRaises(ValueError):project_port(m,EXPECT)
    def test_count_mismatch_duplicate_and_missing_test_identities_reject(self):
        for value in [True,1,3,None]:
            m=fixture();m['tests']=value
            with self.assertRaises(ValueError):project_port(m,EXPECT)
        for cases in [None,[],[['sample.Contract','first']]*2]:
            m=fixture();m['selectedTestMethods']=cases
            with self.assertRaises(ValueError):project_port(m,EXPECT)
    def test_missed_branch_instruction_or_missing_class_is_not_full_coverage(self):
        for key in ['LINE','BRANCH','INSTRUCTION']:
            m=fixture();m['coverage'][TARGET][key]['missed']=1
            with self.assertRaises(ValueError):project_port(m,EXPECT)
        for counters in [{},dict(LINE=dict(covered=9,missed=0))]:
            m=fixture();m['coverage'][TARGET]=counters
            with self.assertRaises(ValueError):project_port(m,EXPECT)
    def test_wrong_source_union_exclusion_and_held_hits_reject(self):
        for key,value in [('source','3'*40),('source','bad'),('productionCoreMain',None),('oldExecUnion',True),('manualCoverageExclusions',['Thing']),('heldFourProbeHits',{'a':1,'b':0,'c':0,'d':0})]:
            m=fixture();m[key]=value
            with self.assertRaises(ValueError):project_port(m,EXPECT)
    def test_explicit_no_code_and_zero_branch_are_not_invented_percentages(self):
        m=fixture();m['coverage'][TARGET]['BRANCH']['covered']=0;p=project_port(m,dict(EXPECT,four=[9,2,1,0]));self.assertEqual(0,p['fourCounters']['BRANCH'])
        m['physicalHashes'][TARGET+'$1']='b'*64;m['coverage'][TARGET+'$1']={}
        with self.assertRaises(ValueError):project_port(m,dict(EXPECT,physical=2,four=[9,2,1,0]))
        m['compilerGeneratedNoCodeClasses']=[TARGET+'$1'];p=project_port(m,dict(EXPECT,physical=2,four=[9,2,1,0]));self.assertEqual([TARGET+'$1'],p['noCodeClasses'])
    def test_report_has_actual_numbers_and_no_unselected_sensitive_fields(self):
        m=fixture();m['credential']='MUST-NOT-COPY';text=render_port(project_port(m,EXPECT),'evidence/01_PT/program/evidence/run/manifest.json','a'*64,'evidence/01_PT/program/spec.md');self.assertIn('選択2件',text);self.assertIn('BRANCH=4',text);self.assertNotIn('MUST-NOT-COPY',text)
        with self.assertRaises(ValueError):render_port(project_port(m,EXPECT),'/private/raw','a'*64,'evidence/01_PT/program/spec.md')
    def test_saved_router_manifest_exact_reference_without_reexecution(self):
        path=Path('evidence/01_PT/015_NK-WEB-001/evidence/PG20514-internal-error-router-style-ten-v1/manifest.json');self.assertEqual('51a2ed29f749c8a33dc9354a84c8900d14018ca14f067e0935dc8c8fd79798b7',hashlib.sha256(path.read_bytes()).hexdigest());m=json.loads(path.read_text());p=project_port(m,dict(source='370905244dc803d65826474aa3dfd7062e5ef142',tests=10,physical=1,four=[28,4,1,8]));self.assertEqual(10,p['tests']);self.assertEqual(28,p['fourCounters']['LINE'])
if __name__=='__main__':
    out=Path('evidence/01_PT/018_NK-OPS-001/evidence/PG20526-port-projection-metadata-v1');assert not out.exists();out.mkdir();stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts));(out/'checks.stdout').write_text(stream.getvalue());assert result.testsRun==8 and result.wasSuccessful();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();files={'checks.stdout':sha(out/'checks.stdout')};m=dict(metadataOnly=True,actualExit=0,metadataTests=8,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),productionTests=0,newSourceProofs=0,newAcceptance=0,inputHashes={p:sha(p) for p in ['tools/quality/pmo_port_report.py',__file__]},files=files,terminalObservedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),os=platform.system(),python=platform.python_version(),command='env PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/079_port_report_contracts.py');(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(metadataTests=8,Product=0,actualExit=0,manifestSha256=sha(out/'manifest.json'))))
