"""Service raw factories, four prebuilt owned boundaries and protected secret clearing."""
import pg5265_owned_factory_proof as proof
import pg5138_factory_bytecode as bytecode
import pg5332_service_resources_selected as entry

SOURCE='c2f1636fe'
CLASS='dev.codex.schubert.nk.api.file.ServiceProcessResources'


def main():
    source=bytecode.subprocess.check_output(['git','rev-parse',SOURCE],cwd=entry.selected.ROOT,text=True).strip()
    run,value=proof.prove(entry=entry,run_name='pg5332-service-resources-green-v1',
        prior_name='pg5322-cgroup-owner-green-v1',source=source,tests=1090,suites=132,
        package='dev.codex.schubert.nk.api.file.',scopes={'ServiceProcessResources':4},
        kinds={'ServiceProcessResources':{'OwnedTransferDirectory.open:':1,'ServiceCredentialSet.load:':1,
            '$SourceFactory.open:':1,'$PoolFactory.open:':1}},
        out_name='PG5334-service-resources-bytecode-v1',module='bootstrap')
    methods,hashed=bytecode.decode(run/'source','bootstrap',CLASS)
    factory=bytecode.one([m for m in methods if any('$SourceFactory.open:' in o[2] for o in m['ops'])],'one source factory')
    if any('Arrays.fill:' in o[2] for o in factory['ops']):
        raise ValueError('factory returns owned source before protected password clearing')
    body=bytecode.one([m for m in methods if any('$PoolFactory' in o[2] and o[1]=='invokedynamic' for o in m['ops'])],
        'one protected source action constructing pool ports')
    fills=[o[0] for o in body['ops'] if 'Arrays.fill:' in o[2]]
    acquisitions=[o[0] for o in body['ops'] if 'ResourceScope.acquire:' in o[2]]
    if len(fills)!=1 or len(acquisitions)!=1 or fills[0]>=acquisitions[0]:
        raise ValueError('password cleared in protected source action before pool acquisition')
    outer=bytecode.one([m for m in methods if bytecode.named(m,'withDatabase')],'one source outer finally')
    if sum('Arrays.fill:' in o[2] for o in outer['ops'])!=2 or not outer['handlers']:
        raise ValueError('password finally handles normal and exceptional factory/port failures')
    retained=bytecode.one([m for m in methods if bytecode.named(m,'retainUnconfirmed')],'one retained frame')
    if sum('Thread.sleep:' in o[2] for o in retained['ops'])!=1 or any(o[1].endswith('return') for o in retained['ops']):
        raise ValueError('UNKNOWN retained frame never returns or retries native release')
    if not any('InterruptedException' in str(h) for h in retained['handlers']):
        raise ValueError('interrupt is observation only, not release acknowledgement')
    value.update(passwordClearingProtectedBeforePool=True,passwordFactoryFailureFinally=True,
        retainingFrameNonReturning=True,sourceClass=hashed,newJavaCases=4,implementationDecision='PG-D427')
    proof.publish(entry,value,'PG5334-service-resources-bytecode-v1')


if __name__=='__main__':main()
