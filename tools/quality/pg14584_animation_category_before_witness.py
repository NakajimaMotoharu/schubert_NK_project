"""BUG2103 pre-fix five literal animation domain checks; expected failure is preserved, never PT PASS."""
import os
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NORMAL=('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
SLOT=run.WORK/'pg14584-animation-category-before-witness-v1'
OUT=data.BASE/'PG14584-animation-category-before-witness-v1'
WITNESS=data.ROOT/'tools/quality/architecture/AnimationCategoryDomainWitness.java'
NAMES=['MAIN_BASELINE_ACCEPTED','OVA_BASELINE_ACCEPTED','PAIR_BASELINE_ACCEPTED','MAIN_OPENING_REJECTED','OVA_OPENING_REJECTED']

def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    normal=data.read_checked(data.BASE/NORMAL[0]/'manifest.json',NORMAL[1]);snapshot=Path(normal['jars']['web']['path']).parents[3]
    # Use the normal's declared source snapshot location, not a historical application process.
    snapshot=run.WORK/'pg14216-typed-marker-guard-six-compile-v1/snapshot'
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items())
    cpfile=snapshot/'src/schubert-nk-web/target/pgpt-test-classpath.txt'
    external=[Path(p) for p in cpfile.read_text().strip().split(os.pathsep) if '/dev/codex/schubert/' not in p and not p.startswith(str(snapshot)+'/src/')]
    jars=[Path(j['path']) for j in normal['jars'].values()]
    assert all(data.sha(Path(j['path']).read_bytes())==j['sha256'] for j in normal['jars'].values())
    dependencies=list(dict.fromkeys([*jars,*external]));assert all(p.is_file() for p in dependencies)
    dependency_hashes={str(p):data.sha(p.read_bytes()) for p in dependencies};witness_hash=data.sha(WITNESS.read_bytes())
    SLOT.mkdir();classes=SLOT/'classes';classes.mkdir();run.SLOT=SLOT
    data.write(SLOT/'begin.safe.json',dict(source=SOURCE,normalManifestSha256=NORMAL[1],witnessSha256=witness_hash,dependencyHashes=dependency_hashes,expected={n:True for n in NAMES},bug='BUG-2103',ykt='YKT-1850',mode='SYNTHETIC_DTO_ONLY_NO_IO_AUTH_VM'))
    jdk=run.TC/'jdk-25.0.4/bin';cp=os.pathsep.join(map(str,dependencies))
    compile_stage=run.step('witness-compile',[str(jdk/'javac'),'-proc:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(WITNESS)],SLOT)
    assert compile_stage['actualExit']==0 and not compile_stage['timedOut']
    product=run.step('witness',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,'AnimationCategoryDomainWitness'],SLOT,timeout=60)
    rows=dict(line.split('=',1) for line in (SLOT/'witness.stdout').read_text().splitlines() if '=' in line)
    assert all(rows[n] in ('true','false') for n in NAMES) and len(rows)==9
    actual={n:rows[n]=='true' for n in NAMES};env={n:rows[n] for n in ('runtime.version','os.name','os.arch','os.version')}
    assert not product['timedOut'] and product['actualExit']==1 and all(actual[n] for n in NAMES if n!='MAIN_OPENING_REJECTED') and actual['MAIN_OPENING_REJECTED'] is False
    assert all(data.sha(Path(p).read_bytes())==h for p,h in dependency_hashes.items()) and data.sha(WITNESS.read_bytes())==witness_hash
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=1,status='BUG_REPRODUCED_NOT_PASS',source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL[1],witnessSourceSha256=witness_hash,dependencyHashes=dependency_hashes,stages=[compile_stage,product],expected={n:True for n in NAMES},actual=actual,reportedEnvironment=env,contractChecks=5,junitMethodsPassed=0,productTestsCountedAsPass=0,sourceInputsUnchanged=True,externalActions=0,formalUpdated=False,newAccepted=0,bug='BUG-2103',ykt='YKT-1850'))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(actual)
    raise SystemExit(1)

if __name__=='__main__':main()
