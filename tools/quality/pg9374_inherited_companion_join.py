"""Read source/interface declarations and fixed normal Jar; do not execute target code."""
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import trace_owner_join_inherited_companion as owner
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9374-inherited-companion-join-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
NORMAL=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
PRIOR=BASE/'PG9364-static-companion-owner-join-v1/manifest.json'
JAR=ROOT.parent/'pgpt-runs/PG379/pg9246-web-life-lock-six-compile-v1/snapshot/src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
TC=ROOT.parent/'toolchain'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    assert sha(NORMAL.read_bytes())=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    assert sha(PRIOR.read_bytes())=='5f7b552fb08fb96e388232952ab88ac61d70a581176c1e63400b405da864cbbb'
    normal=json.loads(NORMAL.read_bytes());prior=json.loads(PRIOR.read_bytes())
    assert normal['source']==prior['source']==SOURCE and normal['actualExit']==prior['actualExit']==0
    hashes=normal['begin']['inputHashes'];old=prior['sourceRows'];assert len(old)==624
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']};known={row['path']:row for row in old}
    jar_sha=sha(JAR.read_bytes());assert jar_sha=='8d93baa2904af6e336b5b369339cc1cdfc76fd667b087cd31fcadcf1e163c65b'
    originals=[dict(path=row['path'],sha256=row['sha256'],owner=row['legacyReportedOwner']) for row in old]
    evidence=[]
    for path,(main_name,interface,fixture,method,expected_owner) in sorted(owner.DECISIONS.items()):
        assert path not in logical and path not in known
        main_path=path.replace('/src/test/java/','/src/main/java/').removesuffix('Test.java')+'.java'
        test=(ROOT/path).read_text();main_source=(ROOT/main_path).read_text()
        assert sha(test.encode())==hashes[path] and sha(main_source.encode())==hashes[main_path]
        assert re.search(r'\bclass\s+'+fixture+r'\s+implements\s+'+main_name+r'\.'+interface+r'\s*\{',test)
        assert re.search(r'\binterface\s+'+interface+r'\s*\{',main_source)
        assert re.search(r'\b'+main_name+r'\.'+method+r'\s*\(',test)
        baseline=logical.get(main_path)
        actual=(baseline['owner'],baseline['costOwner']) if baseline else (known[main_path]['canonicalOwner'],known[main_path]['canonicalCostOwner'])
        assert actual==(expected_owner,expected_owner)
        class_name=main_path.split('/src/main/java/')[1].removesuffix('.java').replace('/','.')+'$'+interface
        command=[str(TC/'jdk-25.0.4/bin/javap'),'-p','-classpath',str(JAR),class_name]
        result=subprocess.run(command,cwd=ROOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
        assert result.returncode==0 and not result.stderr
        text=result.stdout.decode();assert 'interface '+class_name+' {' in text
        declarations=[line.strip() for line in text.splitlines() if line.strip().endswith(';')]
        assert declarations and all('(' in line for line in declarations)
        evidence.append(dict(path=path,sha256=hashes[path],mainPath=main_path,mainSha256=hashes[main_path],owner=expected_owner,
          fixture=fixture,interfaceClass=class_name,subjectMethod=method,javapCommand=command,javapActualExit=0,
          javapOutputSha256=sha(result.stdout),interfaceDeclarations=declarations))
        originals.append(dict(path=path,sha256=hashes[path],owner=None))
    rows=owner.join_rows(originals,logical,hashes,'WBS-G13.07');owner.validate(rows,originals,logical,hashes,'WBS-G13.07')
    for before,after in zip(old,rows):assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    assert len(rows)==len({row['path'] for row in rows})==626
    assert sha(JAR.read_bytes())==jar_sha
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      normalManifestSha256=sha(NORMAL.read_bytes()),priorManifestSha256=sha(PRIOR.read_bytes()),jarSha256=jar_sha,
      originalInputs=originals,sourceRows=rows,interfaceEvidence=evidence,sourceCount=626,newSourceOwnerCandidates=2,
      newOwnerCounts=dict(Counter(row['canonicalOwner'] for row in rows[624:])),previous624CanonicalPreserved=True,
      javaPaths=1789,registered=1451,registeredMain=965,totalMain=965,registeredTest=486,totalTest=824,unregisteredTest=338,
      productTestsExecuted=0,targetCompile=0,targetClassLoading=0,newTestIds=0,newMain=0,coverage=None,newAccepted=0,
      wholeG13Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None)
    with (OUT/'manifest.json').open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,newCandidates=2,registered=1451,unregistered=338,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
