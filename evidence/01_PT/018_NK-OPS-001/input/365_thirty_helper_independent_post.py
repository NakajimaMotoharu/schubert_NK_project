"""Independent finite metadata-index verification; source pins are not compiler/Unit qualification."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=R.parent/'pgpt-runs/PG379/pg23196-thirty-helper-identifier-parse-v1';ip=B/'evidence/PG23194-thirty-helper-receipt-audit-v1/manifest.json';O=B/'evidence/PG23200-thirty-helper-independent-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());assert not O.exists();m=load(ip);assert m['actualExit']==0 and m['selectedHelpers']==30 and len(m['sourceHashPins'])==len(m['helperRows'])==30 and m['sourceIdentifierParsedFiles']==957 and m['statusCounts']=={'CURRENT_SOURCE_PIN_ONLY_NOT_COMPILER_PROOF':30};assert m['originalTestsCompiled']==m['productTestsExecuted']==m['compilerReferencesFollowed']==0 and m['sourceOrTestAbsenceInferred'] is False and m['protectedSourceCallerGraphComplete'] is False;assert not m['unsupportedJsonFiles'];tool=m['ownParser'];assert sha(R/tool['path'])==tool['sha256']==tool['mirrorSha256'];assert {str(p.relative_to(P/'classes')):sha(p) for p in (P/'classes').rglob('*.class')}==tool['classes']
for label,stage in [('own-javac',tool['compileStage']),('parse',tool['parseStage'])]:
 assert stage['actualExit']==0 and not stage['timedOut']
 for stream in ['stdout','stderr']:assert sha(P/(label+'.'+stream))==stage[stream+'Sha256']
assert not re.search(r"Initializing '(?:dev/codex/schubert/nk/|dev\.codex\.schubert\.nk\.)",(P/'class-init.stdout').read_text());source=(R/tool['path']).read_text();assert 'task.parse()' in source and 'task.analyze()' not in source and 'task.call()' not in source and 'List.of("-proc:none", "--release", "25"' in source
names=(P/'sources.txt').read_text().splitlines();assert len(names)==957 and all(Path(n).name not in set(m['excludedProtectedNamesBeforeIO']) and '/src/test/java/' in n and n.startswith('src/') for n in names);references={n:[] for n in m['sourceHashPins']};simple={Path(n).stem:n for n in references}
for line in (P/'parse.stdout').read_text().splitlines():
 path,found=line.split('\t');assert path in names
 for name in found.split(','):
  helper=simple[name]
  if path!=helper:references[helper].append(path)
seen={};recordCount=0
for row in m['helperRows']:
 n=row['helper'];h=row['currentSourceSha256'];assert h==m['sourceHashPins'][n]==sha(R/n)==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n],cwd=R)).hexdigest();assert row['observedSourceIdentifierCallers']==sorted(set(references[n])) and row['protectedCallerCompletenessUnknown'] and row['reflectionStringGraphNotAssessed'];assert row['declaredCurrentClassReceipts']==row['currentCompilerReferenceReceipts']==0 and row['currentPinReceiptCount']>0
 for record in row['records']:
  ref=record['manifest'];name=ref['path'];assert name.startswith('evidence/01_PT/') and name.endswith('/manifest.json') and '/private/' not in name
  if name not in seen:
   assert sha(R/name)==ref['sha256'];seen[name]=load(R/name)
  value=seen[name]
  for binding in record['sourceBindings']:
   cursor=value
   for key in binding['field'].split('/')[1:]:cursor=cursor[int(key)] if isinstance(cursor,list) else cursor[key]
   assert cursor[n]==binding['sourceSha256'] and binding['currentSourceEqual']==(cursor[n]==h)
  assert not record['declaredHelperClassHashes'] and not record['compilerReferencesNotDereferenced'];recordCount+=1
# Explicitly refuse the tempting source-pin/exit0=>compiled inference.
def compiler_qualified(row):return row.get('sourceInputCurrent') is True and row.get('actualCompilerExit')==0 and bool(row.get('boundCurrentClassHashes'))
neg=0
for bad in [dict(sourceInputCurrent=True),dict(sourceInputCurrent=True,actualCompilerExit=0),dict(sourceInputCurrent=False,actualCompilerExit=0,boundCurrentClassHashes={'public':'0'*64})]:assert not compiler_qualified(bad);neg+=1
O.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],observerHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),originalAudit=dict(path=str(ip.relative_to(R)),sha256=sha(ip)),helpers=30,currentSourcePinsVerified=30,supportedInputReceiptOccurrences=recordCount,distinctMatchingPublicReceipts=len(seen),parsedAllowedTestSourceNames=957,protectedSourcesExcluded=2,protectedCallerGraphComplete=False,reflectiveRuntimeGraphComplete=False,allThirtyCompilerBinding='UNRESOLVED_BY_SUPPORTED_PUBLIC_RECEIPT_SCHEMA_NOT_UNIMPLEMENTED',metadataFalseQualificationNegatives=neg,originalTestsCompiled=0,productTestsExecuted=0,actualProductProcessActions=0,productClassesInitialized=0,privateRawOrArchiveAccess=0,originalUnitSuccessPreserved=True,newProductTests=0,newSourceProofs=0,newAcceptance=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,next='Inspect narrowly the existing public compiler receipt PG18554 fixture-setup and a representative legacy six-module compiler recipe/terminal. Source30 current pins often belong to whole-source snapshots; do not infer Test compilation. Seek compiler target/actualexit/output declaration without reading protected source/archive/private raw or rerunning helpers. Use explicit remaining applicability table rather than blanket failure/pass.',verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,helpers=30,inputReceiptOccurrences=recordCount,distinctPublicReceipts=len(seen),compilerQualification='UNRESOLVED_NOT_ABSENT',negative3=True,UnitReplays=0,manifestSha256=sha(O/'manifest.json'))))
