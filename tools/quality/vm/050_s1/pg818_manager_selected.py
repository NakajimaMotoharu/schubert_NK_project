"""Source-fixed batch-only manager query selected regression; no VM or acceptance."""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent
TESTS={'batch':['LinuxSystemdQueryTest','LinuxSystemdSessionTest','RootStartupContextTest','MorningCompletionRetirementTest','MorningResumeAdmissionTest','MorningServiceReadinessTest','MorningCaddyReadinessTest']}
def source():
 raw=(R/'pg743_closing_selected.py').read_text().replace('pg743-closing-selected-v1','pg818-manager-selected-v1').replace("'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',","'src/schubert-nk-batch',")
 start=raw.index('TESTS = {');end=raw.index('\n\n\ndef main():',start);raw=raw[:start]+'TESTS = '+repr(TESTS)+raw[end:]
 raw=raw.replace("'1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'","'102cdf1d365ab321f74b523237590eee764ae858'");ast.parse(raw);return raw
if __name__=='__main__':
 for name in TESTS['batch']:assert len(list((R.parents[3]/'src/schubert-nk-batch/src/test').rglob(name+'.java')))==1
 exec(compile(source(),'<818 selected known seven suites>','exec'),{'__file__':str(R/'pg818_manager_selected.py'),'__name__':'__main__'})
