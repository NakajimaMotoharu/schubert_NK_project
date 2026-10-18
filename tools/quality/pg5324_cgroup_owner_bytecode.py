"""Actual six-slot primitive guard/registration and legacy FIFO no-heap drain, Owner four100."""
import json
import subprocess
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5242_startup_view_bytecode as primitive
import pg5250_startup_view_bytecode as loops
import pg5265_owned_factory_proof as proof
import pg5322_cgroup_owner_selected as entry

SOURCE='82426a6b20b83855da4a46f134d8f15981914669'
OUT='PG5324-cgroup-owner-bytecode-v1'
CLASS='dev.codex.schubert.nk.batch.platform.FixedUnitCgroupNamespace'


def main():
    run,value=proof.prove(entry=entry,run_name='pg5322-cgroup-owner-green-v1',
        prior_name='pg5314-readiness-stream-green-v1',source=SOURCE,tests=1086,suites=131,
        package='dev.codex.schubert.nk.batch.platform.',
        scopes={'FixedUnitCgroupNamespace':1,'FixedUnitCgroupNamespace$Owner':0},
        kinds={'FixedUnitCgroupNamespace':{},'FixedUnitCgroupNamespace$Owner':{}},out_name=OUT)
    owner,hashed=bytecode.decode(run/'source','batch',CLASS+'$Owner')
    ctor=bytecode.one([m for m in owner if '$Owner(' in m['header']],'one bounded owner constructor')
    arrays=[i for i,o in enumerate(ctor['ops']) if o[1]=='newarray']
    if len(arrays)!=2 or {ctor['ops'][i][2] for i in arrays}!={'int','boolean'} or any(
        ctor['ops'][i-1][1]!='bipush' or ctor['ops'][i-1][2]!='6' for i in arrays):
        raise ValueError('six primitive FD and six failure slots before native')
    if any('DirectoryCalls.' in o[2] for o in ctor['ops']):raise ValueError('constructor has no native IO')
    if any('Integer.valueOf:' in o[2] or 'ArrayList' in o[2] or o[1]=='checkcast' and 'java/lang/RuntimeException' in o[2]
            for m in owner for o in m['ops']):raise ValueError('no boxing/grow/generic Runtime cast')
    acquisitions={}
    for name in ('openRoot','openDirectory'):
        m=bytecode.one([m for m in owner if bytecode.named(m,name)],'one primitive '+name)
        acquisitions[name]=primitive.registration(m,'DirectoryCalls.'+name+':',unavailable='Method unavailable:')
    phases={name:bytecode.one([m for m in owner if bytecode.named(m,name)],'one '+name)
        for name in ('close','closeAfterKnown','drain','appendSecondary')}
    details={'close':loops.native_loop(phases['close'],{'closeAfterKnown','drain','appendSecondary'},direction=1),
        'known':loops.native_loop(phases['closeAfterKnown'],{'drain','appendSecondary'},direction=1),
        'drain':loops.native_loop(phases['drain'],set(),direction=1)}
    back=details['known']['loopBackPc']
    if any(o[0]<=back for o in phases['closeAfterKnown']['ops'] if o[1]=='new' or 'getSuppressed:' in o[2]):
        raise ValueError('no normalization or suppression-array inspection until all native attempts')
    if any('DirectoryCalls.' in o[2] for o in phases['appendSecondary']['ops']):
        raise ValueError('aggregation cannot touch native handles')
    if any('Method '+name+':' in o[2] for name,m in phases.items() for o in m['ops']):
        raise ValueError('no recursive drain/aggregation')
    verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-v','-classpath',
        str(run/'source/src/schubert-nk-batch/target/classes'),CLASS+'$Owner'],text=True)
    if 'ACC_SYNTHETIC' in verbose:raise ValueError('no synthetic Runtime throw escape')
    report=ET.parse(run/'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
    target=bytecode.one([c for c in report.findall('package/class') if c.get('name')==(CLASS+'$Owner').replace('.','/')],'current Owner')
    four={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}
        for c in target.findall('counter') if c.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    if len(four)!=4 or any(c['missed'] or not c['covered'] for c in four.values()):
        raise ValueError('every Owner line/method/class/branch must be covered')
    value.update(ownerClass=hashed,primitiveAcquisitions=acquisitions,drainPhases=details,ownerFourCounters=four,
        capacity=6,nativeCloseOrder='ACQUISITION_ORDER_0_TO_COUNT_MINUS1_PRESERVED',originalScopeSites=2,
        typedNativeCatchPrimaryPreserved=True,logicalConsumedNotKernelCloseAck=True,
        newJavaCases=8,nativeOwnerExecutionQualified=False)
    result=json.loads((run/'manifest.safe.json').read_bytes());value['storageFourCounters']=result['storageFourCounters']
    proof.publish(entry,value,OUT)


if __name__=='__main__':main()
