"""Config-only delta ownership + whole six physical bytes + actual static5/ordinary3 proof join."""
import datetime as dt
import json
from pathlib import Path
import platform
import subprocess
import zipfile
from host_tool_invocation import capture,verify
from public_blob_scan import sha
from source_evidence_binding import bind
import trace_owner_join as owners
import pg9012_caddy_format_static as static

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
WORK=ROOT.parent/'pgpt-runs/PG379'
OUT=BASE/'PG9020-caddy-format-trace-v1'
SOURCE='f690fa6be336550f8078e2bdde40ef34ab5efe6b'
BEFORE='fb9fce0f91de3d9fdfa634fe277592700f915e45'
ARTIFACT='src/deployment/caddy/Caddyfile.template'
PROOFS=[('PG9012-caddy-format-static-v1','5cd9e50e288ea56e38341b3e0fbceb60868f72aa9702f290b4a7220fdae620af'),
        ('PG9014-caddy-format-six-compile-v1','01bad7736bbef335cb0b8dee60947e5767d57180bb59c631ae4ea9374058c18c'),
        ('PG9016-caddy-format-host-v1','e5a51ce6969ab8800c6111ef5ce5c0e422947d0a2d01002aeff7810b2eac43f7'),
        ('PG9018-caddy-format-post-v1','7bcec8d77845b98e988498766121756e8bafe5e465b95afc04b6cf16a2461ce8')]


def inventory(normal):
    assert set(normal['jars'])=={'protocol','storage','bootstrap','api','web','batch'}
    result={}
    for role,row in normal['jars'].items():
        path=Path(row['path']);assert sha(path.read_bytes())==row['sha256']
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith('.class'):
                    key=role+':'+name;assert key not in result
                    result[key]=sha(archive.read(name))
    return result


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    bindings=bind([(BASE/name/'manifest.json',digest) for name,digest in PROOFS],SOURCE)
    values={name:json.loads((BASE/name/'manifest.json').read_bytes()) for name,_ in PROOFS}
    normal=values[PROOFS[1][0]];profile=values[PROOFS[0][0]];pt=values[PROOFS[2][0]];post=values[PROOFS[3][0]]
    old_path=BASE/'PG8946-web-metric-pipeline-six-compile-v1/manifest.json'
    assert sha(old_path.read_bytes())=='2bb0684f5eb144957ca69286a703d14fcb19a0fe1826e7621ad496274559b70f'
    old=json.loads(old_path.read_bytes());assert old['source']==BEFORE and old['actualExit']==0
    physical=inventory(normal);prior=inventory(old)
    assert physical==prior and len(physical)==1835
    changed=subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT).decode().splitlines()
    assert changed==[ARTIFACT]
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    snapshot=WORK/'pg9014-caddy-format-six-compile-v1/snapshot'
    data=(ROOT/ARTIFACT).read_bytes();digest=sha(data)
    assert (snapshot/ARTIFACT).read_bytes()==data==subprocess.check_output(['git','show',SOURCE+':'+ARTIFACT],cwd=ROOT)
    assert normal['begin']['inputHashes'][ARTIFACT]==pt['begin']['sourceHashes'][ARTIFACT]==profile['artifactSha256']==digest
    expected_ids={'PT-C01-FMT-'+str(number).zfill(3) for number in range(1,6)}
    assert len(profile['staticCases'])==5 and {row['caseId'] for row in profile['staticCases']}==expected_ids
    verify_json=static.verifier();slot=WORK/'pg9012-caddy-format-static-v1'
    for row in profile['staticCases']:
        name=row['caseId'];terminal=json.loads((slot/(name+'-terminal.safe.json')).read_bytes())
        before=json.loads((slot/(name+'-begin.safe.json')).read_bytes())
        assert terminal==row['terminal'] and terminal['actualExit']==0 and before['source']==SOURCE
        assert before['command']==row['command'] and before['inputSha256']==row['inputSha256']
        assert before['binarySha256']==profile['binarySha256']==static.BINARY_SHA
        output=(BASE/PROOFS[0][0]/(name+'.output.txt')).read_bytes()
        assert sha(output)==terminal['stdoutSha256'] and row['unclassifiedWarnings']==0
        input_path=Path(row['command'][2] if row['command'][1]=='fmt' else row['command'][3])
        assert input_path.parent==slot and sha(input_path.read_bytes())==row['inputSha256']
        if name.endswith(('001','002','003')):
            assert row['command']==[str(static.BINARY),'fmt',str(input_path)]
            assert output==input_path.read_bytes() and row['fixedPoint'] is True
        else:
            assert row['command']==[str(static.BINARY),'adapt','--config',str(input_path),'--adapter','caddyfile']
            verify_json(json.loads(output),'127.0.0.1' if name.endswith('004') else '2001:db8::1')
    plan=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in plan['artifacts']}
    row=dict(path=ARTIFACT,sha256=digest,owner='WBS-C01')
    joined=owners.join_rows([row],logical,normal['begin']['inputHashes'],'WBS-C01')
    owners.validate(joined,[row],logical,normal['begin']['inputHashes'],'WBS-C01')
    assert joined[0]['canonicalOwner']==joined[0]['canonicalCostOwner']=='WBS-C01'
    assert post['actualTests']==3 and post['requiredWholeClassFour100'] is False
    assert post['wholeClassCounters']=={'LINE':{'missed':109,'covered':24},'METHOD':{'missed':21,'covered':2},'CLASS':{'missed':0,'covered':1},'BRANCH':{'missed':78,'covered':22}}
    verify(invocation);OUT.mkdir()
    result=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
       source=SOURCE,previousJavaSource=BEFORE,branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip(),
       os=platform.platform(),sourceProofs=bindings,changedProductionInputs=changed,changedMain=0,allPhysicalMain=1835,
       allPhysicalClassBytesUnchanged=True,physicalInventoryDigest=sha(json.dumps(physical,sort_keys=True,separators=(',',':')).encode()),
       changedArtifactOwnership=joined,previousArchitectureNotRerun=True,oldPtOrCoverageTransferred=False,
       staticCases=5,actualOrdinaryJavaTests=3,newJavaTestIds=0,newMain=0,
       actualWholeClassCoverage=post['wholeClassCounters'],wholeClassFour100=False,
       literalSsProfileAndFmtFixedPoint=True,wholeC01Or451Accepted=False,
       bug='BUG-1728',ykt='YKT-1479',actualVmOrTlsOrServiceActions=0,formalUpdated=False,newAccepted=0)
    with (OUT/'manifest.json').open('x',encoding='utf-8') as stream:
        json.dump(result,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,allPhysicalMain=1835,changedMain=0,changedArtifacts=1,staticCases=5,ordinaryJavaTests=3,wholeClassFour100=False)))


if __name__=='__main__':main()
