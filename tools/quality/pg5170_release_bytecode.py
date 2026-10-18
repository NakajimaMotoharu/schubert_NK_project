"""Actual16 factory-return scopes, exact two outer changes and bounded optional nested debug."""
import json
import os
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
import pg5168_release_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5168-release-scopes-green-v1'
PACKAGE='dev.codex.schubert.nk.bootstrap.'
FACTORIES={
 'ReleasePayloadVerification':{
   'OwnedTransferDirectory.openExistingChild:':2,'StartupReleaseManifest$Io.names:':1,
   'StartupReleaseManifest$Io.open:':1,'StartupReleaseManifest$Io.archive:':1,
   'java/util/zip/ZipFile.getInputStream:':1,'java/io/BufferedReader."<init>":':1},
 'StartupReleaseManifest':{
   'OwnedTransferDirectory.open:':2,'OwnedTransferDirectory.openExistingChild:':6,
   'StartupReleaseManifest$Io.open:':1},
}


def physical_delta(before,after):
    required={entry.PREFIX+n+'.class' for n in FACTORIES}
    optional={entry.PREFIX+n+'.class' for n in entry.DEBUG}
    changed={key for key in before if key in after and before[key]!=after[key]}
    if set(before)!=set(after) or not required<=changed or not changed<=required|optional:
        raise ValueError('two exact outer changes and bounded optional nested debug only')
    return sorted(changed- required)


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes())
    if result['actualExit']!=0 or result['tests']!=537 or result['suites']!=73:
        raise ValueError('complete current537/73 before independent proof')
    prior_run=selected.ROOT.parent/'pgpt-runs/PG379/pg5164-readonly-agent-green-v1'
    prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    debug_keys=physical_delta(prior['mainDelta']['physicalSha256'],result['mainDelta']['physicalSha256'])
    proofs={}
    for name,needles in FACTORIES.items():
        methods,hashed=bytecode.decode(RUN/'source','bootstrap',PACKAGE+name)
        sites=caller.callers(methods)
        expected=sum(needles.values())
        if len(sites)!=expected:raise ValueError('all actual owned scopes required')
        returns=[]
        for needle,count in needles.items():
            found=[m for m in methods if any(needle in op[2] for op in m['ops'])]
            if len(found)!=count:raise ValueError('exact factory category '+needle)
            for method in found:
                returns.append({'method':method['header'],'acquisition':needle,
                                'directReturnPcs':caller.tail(method,needle)})
        proofs[name]={'scopes':sites,'factoryReturns':returns,**hashed}
    debug=[]
    for key in debug_keys:
        name=key.split(':',1)[1][:-6].replace('/','.')
        before,before_hash=bytecode.decode(prior_run/'source','bootstrap',name)
        after,after_hash=bytecode.decode(RUN/'source','bootstrap',name)
        native.require_reference(prior['mainDelta']['physicalSha256'],key,before_hash['classSha256'])
        native.same_methods(before,after)
        debug.append({'class':name,'prior':before_hash,'current':after_hash,'semanticsEqual':True})
    xml=RUN/'source/src/schubert-nk-bootstrap/target/site/jacoco/jacoco.xml'
    cls=bytecode.one([c for c in ET.parse(xml).getroot().findall('package/class')
         if c.get('name')=='dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile'],'one measured coverage class')
    checked=bytecode.one([m for m in cls.findall('method') if m.get('name')=='checked'],'one metadata boundary')
    def counters(element):
        return {c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}
                for c in element.findall('counter')}
    checked_counts=counters(checked);class_counts=counters(cls)
    if checked_counts['BRANCH']['missed'] or class_counts['BRANCH']['missed']:
        raise ValueError('full bootstrap context plus readonly metadata vector must close measured branch gap')
    value={'source':result['sourceSnapshot'],'actualExit':0,'proofs':proofs,'physicalMain':764,
       'newOuterChanges':2,'debugEquivalent':debug,'otherPhysicalClassesUnchanged':762-len(debug),
       'previousSource':prior['sourceSnapshot'],'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),
       'metadataCheckedCounters':checked_counts,'coverageDirectoryClassCounters':class_counts,
       'metadataBranch100':True,'targetClassBranch100':True,'wholeFourCounters100':False,
       'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],'wholeHorizontalComplete':False,
       'formalAccepted':False,'nativeImported':False,'actualHeapOomReproduced':False,'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5170-release-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'scopes':16,'debugCount':len(debug),'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
