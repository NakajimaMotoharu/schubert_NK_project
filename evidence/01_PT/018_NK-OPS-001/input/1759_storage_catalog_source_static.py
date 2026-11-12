"""Only a storage-local graph classifier and three existing checked-catalog guard calls."""
from pathlib import Path
import ast, hashlib, json, subprocess, xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG27680-storage-catalog-source-static-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source='6f7ecb86834295c65753103b48b9740c7e201533'
before=json.loads((B/'evidence/PG27678-storage-catalog-before-v1/before.json').read_text());assert not O.exists()
helper=B/'input/1634_web_security_fatal_source_static.py';tree=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['revert_calls','require_owned']],type_ignores=[]),str(helper),'exec'),globals())
directory=R/'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/OwnedTransferDirectory.java';exception=directory.with_name('StorageIoException.java');old={p:subprocess.check_output(['git','show',source+':'+str(p.relative_to(R))],text=True) for p in [directory,exception]};assert all(sha(p)==before['inputHashes'][str(p.relative_to(R))] for p in old)
new=old[directory];calls=[]
for pattern in before['directoryCatchPatterns']:
 lines=new.splitlines(keepends=True);found=[(i,x) for i,x in enumerate(lines) if pattern in x];assert len(found)==1;i,line=found[0];indent=line[:len(line)-len(line.lstrip())];call=indent+'  StorageIoException.preserveFatal(ex);\n';lines.insert(i+1,call);calls.append(call);new=''.join(lines)
assert revert_calls(new,calls)==old[directory]
reference=R/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionStoreException.java';reftext=reference.read_text();signature='  public static void preserveFatal(Throwable failure) {';method=reftext[reftext.index(signature):reftext.rindex('\n}')]
comment='\n  /** BUG2718/YKT2359: classify transient provider graphs before discarding diagnostics. */\n'
planned={directory:new,exception:old[exception].removesuffix('}\n')+comment+method+'\n}\n'}
assert planned[exception].replace(comment+method+'\n','')==old[exception]
assert all(require_owned(p.read_text(),old[p],planned[p]) is False for p in old)
for p,s in planned.items():p.write_text(s)
O.mkdir();c.SLOT=O;jdk=TC/'jdk-25.0.4/bin';sg=TC/'static-gates-20261015';paths=list(map(str,planned))
stages=dict(format=c.step('format',[str(jdk/'java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*paths],R),checkstyle=c.step('checkstyle',[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),*paths],R))
passed=all(v['actualExit']==0 and not v['timedOut'] for v in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error')
v=dict(actualExit=0 if passed else 1,sourceBefore=source,inputHashes={str(p.relative_to(R)):sha(p) for p in old},stages=stages,originalSourceInverseExact=True,localHelperExactAlgorithmReuse= dict(path=str(reference.relative_to(R)),sha256=sha(reference),methodSha256=hashlib.sha256(method.encode()).hexdigest()),directoryCallsOnly=3,resourceScopeChanged=False,normalReasonsResourceOwnershipAndCleanupUnchanged=True,productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,coverage=None,ptStatus='NOT_RUN_NOT_PASS',bug='BUG-2718',actualHeldClassBinaryAccess=False,actualNativeFdRootFsOperations=0,verifierSha256=sha(Path(__file__).resolve()))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert passed;print(json.dumps(dict(actualExit=0,changedSources=2,directoryCalls=3,manifestSha256=sha(O/'manifest.json'))))
