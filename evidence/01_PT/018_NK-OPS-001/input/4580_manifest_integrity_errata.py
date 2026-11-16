"""Correct only saved public file-inventory metadata; never rerun a producer or change an original."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import platform
import subprocess
import sys

r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from public_manifest_inventory import inventory,validate
b=r/'evidence/01_PT/018_NK-OPS-001';base=b/'evidence';w=r.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
discovery=load(w/'pg37056-self-hash-discovery.json');assert len(discovery['checked'])==144 and len(discovery['bad'])==2
# Check every source-qualified profile used by the current prior-candidate reviews for this same defect.
refs={}
for prefix in ['PG37050','PG37052','PG37054']:
 for folder in base.glob(prefix+'*'):
  for site in load(folder/'site-decisions.json'):
   for pin in site['priorEvidencePins'].values():refs[pin['path']]=pin['sha256']
referenced=[]
for path,h in refs.items():
 p=r/path;assert path.startswith('evidence/01_PT/018_NK-OPS-001/') and sha(p)==h;v=load(p);files=v.get('files',{})
 assert not isinstance(files,dict) or p.name not in files
 referenced.append(dict(path=path,sha256=h,selfEntryPresent=False,reason='Referenced prior profile/admission does not declare its own filename as an artifact; unrelated historical file availability is not requalified.'))
corrections=[]
for bad in discovery['bad']:
 p=r/bad['path'];assert sha(p)==bad['actual'];v=load(p);declared=v['files'];assert declared[p.name]=='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
 corrected={name:h for name,h in declared.items() if name!=p.name};assert validate(p.parent,corrected)
 try:validate(p.parent,declared)
 except ValueError:pass
 else:raise AssertionError('original self-hash defect must be rejected')
 corrections.append(dict(originalManifest=ref(p),originalSelfEntry=dict(name=p.name,declaredSha256=declared[p.name],status='INVALID_SELF_ENTRY_RETAINED_IMMUTABLY'),correctedFileInventory=corrected,correctedFileCount=len(corrected),allNonselfFileHashesVerified=True,scope='Metadata inventory correction only. Original execution/source/command/XML/counters are retained, no product/static rerun or inferred acceptance.'))
# Source-only repairs preserve every other byte and preserve original already-used slot guards.
repairs=[]
for old,new in [('4532_f03_current287_pmd.py','4581_f03_current287_pmd_exclude_self.py'),('4560_p020_five_main_static.py','4582_p020_five_main_static_exclude_self.py')]:
 oldp=b/'input'/old;newp=b/'input'/new;s=oldp.read_text();oldterm='p.is_file()';at=s.rfind(oldterm);assert at>=0 and 'files=' in s[max(0,at-100):at]
 fixed=s[:at]+"p.is_file() and p.name != 'manifest.json'"+s[at+len(oldterm):]
 assert fixed.replace("p.is_file() and p.name != 'manifest.json'",oldterm,1)==s
 ast.parse(fixed,filename=str(newp));compile(fixed,str(newp),'exec')
 assert not newp.exists();newp.write_text(fixed)
 repairs.append(dict(original=ref(oldp),futureSource=ref(newp),change='Only final file inventory predicate excludes manifest.json, inverse byte-exact',pythonAstAndCompileExit=0,producerExecuted=False,usedSlotGuardsRetained=True,executionStatus='SOURCE_PATCH_ONLY_DO_NOT_REPLAY_ORIGINAL_USED_SLOT'))
out=base/'PG37058-manifest-integrity-errata-v1';assert not out.exists();out.mkdir()
(out/'corrections.json').write_text(json.dumps(corrections,ensure_ascii=False,indent=2)+'\n');(out/'referenced-profile-nonapplicability.json').write_text(json.dumps(referenced,ensure_ascii=False,indent=2)+'\n')
observed=dict(command=['python3','-B','tools/quality/public_manifest_inventory_test.py'],workingDirectory=str(r),observedDirectExecChunkId='ec765b',actualExit=0,observedToolCases=9,stdout='',stderr='.........\n----------------------------------------------------------------------\nRan 9 tests in 0.002s\n\nOK\n',executionStartUTC=None,startMissingIsNotEstimated=True,completionObservationUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),evidenceOrigin='GENUINE_DIRECT_EXEC_RESULT_TRANSCRIPTION_NOT_MACHINE_SIGNED',testsReexecutedForEvidenceCapture=False,sourcePins=[ref(r/'tools/quality/public_manifest_inventory.py'),ref(r/'tools/quality/public_manifest_inventory_test.py')],formalProductionPtCount=0)
(out/'tool-nine-observed-result.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore='01c3b1a34ee01f4a43fcfd1eaa4cc945010675c9',operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),python=platform.python_version(),os=platform.platform(),bug='BUG3151',horizontal='YKT2620',currentCohortChecked=144,currentCohortDefects=2,referencedHistoricalProfilesChecked=len(referenced),referencedHistoricalSelfDefects=0,corrections=ref(out/'corrections.json'),historicalProfiles=ref(out/'referenced-profile-nonapplicability.json'),toolCasesObserved=9,toolObservation=ref(out/'tool-nine-observed-result.json'),futureProducerSourceRepairs=repairs,sourceRuleQualityExclusions=0,originalsUnchanged=True,realProductOrStaticTestsReexecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,files=inventory(out))
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert validate(out,v['files'])
assert all(sha(r/x['path'])==x['sha256'] for x in [item['originalManifest'] for item in corrections])
print(json.dumps(dict(actualExit=0,currentCohort=144,originalDefects=2,referencedProfiles=len(referenced),oldOtherSelfDefects=0,correctedOriginalFileHashes=True,toolCasesObserved=9,producerSourceRepairs=2,producersExecuted=0,newAcceptance=0)))
