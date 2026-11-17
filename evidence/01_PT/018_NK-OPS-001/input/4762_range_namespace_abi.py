"""Five original Parser ABI unchanged; distinguish actual ctor Code change from line/debug shifts."""
from pathlib import Path
import json,hashlib,re,subprocess,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=json.loads((b/'evidence/PG37540-range-namespace5-prepare-v1/manifest.json').read_text());old=json.loads((b/'evidence/PG27002-media186-independent-v1/manifest.json').read_text());oldroot=w/'pg26990-media186-profile-v2/component';newroot=w/'pg37540-range-namespace5-v1/component';names=sorted(n for n in old['physicalClassHashes'] if '/HttpByteRangeParser' in n);assert len(names)==5
out=b/'evidence/PG37544-range-namespace-abi-v1';assert not out.exists();out.mkdir();javap=r.parent/'toolchain/jdk-25.0.4/bin/javap';rows=[]
def run(label,args):
 x=subprocess.run([str(javap),*args],capture_output=True,timeout=30);assert x.returncode==0;(out/(label+'.stdout')).write_bytes(x.stdout);(out/(label+'.stderr')).write_bytes(x.stderr);return x.stdout.decode()
def normal(text):return re.sub(r'#\d+','#CP',text)
for index,n in enumerate(names):
 assert sha(oldroot/n)==old['physicalClassHashes'][n] and sha(newroot/n)==p['physicalClassHashes'][n]
 a=run(f'{index}-before-abi',['-p','-s',str(oldroot/n)]);z=run(f'{index}-after-abi',['-p','-s',str(newroot/n)]);assert a==z
 x=normal(run(f'{index}-before-code',['-p','-s','-c',str(oldroot/n)]));y=normal(run(f'{index}-after-code',['-p','-s','-c',str(newroot/n)]));changed=sha(oldroot/n)!=sha(newroot/n);semantic=x!=y
 if n.endswith('/HttpByteRangeParser.class'):
  assert changed and semantic
  # All methods after the private ctor keep exactly the same normalized symbolic instruction text.
  anchor='  public static dev.codex.schubert.nk.web.media.HttpByteRangeParser$Selection parseFirst'
  assert x[x.index(anchor):]==y[y.index(anchor):] and 'class java/lang/AssertionError' in y and 'String static utility' in y
 else:assert not semantic
 rows.append(dict(path=n,beforeSha256=sha(oldroot/n),afterSha256=sha(newroot/n),allPublicPrivateDescriptorsSame=True,physicalChanged=changed,symbolicInstructionsChanged=semantic,debugOnlyChanged=changed and not semantic))
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceMainFilesChanged=1,all5PublicPrivateAbiSame=True,onlyCtorInstructionSemanticChanged=True,parseFirstAndDecimalCodeSame=True,physicalChanges=sum(x['physicalChanged'] for x in rows),debugOnlyChanges=sum(x['debugOnlyChanged'] for x in rows),rows=rows,methodBytecodeCommentCpIndexesNormalizedOnly=True,productionClassDefinedOrInitialized=False,testsExecuted=0,heldFourClassfileOperations=0,formalUpdated=False);(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print({k:v[k] for k in ['actualExit','all5PublicPrivateAbiSame','onlyCtorInstructionSemanticChanged','physicalChanges','debugOnlyChanges']})
