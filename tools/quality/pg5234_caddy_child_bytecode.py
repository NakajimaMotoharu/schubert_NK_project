"""Exact two physical Main changes; all4 Caddy/Child factories directly return resource."""
import json
import os
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5232_caddy_child_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5232-caddy-child-green-v1'
KINDS={('batch','dev.codex.schubert.nk.batch.file.CaddyPublicConfiguration'):
       {'OwnedTransferDirectory.open:':1,'OwnedTransferDirectory.openExistingChild:':1,'Files.newInputStream:':1},
       ('bootstrap','dev.codex.schubert.nk.bootstrap.ChildStartupContext$NativeIo'):{'Files.newInputStream:':1}}


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes())
    if result['actualExit']!=0 or result['phaseExits']!=[0,0] or result['tests']!=812 or result['suites']!=96:
        raise ValueError('original812/96 complete first')
    prior_run=selected.ROOT.parent/'pgpt-runs/PG379/pg5224-current-permit-green-v1'
    prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    if set(before)!=set(after) or {key for key in before if before[key]!=after[key]}!=entry.KEYS:
        raise ValueError('exact Caddy outer/Child NativeIo changes only; other762 same byte')
    proofs={};targets={}
    for (module,name),kinds in KINDS.items():
        methods,hashed=bytecode.decode(RUN/'source',module,name)
        scopes=caller.callers(methods)
        if len(scopes)!=sum(kinds.values()):raise ValueError('exact four Caddy/Child scopes')
        factories=[]
        for needle,count in kinds.items():
            found=[m for m in methods if any(needle in op[2] for op in m['ops'])]
            if len(found)!=count:raise ValueError('exact factory '+name+needle)
            for method in found:
                factories.append({'method':method['header'],'acquisition':needle,'directReturnPcs':caller.tail(method,needle)})
        proofs[name]={'module':module,'scopes':scopes,'factories':factories,**hashed}
        report=ET.parse(RUN/('source/src/schubert-nk-'+module+'/target/site/jacoco/jacoco.xml')).getroot()
        target=bytecode.one([c for c in report.findall('package/class') if c.get('name')==name.replace('.','/')],
                            'one actual physical target counters')
        targets[name]={v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}
            for v in target.findall('counter') if v.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    value={'source':result['sourceSnapshot'],'actualExit':0,'physicalMain':764,'proofs':proofs,
        'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),'semanticClasses':2,'directoryFactories':2,
        'rawStreamFactories':2,'otherPhysicalClassesUnchanged':762,'targetClassCounters':targets,
        'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],'wholeHorizontalComplete':False,
        'formalAccepted':False,'nativeImported':False,'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5234-caddy-child-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'scopes':4,'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
