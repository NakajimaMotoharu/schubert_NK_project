"""FFM out ownership before C, primitive returned registration, retained UNKNOWN, full counters."""
import subprocess
import pg5265_owned_factory_proof as proof
import pg5138_factory_bytecode as bytecode
import pg5356_ffm_outputs_selected as entry

SOURCE='8558eed7c8d3aa873af35a03d85b59df0a3e37d1'
RUN='pg5364-ffm-outputs-green-v1'
OUT='PG5366-ffm-outputs-bytecode-v1'
CLASS='dev.codex.schubert.nk.bootstrap.LinuxSystemdSession'


def state_registration(method):
    calls=[i for i,o in enumerate(method['ops']) if 'Method call:' in o[2]]
    if len(calls)!=1:raise ValueError('one prepared native call')
    call=calls[0]
    before=[i for i,o in enumerate(method['ops'][:call]) if o[1]=='bastore']
    after=[i for i,o in enumerate(method['ops']) if i>call and o[1]=='bastore']
    if len(before)!=1 or len(after)!=1 or method['ops'][before[0]-1][1]!='iconst_1' or method['ops'][after[0]-1][1]!='iconst_2':
        raise ValueError('pending before C and returned immediately on normal return')
    if any(o[1].startswith('invoke') or o[1] in ('new','anewarray','newarray','multianewarray')
        for o in method['ops'][call+1:]):
        raise ValueError('normal C return cannot allocate or call before primitive registration/return')
    if method['ops'][-1][1]!='areturn':raise ValueError('actual native result returned directly')
    return {'pendingStorePc':method['ops'][before[0]][0],'nativeCallPc':method['ops'][call][0],
            'returnedStorePc':method['ops'][after[0]][0]}


def main():
    run,value=proof.prove(entry=entry,run_name=RUN,prior_name='pg5348-manager-session-green-v1',
        source=SOURCE,tests=1099,suites=132,package='dev.codex.schubert.nk.bootstrap.',
        scopes={'LinuxSystemdSession':4,'LinuxSystemdSession$Factory':0},
        kinds={'LinuxSystemdSession':{},'LinuxSystemdSession$Factory':{}},out_name=OUT,module='bootstrap')
    methods,hashed=bytecode.decode(run/'source','bootstrap',CLASS)
    constructor=bytecode.one([m for m in methods if 'LinuxSystemdSession(' in m['header']],'one session constructor')
    arrays=[(i,o) for i,o in enumerate(constructor['ops']) if o[1] in ('newarray','anewarray')]
    if len(arrays)!=2 or {o[1] for _,o in arrays}!={'newarray','anewarray'} or any(
        constructor['ops'][i-1][1]!='iconst_3' for i,_ in arrays):
        raise ValueError('three out buffers and three primitive states are constructor-owned')
    if sum('Method pointer:' in o[2] for o in constructor['ops'])!=3 or any('Calls.call:' in o[2] for o in constructor['ops']):
        raise ValueError('all three output buffers before any native acquisition')
    call=bytecode.one([m for m in methods if bytecode.named(m,'callOutput')],'one call registration')
    registration=state_registration(call)
    sites=[m['header'] for m in methods for o in m['ops'] if 'Method callOutput:' in o[2]]
    if len(sites)!=5:raise ValueError('bus and all four ephemeral output acquisitions registered')
    free=bytecode.one([m for m in methods if bytecode.named(m,'releaseOutput')],'one owned output release')
    consume=[i for i,o in enumerate(free['ops']) if o[1]=='bastore' and free['ops'][i-1][1]=='iconst_3']
    decode=[i for i,o in enumerate(free['ops']) if 'MemorySegment.get:' in o[2]]
    if len(consume)!=1 or len(decode)!=1 or consume[0]>=decode[0] or not free['handlers']:
        raise ValueError('unconfirmed state precedes pointer decode/release, caught failures retained')
    close=bytecode.one([m for m in methods if bytecode.named(m,'close')],'one session close')
    if bytecode.index_of(close,'Method releaseOutput:')>=bytecode.index_of(close,'Arena.close:'):
        raise ValueError('bus consumption precedes arena close')
    if not close['handlers'] or not any('Field uncertain:' in o[2] and o[1]=='putfield' for o in close['ops']):
        raise ValueError('arena close failure must become sticky UNKNOWN')
    direct=bytecode.one([m for m in methods if bytecode.named(m,'release')],'known nonzero native release')
    if any('MemorySegment.address:' in o[2] for o in direct['ops'][:bytecode.index_of(direct,'Method call:')]):
        raise ValueError('duplicate zero test removed; sole caller admits nonzero first')
    if sum('Method release:' in o[2] for m in methods for o in m['ops'])!=1:
        raise ValueError('known-nonzero release has exactly one admitted caller')
    factory,_=bytecode.decode(run/'source','bootstrap',CLASS+'$Factory')
    if sum('ResourceScope.handoff:' in o[2] for m in factory for o in m['ops'])!=1:
        raise ValueError('Arena to complete Session is protected by one handoff')
    verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-v','-classpath',
        str(run/'source/src/schubert-nk-bootstrap/target/classes'),CLASS+'$Factory'],text=True)
    if 'REF_invokeStatic java/lang/foreign/Arena.ofConfined:' not in verbose:
        raise ValueError('production factory still creates confined Arena only')
    for counts in value['targetClassCounters'].values():
        if set(counts)!={'LINE','METHOD','CLASS','BRANCH'} or any(c['missed'] or not c['covered'] for c in counts.values()):
            raise ValueError('entire Session and Factory four100, no exclusions')
    value.update(primitiveCallState=registration,registeredNativeSites=sites,
        threeStrongOutputSlotsBeforeNative=True,releaseUnconfirmedBeforeDecode=True,
        arenaCloseUnknownSticky=True,constructorHandoffProtected=True,sourceClass=hashed,
        newJavaCasesInGroup=7,originalScopeSites=4,additionalBoundariesOutsideOriginal=2,
        implementationDecision='PG-D429',prototypeRun='PG5356/e5501097; partial counters; no imports')
    value['bugs'].append('BUG1444');value['ykt'].append('YKT1208')
    proof.publish(entry,value,OUT)


if __name__=='__main__':main()
