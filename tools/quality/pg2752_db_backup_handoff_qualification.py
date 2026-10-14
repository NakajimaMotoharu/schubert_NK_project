"""Read-only exact XML, SQL fixture and current Main/native qualification; no inferred gain."""
import hashlib
import json
import os
import shlex
from lan_server import run
from pg1446_current_cold_stage import W
from pg2674_operation_publication_sources import production


def main():
    outer=json.loads((W/'pg2750-db-backup-handoff-selected-v1/manifest.safe.json').read_bytes())
    if outer.get('actualExit')!=0 or outer.get('source')!=production():raise ValueError('actual selected source required')
    code='''import hashlib,json,pathlib,xml.etree.ElementTree as E
p=pathlib.Path('/home/mini/schubert-nk-pgpt/runs/PG2750-selected-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p/'manifest.safe.json')==EXPECTED
m=json.loads((p/'manifest.safe.json').read_bytes())
assert m['actualExit']==0 and m['tests']==1 and m['FESAbortedNotRun']==0
assert m['source']==SOURCE and m['MainRecompiled'] is False and m['vmActions0'] is True
assert m['freshIsolatedPostgres'] is True and m['fixturesUnchanged'] is True
assert sha(p/'tests.xml')==m['xmlSha256'] and sha(p/'selected.exec')==m['execSha256']
x=E.parse(p/'tests.xml').getroot()
assert x.attrib=={'name':'PG2750','tests':'1','failures':'0','errors':'0','skipped':'0'}
cases=x.findall('testcase');assert len(cases)==1 and not list(cases[0])
assert cases[0].attrib=={'classname':'dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest','name':'mdb2750001BackupObservationRejectsInHandoffBeforeJdbcAndPreservesFailedPair'}
for module,digest in m['xmlHashes'].items():assert sha(p/(module+'.xml'))==digest
root=E.parse(p/'batch.xml').getroot()
c=next(c for c in root.findall('.//class')if c.get('name')=='dev/codex/schubert/nk/batch/repository/MorningDatabaseSession$Session')
method=next(v for v in c.findall('method')if v.get('name')=='observeBackup')
counters={v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}for v in method.findall('counter')}
assert counters['BRANCH']=={'missed':3,'covered':29}
assert counters['LINE']=={'missed':0,'covered':41} and counters['METHOD']=={'missed':0,'covered':1}
sf=next(v for v in root.findall('.//sourcefile')if v.get('name')=='MorningDatabaseSession.java')
lines={v.get('nr'):dict(v.attrib) for v in sf.findall('line')if v.get('nr')in ['669','680','689']}
assert len(lines)==3 and all(v['mb']=='1'for v in lines.values())
assert all(v['classByteMismatch']==0 for v in m['coverage'].values())
assert m['remainingSameSourceWithNative']=={'LINE':788,'METHOD':156,'CLASS':9,'BRANCH':532}
print(json.dumps({'actualExit':0,'productionSource':SOURCE,'testSource':m['testSource'],'selectedTests':1,'case':'PT-MDB-2750-001','xmlSha256':m['xmlSha256'],'execSha256':m['execSha256'],'exactXmlCaseVerified':True,'methodCounters':counters,'remainingLines':lines,'newCounterGain':0,'coverageHashesVerified':True,'inputFiles':m['input']['files'],'serverManifestSha256':EXPECTED,'freshIsolatedPostgres':True,'MainRecompiled':False,'vmActions0':True,'formalAccepted':False}))
'''
    raw='EXPECTED='+repr(outer['manifestSha256'])+'\nSOURCE='+repr(production())+'\n'+code
    compile(raw,'<independent selected DB qualification>','exec')
    out=W/'pg2752-db-backup-handoff-qualified-v1'
    os.umask(0o077);out.mkdir(mode=0o700)
    c,o=run('python3 -B -c '+shlex.quote(raw),60)
    (out/'server.private.log').write_text(o)
    result={'actualExit':c,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if not c:result.update(json.loads(next(l for l in o.splitlines()if l.startswith('{'))))
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True))
    print(json.dumps(result));return c


if __name__=='__main__':raise SystemExit(main())
