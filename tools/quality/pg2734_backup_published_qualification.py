"""Read-only exact selected XML/hash and method qualification; no inferred counter gain."""
import hashlib
import json
import os
import shlex
from pathlib import Path
from lan_server import run
from pg1446_current_cold_stage import W
from pg2674_operation_publication_sources import production


def main():
    outer = json.loads((W/'pg2732-backup-published-selected-v1/manifest.safe.json').read_bytes())
    if outer.get('actualExit') != 0 or outer.get('source') != production():
        raise ValueError('actual selected source required')
    code = '''import hashlib,json,pathlib,xml.etree.ElementTree as E
p=pathlib.Path('/home/mini/schubert-nk-pgpt/runs/PG2732-selected-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p/'manifest.safe.json')==EXPECTED
m=json.loads((p/'manifest.safe.json').read_bytes())
assert m['actualExit']==0 and m['tests']==1 and m['FESAbortedNotRun']==0
assert m['source']==SOURCE and m['MainRecompiled'] is False and m['vmActions0'] is True
assert sha(p/'tests.xml')==m['xmlSha256'] and sha(p/'selected.exec')==m['execSha256']
x=E.parse(p/'tests.xml').getroot()
assert x.attrib=={'name':'PG2732','tests':'1','failures':'0','errors':'0','skipped':'0'}
cases=x.findall('testcase');assert len(cases)==1
assert cases[0].attrib=={'classname':'dev.codex.schubert.nk.batch.file.BackupBundlePublisherTest','name':'bat2732001PublishedBundleRejectsEveryIdentityOrContentDrift'}
assert not list(cases[0])
for module,digest in m['xmlHashes'].items():assert sha(p/(module+'.xml'))==digest
classes=E.parse(p/'batch.xml').getroot().findall('.//class')
c=next(c for c in classes if c.attrib['name']=='dev/codex/schubert/nk/batch/file/BackupArtifactVerifier$BundleSnapshot')
method=next(v for v in c.findall('method') if v.attrib['name']=='samePublished')
counters={v.attrib['type']:{'missed':int(v.attrib['missed']),'covered':int(v.attrib['covered'])}for v in method.findall('counter')}
assert counters and all(v['missed']==0 for v in counters.values())
assert all(v['classByteMismatch']==0 for v in m['coverage'].values())
print(json.dumps({'actualExit':0,'productionSource':SOURCE,'testSource':m['testSource'],'selectedTests':1,'case':'PT-BAT-2732-001','xmlSha256':m['xmlSha256'],'execSha256':m['execSha256'],'exactXmlCaseVerified':True,'methodCounters':counters,'newCounterGain':0,'coverageHashesVerified':True,'inputFiles':m['input']['files'],'serverManifestSha256':EXPECTED,'MainRecompiled':False,'vmActions0':True,'formalAccepted':False}))
'''
    raw='EXPECTED='+repr(outer['manifestSha256'])+'\nSOURCE='+repr(production())+'\n'+code
    out=W/'pg2734-backup-published-qualified-v1'
    os.umask(0o077);out.mkdir(mode=0o700)
    c,o=run('python3 -B -c '+shlex.quote(raw),60)
    (out/'server.private.log').write_text(o)
    result={'actualExit':c,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if not c:result.update(json.loads(o))
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True))
    print(json.dumps(result));return c


if __name__=='__main__':
    raise SystemExit(main())
