"""Exact committed public Git delta only, three known credential formats; no worktree/private/untracked reads."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,sys
r=Path.cwd();before='1844a56e99dee75d76221d877c9125bf1c2cd800';head=sys.argv[1];assert re.fullmatch('[0-9a-f]{40}',head) and head==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();subprocess.run(['git','merge-base','--is-ancestor',before,head],check=True)
rules={'PRIVATE_KEY_PEM':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),'GITHUB_CREDENTIAL':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b'),'AWS_ACCESS_KEY_ID':re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')}
names=subprocess.check_output(['git','diff','--no-renames','--diff-filter=ACMRT','--name-only','-z',before,head,'--']).decode().strip('\0').split('\0');assert names and names!=[''];rows=[];findings=[]
blocked={'tools/quality/architecture/SnapshotKeyCloseWitness.java','tools/quality/pg9892_snapshot_key_close_witness.py'}
for n in names:
 assert n not in blocked and n.startswith(('src/','documents/','evidence/01_PT/','tools/quality/','program/characterization/src/main/java/','program/characterization/tests/java/')) and '/private' not in n.lower() and not n.endswith('.private.log')
 tree=subprocess.check_output(['git','ls-tree','-z',head,'--',n]);meta,path=tree[:-1].split(b'\t',1);mode,kind,oid=meta.decode().split();assert path.decode()==n and mode in ['100644','100755'] and kind=='blob'
 raw=subprocess.check_output(['git','cat-file','blob',oid]);row=dict(path=n,gitObject=oid,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),rawThreePatternScan=True,binaryContainsNul=b'\0' in raw);rows.append(row)
 for label,pattern in rules.items():
  for match in pattern.finditer(raw):findings.append(dict(path=n,rule=label,line=raw[:match.start()].count(b'\n')+1))
 raw=None
out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG37558-current-public-delta-three-patterns-v1';assert not out.exists();out.mkdir();value=dict(actualExit=1 if findings else 0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),beforeCommit=before,contentCommit=head,productionSourceCore=subprocess.check_output(['git','log','-1','--format=%H','--',*[f'src/schubert-nk-{m}/src/main/java' for m in ['protocol','storage','bootstrap','api','web','batch']]],text=True).strip(),scope='EXACT_TRACKED_PUBLIC_GIT_DELTA_RAW_BYTES_THREE_FORMATS_ONLY',rules=list(rules),files=rows,findings=findings,matchedValuesOrIndividualSecretHashesSaved=False,protectedFilesAccessed=False,worktreeUntrackedOrPrivateInputsRead=False,binaryAlsoRawPatternScanned=True,encodedContainerOrGenericCredentialFormatsNotCovered=True,wholeG07Or451Accepted=False,productTestsExecuted=0,newFormalAcceptance=0)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=value['actualExit'],files=len(rows),findings=len(findings),scope='THREE_FORMATS_ONLY_NOT_ALL_SECRETS_OR_G07')));raise SystemExit(value['actualExit'])
