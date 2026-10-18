"""Direct UNKNOWN loops retain catch frames; every Service resource counter is observed."""
import pg5265_owned_factory_proof as proof
import pg5138_factory_bytecode as bytecode
import pg5332_service_resources_selected as entry

SOURCE='7aa3ab90c26701a6cce96fe92151e85a802fb3cb'
RUN='pg5340-service-resources-green-v2'
OUT='PG5342-service-resources-bytecode-v1'
CLASS='dev.codex.schubert.nk.api.file.ServiceProcessResources'


def main():
    run,value=proof.prove(entry=entry,run_name=RUN,prior_name='pg5332-service-resources-green-v1',
        source=SOURCE,tests=1090,suites=132,package='dev.codex.schubert.nk.api.file.',
        scopes={'ServiceProcessResources':4},kinds={'ServiceProcessResources':{
            'OwnedTransferDirectory.open:':1,'ServiceCredentialSet.load:':1,
            '$SourceFactory.open:':1,'$PoolFactory.open:':1}},out_name=OUT,module='bootstrap')
    methods,hashed=bytecode.decode(run/'source','bootstrap',CLASS)
    retain=[m for m in methods if any('Method observeUnconfirmed:' in o[2] for o in m['ops'])]
    if len(retain)!=2:raise ValueError('both original and typed release retain their own catch frame')
    for method in retain:
        observe=bytecode.one([o for o in method['ops'] if 'Method observeUnconfirmed:' in o[2]],'one observation call')
        jumps=[o for o in method['ops'] if o[1]=='goto' and int(o[2])==observe[0]]
        if len(jumps)!=1 or not method['handlers']:raise ValueError('non-returning loop belongs to caught release failure')
        for kind in ('IOException','RuntimeException','Error'):
            if not any(kind in str(h) for h in method['handlers']):raise ValueError('all native failure classes retained')
    tick=bytecode.one([m for m in methods if bytecode.named(m,'observeUnconfirmed')],'single observation tick')
    if sum('Thread.sleep:' in o[2] for o in tick['ops'])!=1 or not any('InterruptedException' in str(h) for h in tick['handlers']):
        raise ValueError('observation tick is interrupt tolerant and does not release anything')
    if any('close:' in o[2] for o in tick['ops']):raise ValueError('observation cannot retry release')
    body=bytecode.one([m for m in methods if sum('Arrays.fill:' in o[2] for o in m['ops'])==1
        and any('ResourceScope.acquire:' in o[2] for o in m['ops'])],'protected source action')
    if bytecode.index_of(body,'Arrays.fill:')>=bytecode.index_of(body,'ResourceScope.acquire:'):
        raise ValueError('password cleared before pool operation or retaining release')
    outer=bytecode.one([m for m in methods if bytecode.named(m,'withDatabase')],'source factory finally')
    if sum('Arrays.fill:' in o[2] for o in outer['ops'])!=2 or not outer['handlers']:
        raise ValueError('factory failures still clear password')
    counters=value['targetClassCounters'][CLASS.replace('.','/')]
    if set(counters)!={'LINE','METHOD','CLASS','BRANCH'} or any(c['missed'] or not c['covered'] for c in counters.values()):
        raise ValueError('entire ServiceProcessResources four100 required without exclusion')
    value.update(serviceFourCounters=counters,sourceClass=hashed,allFourProtected=True,
        retainedOriginalCatchFrames=2,passwordClearedBeforePool=True,passwordFailureFinally=True,
        implementationDecision='PG-D427',newJavaCasesInGroup=4,newJavaCasesInThisSource=0,
        previousLimitedRun='PG5332; partial coverage5line1branch; never imported',
        failedCurrentV1='PG5340-v1; testCompile import failure;186/25 not accepted')
    proof.publish(entry,value,OUT)


if __name__=='__main__':main()
