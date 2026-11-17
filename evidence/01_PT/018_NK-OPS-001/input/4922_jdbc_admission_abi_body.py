"""Compare existing compiler outputs and complete source bodies; no Product invocation."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));prior=b/'evidence/PG38066-jdbc-pure-before-fix-v1/manifest.json';old=ld(prior);before=b/'evidence/PG38068-jdbc-pure-before-prepare-v1';after=b/'evidence/PG38070-jdbc-pure-after-prepare-v1';bm=ld(before/'manifest.json');am=ld(after/'manifest.json');assert bm['actualExit']==am['actualExit']==0
rows=[]
for n,h in old['mainHashes'].items():
 previous=subprocess.check_output(['git','show',old['sourceCore']+':'+n]).decode();assert hashlib.sha256(previous.encode()).hexdigest()==h
 current=(r/n).read_text();inverse=current
 if n.endswith('/JdbcAdmissionFailures.java'):
  assert current.count('Objects.requireNonNull(secondary, "secondary failure");')==1
  inverse=current.replace('import java.util.Objects;\n','').replace('private JdbcAdmissionFailures() {\n    throw new AssertionError("static namespace");\n  }','private JdbcAdmissionFailures() {}').replace('    Objects.requireNonNull(secondary, "secondary failure");\n','')
 assert inverse==previous
 rows.append(dict(path=n,beforeSha256=h,afterSha256=sha(r/n),privateGuardAndNonnullOnlyInverseExact=True,unchanged=n.endswith('/StorageIoException.java')))
abi=[]
for n,h in bm['physicalClassHashes'].items():
 name=Path(n).stem;left=before/('abi-'+name+'.stdout');right=after/('abi-'+name+'.stdout');assert left.read_bytes()==right.read_bytes();unchanged=n.rsplit('/',1)[-1].startswith('StorageIoException');assert not unchanged or h==am['physicalClassHashes'][n]
 abi.append(dict(className=n,allVisibilityAbiEqual=True,unchangedDependencyByteExact=unchanged,beforeClassSha256=h,afterClassSha256=am['physicalClassHashes'][n],beforeAbi=ref(left),afterAbi=ref(right)))
witness=[]
for n,h in old['callerSourceHashes'].items():
 assert sha(r/n)==h;text=(r/n).read_text()
 for m in re.finditer(r'catch \(([^)]+) (secondary|cleanup)\) \{\s*(?:if \()?JdbcAdmissionFailures\.(replace|beforeDiscard)\((\w+), (secondary|cleanup)\)',text):
  assert m[2]==m[5];witness.append(dict(path=n,line=text[:m.start()].count('\n')+1,catchTypes=m[1],secondaryBinding=m[2],method=m[3],bindingNonNullByJavaCatchContract=True))
assert len(witness)==6
out=b/'evidence/PG38074-jdbc-pure-abi-body-v1';assert not out.exists();out.mkdir();value=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),beforeSourceCore=old['sourceCore'],rows=rows,allVisibilityAbi3Equal=abi,sharedStorage2PhysicalByteExact=True,sixCatchBindingCallerWitnesses=witness,actualCallerDbTestsExecuted=0,actualDbRootNativeVmKeyAuthorityActions=0,oracle='PG-D312 fixed knownSQL/unknown identity priorities and SSC095; private invariant only valid callers unchanged',previous=ref(prior),before=ref(before/'manifest.json'),after=ref(after/'manifest.json'));(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,abi=3,bodyInverse=2,unchangedShared=2,nonnullCatchWitness=6))
