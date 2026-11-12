"""Reproducible BUG2745 pure metadata regression; no events or product files are changed."""
from pathlib import Path
import copy,hashlib,json,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';sys.path.insert(0,str(R/'tools/quality'));from pmo_group_context import validate_implementation_artifacts
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=ld(R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json')['artifacts'];old=ld(B/'input/2030_backup_fatal_source_pg_start.json');pin=sha(B/'input/2030_backup_fatal_source_pg_start.json');cases=[]
def reject(name,c):
 try:validate_implementation_artifacts(c,rows)
 except ValueError as e:cases.append(dict(case=name,rejected=True,reason=str(e)));return
 raise AssertionError(name)
reject('OLD_CLONE_MISSING_ARTIFACT_BINDING',old);good=copy.deepcopy(old);good['implementationArtifactPaths']=['src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/'+n+'.java' for n in ['file/BackupArtifactVerifier','file/BackupManifestReader','backup/BackupCommitService']];reject('CLONED_WRONG_WBS_WITH_EXPLICIT_ARTIFACTS',good);good['wbsLeafIds']=['WBS-P017-05'];validate_implementation_artifacts(good,rows);cases.append(dict(case='EXPLICIT_CORRECTED_PROJECTION',passed=True));bad=copy.deepcopy(good);bad['implementationArtifactPaths']=['src/unregistered/Example.java'];reject('UNREGISTERED_ARTIFACT',bad);bad=copy.deepcopy(good);bad['implementationArtifactPaths'].append(bad['implementationArtifactPaths'][0]);reject('DUPLICATE_ARTIFACT',bad)
for n in ['1984_next4_host_eligibility_start.json','1987_api_config7_start.json','1996_router18_start.json','2005_http_metric28_start.json','2015_backup_values_eligibility_start.json','2018_backup_manifest16_start.json','2028_p01705_original_start.json','2035_closed_host_tool_start.json']:
 validate_implementation_artifacts(ld(B/'input'/n),rows);cases.append(dict(case='NONAPPLICABLE_NONPRODUCTION_IMPLEMENTATION_'+n,passed=True))
assert sha(B/'input/2030_backup_fatal_source_pg_start.json')==pin
if __name__=='__main__':
 O=B/'evidence'/sys.argv[1];assert not O.exists();O.mkdir();v=dict(actualExit=0,cases=cases,pureChecks=len(cases),oldConfigUnchanged=True,oldConfigSha256=pin,productTestsExecuted=0,eventsWritten=0,sourceFilesRead=0,verifierSha256=sha(Path(__file__).resolve()),guardSha256=sha(R/'tools/quality/pmo_group_context.py'));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,pureChecks=len(cases),productTestsExecuted=0))
