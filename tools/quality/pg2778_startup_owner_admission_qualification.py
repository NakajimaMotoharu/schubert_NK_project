"""Read-only exact two-case XML and entry guard gain, not native owner acceptance."""
import hashlib
import json
import os
import shlex
from lan_server import run
from pg1446_current_cold_stage import W
from pg2674_operation_publication_sources import production


def main():
    outer=json.loads((W/'pg2776-startup-owner-admission-selected-v1/manifest.safe.json').read_bytes())
    if outer.get('actualExit')!=0 or outer.get('source')!=production():raise ValueError('actual selected current source required')
    code='''import hashlib,json,pathlib,xml.etree.ElementTree as E
p=pathlib.Path('/home/mini/schubert-nk-pgpt/runs/PG2776-selected-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p/'manifest.safe.json')==EXPECTED
m=json.loads((p/'manifest.safe.json').read_bytes())
assert m['actualExit']==0 and m['tests']==2 and m['FESAbortedNotRun']==0 and m['source']==SOURCE
assert m['MainRecompiled'] is False and m['vmActions0'] is True
assert sha(p/'tests.xml')==m['xmlSha256'] and sha(p/'selected.exec')==m['execSha256']
x=E.parse(p/'tests.xml').getroot()
assert x.attrib=={'name':'PG2776','tests':'2','failures':'0','errors':'0','skipped':'0'}
names={'launch2776001UntrustedPublicationValuesRejectBeforeProviders','launch2776002EveryNullBoundaryRejectsBeforeProviders'}
cases=x.findall('testcase');assert len(cases)==2 and {v.get('name')for v in cases}==names
assert all(v.get('classname')=='dev.codex.schubert.nk.batch.file.MorningStartupLaunchOwnerAdmissionTest'and not list(v)for v in cases)
for module,digest in m['xmlHashes'].items():assert sha(p/(module+'.xml'))==digest
root=E.parse(p/'batch.xml').getroot()
c=next(v for v in root.findall('.//class')if v.get('name')=='dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner')
methods={v.get('name'):{x.get('type'):{'missed':int(x.get('missed')),'covered':int(x.get('covered'))}for x in v.findall('counter')}for v in c.findall('method')if v.get('name')in ['prepare','publish']}
assert set(methods)=={'prepare','publish'}
sf=next(v for v in root.findall('.//sourcefile')if v.get('name')=='MorningStartupLaunchOwner.java')
lines={v.get('nr'):dict(v.attrib)for v in sf.findall('line')if v.get('nr')in ['48','49','50']}
assert len(lines)==3 and all(v['mb']=='0'for v in lines.values())
assert all(v['classByteMismatch']==0 for v in m['coverage'].values())
assert m['remainingSameSourceWithNative']=={'LINE':786,'METHOD':156,'CLASS':9,'BRANCH':526}
print(json.dumps({'actualExit':0,'productionSource':SOURCE,'testSource':m['testSource'],'tests':2,'fixtureModes':10,'exactXmlCasesVerified':True,'xmlSha256':m['xmlSha256'],'execSha256':m['execSha256'],'serverManifestSha256':EXPECTED,'inputFiles':m['input']['files'],'methodCounters':methods,'entryLines':lines,'newBranchGain':3,'newLineGain':0,'newMethodGain':0,'noNativeOwnerAcceptance':True,'MainRecompiled':False,'vmActions0':True,'formalAccepted':False}))
'''
    raw='EXPECTED='+repr(outer['manifestSha256'])+'\nSOURCE='+repr(production())+'\n'+code
    compile(raw,'<independent publication entry two-case qualification>','exec')
    out=W/'pg2778-startup-owner-admission-qualified-v1';os.umask(0o077);out.mkdir(mode=0o700)
    c,o=run('python3 -B -c '+shlex.quote(raw),60)
    (out/'server.private.log').write_text(o)
    result={'actualExit':c,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if not c:result.update(json.loads(next(l for l in o.splitlines()if l.startswith('{'))))
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));print(json.dumps(result));return c


if __name__=='__main__':raise SystemExit(main())
