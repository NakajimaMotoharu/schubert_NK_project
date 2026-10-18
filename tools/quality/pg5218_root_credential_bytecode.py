"""Actual11 Root reader scopes, rawDirectory8/channel3, same original776 source only."""
import json
import os
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
import pg5216_root_credential_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5216-root-credential-green-v1'
PACKAGE='dev.codex.schubert.nk.batch.file.'
KINDS={'RootReleaseApprovalReader':(2,3,1),'RootServiceCredentialSource':(1,2,1),'RootBatchCredentialReader':(0,0,1)}


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes())
    if result['actualExit']!=0 or result['phaseExits']!=[0,0] or result['tests']!=776 or result['suites']!=92:
        raise ValueError('original776/92 complete first')
    prior_run=selected.ROOT.parent/'pgpt-runs/PG379/pg5208-maintenance-run-green-v1'
    prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    required={entry.PREFIX+n+'.class' for n in entry.OUTERS};optional={entry.PREFIX+n+'.class' for n in entry.DEBUG}
    changed={key for key in before if key in after and before[key]!=after[key]}
    if set(before)!=set(after) or not required<=changed or not changed<=required|optional:
        raise ValueError('only three reader outer semantics plus declared nested candidates')
    proofs={}
    for name,counts in KINDS.items():
        methods,hashed=bytecode.decode(RUN/'source','batch',PACKAGE+name)
        scopes=caller.callers(methods)
        if len(scopes)!=sum(counts):raise ValueError('exact reader scope count')
        factories=[]
        for needle,count in zip(('OwnedTransferDirectory.open:','OwnedTransferDirectory.openExistingChild:','$Io.open:'),counts):
            found=[m for m in methods if any(needle in op[2] for op in m['ops'])]
            if len(found)!=count:raise ValueError('exact factory '+name+needle)
            for method in found:
                factories.append({'method':method['header'],'acquisition':needle,'directReturnPcs':caller.tail(method,needle)})
        proofs[name]={'scopes':scopes,'factories':factories,**hashed}
    debug=[]
    for key in sorted(changed-required):
        name=key.split(':',1)[1][:-6].replace('/','.')
        old,old_hash=bytecode.decode(prior_run/'source','batch',name)
        current,current_hash=bytecode.decode(RUN/'source','batch',name)
        native.require_reference(before,key,old_hash['classSha256']);native.same_methods(old,current)
        debug.append({'class':name,'old':old_hash,'current':current_hash,'allOpcodeHandlerSemanticsEqual':True})
    report=ET.parse(RUN/'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
    targets={c.get('name'):{v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}
        for v in c.findall('counter') if v.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
        for c in report.findall('package/class') if c.get('name') in {PACKAGE.replace('.','/')+n for n in KINDS}}
    if len(targets)!=3:raise ValueError('exact3 physical target counters')
    value={'source':result['sourceSnapshot'],'actualExit':0,'physicalMain':764,'proofs':proofs,
        'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),'semanticClasses':3,'directoryFactories':8,
        'rawChannelFactories':3,'nestedDebugEquivalent':debug,'otherPhysicalClassesUnchanged':761-len(debug),
        'targetClassCounters':targets,'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],
        'wholeHorizontalComplete':False,'formalAccepted':False,'nativeImported':False,'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5218-root-credential-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'scopes':11,'debugCount':len(debug),'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
