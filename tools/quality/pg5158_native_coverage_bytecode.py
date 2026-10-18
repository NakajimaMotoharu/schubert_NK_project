"""Exact seven coverage-directory scopes, direct factory returns and all other class bytes unchanged."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5156_native_coverage_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5156-native-coverage-green-v2'
CLASS='dev.codex.schubert.nk.bootstrap.NativeCoveragePrivateFile'
KEY='bootstrap:'+CLASS.replace('.','/')+'.class'


def require_only_target_delta(before,after):
    if set(before)!=set(after) or {key for key in before if before[key]!=after[key]}!={KEY}:
        raise ValueError('only one declared coverage-directory outer may change; no removed/added/other debug changes')


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes())
    if result['actualExit']!=0 or result['phaseExits']!=[0,0] or result['tests']!=536 or result['suites']!=73:
        raise ValueError('original536/73 complete first')
    before=json.loads((selected.ROOT.parent/'pgpt-runs/PG379/pg5148-native-fd-green-v2/manifest.safe.json').read_bytes())
    require_only_target_delta(before['mainDelta']['physicalSha256'],result['mainDelta']['physicalSha256'])
    methods,hashes=bytecode.decode(RUN/'source','bootstrap',CLASS)
    sites=caller.callers(methods)
    if len(sites)!=7:raise ValueError('all7 owned scopes required')
    factories=[]
    for method in methods:
        for needle in ('OwnedTransferDirectory.open:','OwnedTransferDirectory.openExistingChild:'):
            if any(needle in op[2] for op in method['ops']):
                factories.append({'method':method['header'],'directReturnPcs':caller.tail(method,needle),'acquire':needle})
    if len(factories)!=6:raise ValueError('exact6 direct Directory factories plus one openRun method reference')
    raw=subprocess.check_output([str(bytecode.JAVAP),'-p','-c','-v','-classpath',
       str(RUN/'source/src/schubert-nk-bootstrap/target/classes'),CLASS],text=True)
    if 'REF_invokeInterface dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile$Io.openRun:()Ldev/codex/schubert/nk/storage/OwnedTransferDirectory;' not in raw:
        raise ValueError('openRun direct method reference required')
    xml=RUN/'source/src/schubert-nk-bootstrap/target/site/jacoco/jacoco.xml'
    target=bytecode.one([c for c in ET.parse(xml).getroot().findall('package/class')
                        if c.get('name')==CLASS.replace('.','/')],'one actual target class')
    counters={v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}
              for v in target.findall('counter')}
    four={'LINE','METHOD','CLASS','BRANCH'}
    class_four100=four<=set(counters) and all(counters[key]['missed']==0 for key in four)
    value={'source':result['sourceSnapshot'],'actualExit':0,'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),
       'class':hashes,'scopes':sites,'directFactoryReturns':factories,'openRunDirectMethodReference':True,
       'previousSource':before['sourceSnapshot'],'physicalMain':764,'changedPhysicalMain':1,
       'unchangedOtherClasses':763,'targetClassCounters':counters,'targetWholeCoverage100':class_four100,
       'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],'wholeHorizontalComplete':False,
       'formalAccepted':False,'nativeImported':False,'actualHeapOomReproduced':False,'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5158-native-coverage-directory-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'scopes':7,'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
