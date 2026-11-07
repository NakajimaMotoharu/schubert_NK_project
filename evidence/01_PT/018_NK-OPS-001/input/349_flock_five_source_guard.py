"""Source/primary-manual contract and five exact reverse argv edits; no original process execution."""
from pathlib import Path
import datetime,gzip,hashlib,importlib.util,json,re
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG23134-flock-five-source-guard-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sp=importlib.util.spec_from_file_location('tokens',R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py');lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib);tok=lib.java_tokens;comment='// BUG2468: keep the command in this PID.'
def check(s,old,expected):
 t=tok(s);original=tok(old);triple=tok('"/usr/bin/flock", "--no-fork", '+comment);matches=[i for i in range(len(t)) if t[i:i+len(triple)]==triple]
 if len(matches)!=expected or '"--close"' in t or '"-o"' in t:return False
 for i in reversed(matches):t[i:i+len(triple)]=tok('"/usr/bin/flock",')
 return t==original
assert not O.exists();original=B/'evidence/PG23132-flock-five-original-v1/manifest.json';m=json.loads(original.read_bytes());rows=[];neg=[]
for v in m['inputs']:
 p=R/v['path'];old=(original.parent/v['backup']).read_text();assert sha(original.parent/v['backup'])==v['sha256'];s=p.read_text();expected=1 if p.name=='LinuxStartupFileLockTest.java' else 2;assert check(s,old,expected);rows.append(dict(path=v['path'],oldSha256=v['sha256'],sha256=sha(p),flagAdditions=expected,allOtherJavaTokensOraclesAndCommandsPreserved=True))
 for a,z in [('"--no-fork"','"--close"'),('"--no-fork"','"--shared"'),('"/usr/bin/flock"','"/usr/bin/other"')]:
  assert a in s and not check(s.replace(a,z,1),old,expected);neg.append(dict(path=v['path'],mutation=a+'→'+z))
# A missing line boundary must be rejected before any original process Test.
for v in m['inputs']:
 s=(R/v['path']).read_text();old=(original.parent/v['backup']).read_text();expected=1 if v['path'].endswith('/LinuxStartupFileLockTest.java') else 2
 a=comment+'\n';assert a in s;assert not check(s.replace(a,comment,1),old,expected);neg.append(dict(path=v['path'],mutation='remove inserted comment newline'))
assert sum(v['flagAdditions'] for v in rows)==5;man=Path(m['primaryManual']['path']);assert sha(man)==m['primaryManual']['sha256'];text=gzip.decompress(man.read_bytes()).decode().replace('\\-','-');assert 'process is replaced by' in text and 'continues to hold the lock' in text and 'incompatible with' in text and '--close' in text
O.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputs=rows,primaryManual=m['primaryManual'],designRef=m['designRef'],newFlagAdditions=5,allOtherOracleTokensUnchanged=True,metadataNegativeGuards=neg,originalTestsCompiled=False,productTestsExecuted=0,actualProductProcessActions=0,actualPass=None,coverage=None,sourceFixStatus='FLOCK_COMMAND_SAME_PID_SOURCE_DESIGN_ONLY_RUNTIME_HOLD',residualRisk='Actual util-linux and command binaries, shell descendants, wait/close and lock postconditions must be authenticated/measured later. No current VM/process evidence inferred.');(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print('five exact argv source changes/remaining whole source tokens preserved/negative12; no Product execution')
