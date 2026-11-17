"""Exact committed public Git delta only, three known credential formats; no worktree/private/untracked reads."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from public_delta_path_policy import validate_path,validate_metadata,PUBLIC_NAMESPACE_METADATA
before='71461d0bc6446f3ccc9f24df1fc1f50705d443d5';head=sys.argv[1];assert re.fullmatch('[0-9a-f]{40}',head) and head==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();subprocess.run(['git','merge-base','--is-ancestor',before,head],check=True)
binding_path=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG37564-public-path-failclosed-tool-selfcheck-v1/binding.json'
selfcheck_path=binding_path.parent/'manifest.json'
policy_path=r/'tools/quality/public_delta_path_policy.py'
for pin in [Path(__file__).resolve(),binding_path,selfcheck_path,policy_path]:
 assert pin.read_bytes()==subprocess.check_output(['git','show',head+':'+str(pin.relative_to(r))])
binding=json.loads(binding_path.read_bytes());selfcheck=json.loads(selfcheck_path.read_bytes())
assert binding['publicPath']==PUBLIC_NAMESPACE_METADATA and binding['protectedExceptionsAllowed'] is False
assert selfcheck['actualExit']==0 and selfcheck['toolTests']==23 and selfcheck['failed']==0 and selfcheck['productTestsExecuted']==0
assert selfcheck['pathPolicySha256']==hashlib.sha256(policy_path.read_bytes()).hexdigest()
rules={'PRIVATE_KEY_PEM':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),'GITHUB_CREDENTIAL':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b'),'AWS_ACCESS_KEY_ID':re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')}
names=subprocess.check_output(['git','diff','--no-renames','--diff-filter=ACMRT','--name-only','-z',before,head,'--']).decode().strip('\0').split('\0');assert names and names!=[''];rows=[];findings=[]
blocked={'tools/quality/architecture/SnapshotKeyCloseWitness.java','tools/quality/pg9892_snapshot_key_close_witness.py'}
for n in names:
 policy_mode=validate_path(n)
 tree=subprocess.check_output(['git','ls-tree','-z',head,'--',n]);meta,path=tree[:-1].split(b'\t',1);mode,kind,oid=meta.decode().split();assert path.decode()==n and mode in ['100644','100755'] and kind=='blob'
 raw=subprocess.check_output(['git','cat-file','blob',oid])
 if policy_mode=='PUBLIC_NAMESPACE_METADATA_REQUIRES_PIN_AND_SCHEMA':
  validate_metadata(raw,binding['sha256'])
 row=dict(path=n,gitObject=oid,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),rawThreePatternScan=True,binaryContainsNul=b'\0' in raw);rows.append(row)
 for label,pattern in rules.items():
  for match in pattern.finditer(raw):findings.append(dict(path=n,rule=label,line=raw[:match.start()].count(b'\n')+1))
 raw=None
out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG38176-media-context-whole16-public-delta-v1';assert not out.exists();out.mkdir();value=dict(actualExit=1 if findings else 0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),beforeCommit=before,contentCommit=head,productionSourceCore=subprocess.check_output(['git','log','-1','--format=%H','--',*[f'src/schubert-nk-{m}/src/main/java' for m in ['protocol','storage','bootstrap','api','web','batch']]],text=True).strip(),scope='EXACT_TRACKED_PUBLIC_GIT_DELTA_RAW_BYTES_THREE_FORMATS_ONLY',rules=list(rules),files=rows,findings=findings,matchedValuesOrIndividualSecretHashesSaved=False,protectedFilesAccessed=False,worktreeUntrackedOrPrivateInputsRead=False,publicMetadataStrictHashSchemaBound=True,protectedExceptionsAllowed=False,pathPolicyToolSha256=hashlib.sha256(policy_path.read_bytes()).hexdigest(),toolSelfcheck23OnlyNotProductTests=True,binaryAlsoRawPatternScanned=True,encodedContainerOrGenericCredentialFormatsNotCovered=True,wholeG07Or451Accepted=False,productTestsExecuted=0,newFormalAcceptance=0)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=value['actualExit'],files=len(rows),findings=len(findings),scope='THREE_FORMATS_ONLY_NOT_ALL_SECRETS_OR_G07')));raise SystemExit(value['actualExit'])
