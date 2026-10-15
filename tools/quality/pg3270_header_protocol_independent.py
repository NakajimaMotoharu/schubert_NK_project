"""Read original successful Protocol84 after wrapper1; never rerun the test command."""
import ast
import hashlib
import json
import os
from lan_server import run
from pg1446_current_cold_stage import W
from pg3258_statement_group_full_six import SOURCE

SERVER = r'''
import datetime,hashlib,json,os,subprocess,tarfile,xml.etree.ElementTree as E,zipfile
from pathlib import Path
os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');p=b/'runs/PG3266-v1';s=b/'source-protocol-PG3266-v1';m=s/'src/schubert-nk-protocol';t=b/'transfer/PG3266-v1'
def require(v):
 if not v:raise ValueError('independent original Header Protocol qualification refused')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
authority=p/'manifest.safe.json';require(sha(authority)==INPUT['manifestSha256']);d=json.loads(authority.read_bytes())
require(d['actualExit']==d['mavenExit']==0 and d['source']==INPUT['source'] and d['testSource']==INPUT['testSource'])
require(sha(t/'regression.private.py')==INPUT['payloadSha256'] and sha(t/'source.tar')==d['input']['archiveSha256']==INPUT['archiveSha256'])
with tarfile.open(t/'source.tar')as archive:
 files=[n for n in archive.getmembers()if n.isfile()]
 for n in files:require(hashlib.sha256(archive.extractfile(n).read()).hexdigest()==sha(s/n.name))
 require(len(files)>0)
xmls=list((m/'target/surefire-reports').glob('TEST-*.xml'));require(len(xmls)==17 and {f.name for f in xmls}==set(d['xmlHashes']));cases=[]
for f in xmls:
 require(sha(f)==d['xmlHashes'][f.name]);x=E.parse(f).getroot();rows=x.findall('testcase')
 require(len(rows)==int(x.get('tests')) and all(x.get(k)=='0'for k in ['failures','errors','skipped']))
 require(not any(any(k in n.tag.lower()for k in ['failure','error','skipped','flaky','rerun'])for n in x.iter()if n is not x))
 cases.extend((r.get('classname'),r.get('name'))for r in rows)
require(len(cases)==len(set(cases))==d['tests']==84)
headers={n for c,n in cases if c=='dev.codex.schubert.nk.protocol.header.HeaderModelTest'}
require(headers=={'enumsMapOnlyApprovedWireValues','authenticationContextValidatesAndRedacts','validHeadersCoverRequestResponseErrorAndEventProfiles','headerConstructorRejectsEveryStructuralViolation','headerValidateAgainstRejectsEachMetadataMismatch','headerReferencesRejectNullAtTheNamedInvariantBoundary','headerLengthArithmeticAcceptsExactMillionAndRejectsTheNextByteAndOverflow'})
coverage=m/'target/site/jacoco/jacoco.xml';require(sha(coverage)==d['coverageXmlSha256']);counters={n.get('type'):{'missed':int(n.get('missed')),'covered':int(n.get('covered'))}for n in E.parse(coverage).getroot().findall('counter')}
require(counters==d['coverage'] and all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS','BRANCH']))
spot=m/'target/spotbugsXml.xml';require(sha(spot)==d['staticSha256'] and not E.parse(spot).getroot().findall('.//BugInstance')and d['staticIssues']==0)
jar=m/'target/schubert-nk-protocol-0.1.0-SNAPSHOT.jar';old=b/'source-full-PG3248/src/schubert-nk-protocol/target/schubert-nk-protocol-0.1.0-SNAPSHOT.jar';require(sha(jar)==d['jarSha256']and sha(old)==d['input']['priorJarSha256']);images=[]
for f in [old,jar]:
 with zipfile.ZipFile(f)as z:
  require(len(z.namelist())==len(set(z.namelist())));images.append({n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()})
require(images[0]==images[1]and sum(n.endswith('.class')for n in images[1])==d['mainClasses']==174)
require(sha(authority)==INPUT['manifestSha256'])
env={k:v for k,v in os.environ.items()if k not in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']};jdk=subprocess.run([str(b/'tools/jdk-25.0.4/bin/java'),'-version'],env=env,capture_output=True,check=True).stderr.decode()
value={'actualExit':0,'productionSource':INPUT['source'],'testSource':d['testSource'],'run':'PG3270-independent-header-v1','actualMavenExit':0,'originalWrapperExit':1,'tests':84,'suites':17,'mainClasses':174,'headerTests':7,'coverage':counters,'staticIssues':0,'FESFlakyNotRun':0,'sameAllMainAndResourceMembers':True,'authoritySha256':INPUT['manifestSha256'],'xmlHashes':d['xmlHashes'],'coverageXmlSha256':d['coverageXmlSha256'],'staticSha256':d['staticSha256'],'fixedInputFiles':len(files),'originalCommand':d['command'],'startUTC':d['startUTC'],'endUTC':d['endUTC'],'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'os':Path('/etc/os-release').read_text(),'jdk':jdk,'vmActions':0,'mavenReissued':False,'formalAccepted':False,'newWholeIntegrationPending':True}
out=b/'runs/PG3270-independent-header-v1';out.mkdir(mode=0o700);manifest=out/'manifest.safe.json';manifest.write_text(json.dumps(value,sort_keys=True));print(json.dumps({'manifestSha256':sha(manifest),'result':value}))
'''


def main():
    original = W / 'pg3266-header-protocol-regression-v1'
    receipt = json.loads((original / 'manifest.safe.json').read_bytes())
    payload = (original / 'regression.private.py').read_bytes()
    data = ast.literal_eval(payload.decode().splitlines()[0].removeprefix('INPUT='))
    if receipt['actualExit'] != 0 or hashlib.sha256(payload).hexdigest() != receipt['payloadSha256'] or receipt['testSource'] != data['head']:
        raise ValueError('original child0 receipt and exact immutable payload required')
    data = {'source': SOURCE, 'testSource': data['head'], 'payloadSha256': receipt['payloadSha256'],
            'archiveSha256': data['archiveSha256'], 'manifestSha256': '6dcd5532a2fb629cead8a1511bde71b49d8c3372e1a86b92798862d9b7f28291'}
    raw = 'INPUT=' + repr(data) + '\n' + SERVER
    compile(raw, '<independent existing Header84 original evidence>', 'exec')
    os.umask(0o077); out = W / 'pg3270-header-protocol-qualified-v1'; out.mkdir(mode=0o700)
    (out / 'qualifier.private.py').write_text(raw)
    code, output = run("python3 -B - <<'INDEPENDENT'\n" + raw + '\nINDEPENDENT', timeout=90)
    (out / 'observer.private.log').write_text(output)
    value = {'actualExit': code, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if code == 0:
        value.update(json.loads(next(line for line in output.splitlines() if line.startswith('{'))))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps({k: v for k, v in value.items() if k != 'result'}))
    if code == 0:
        print(json.dumps({k: value['result'][k] for k in ['tests', 'suites', 'mainClasses', 'headerTests', 'coverage', 'staticIssues', 'originalWrapperExit', 'actualMavenExit']}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
