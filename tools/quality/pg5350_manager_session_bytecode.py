"""Manager acquisition ports, immediate pending registration and post-release finally."""
import subprocess
import pg5265_owned_factory_proof as proof
import pg5138_factory_bytecode as bytecode
import pg5348_manager_session_selected as entry

SOURCE='6c212913dd407d4f35a9aac8553e724eea3bc887'
RUN='pg5348-manager-session-green-v1'
OUT='PG5350-manager-session-bytecode-v1'
CLASS='dev.codex.schubert.nk.bootstrap.SystemManagerObservation'


def main():
    run,value=proof.prove(entry=entry,run_name=RUN,prior_name='pg5340-service-resources-green-v2',
        source=SOURCE,tests=1092,suites=132,package='dev.codex.schubert.nk.bootstrap.',
        scopes={'SystemManagerObservation':1},kinds={'SystemManagerObservation':{}},
        out_name=OUT,module='bootstrap')
    methods,hashed=bytecode.decode(run/'source','bootstrap',CLASS)
    read=bytecode.one([m for m in methods if bytecode.named(m,'read')],'one fixed manager read')
    acquire=bytecode.index_of(read,'ResourceScope.acquire:')
    closed=[i for i,o in enumerate(read['ops']) if '$Session.closed:' in o[2]]
    if len(closed)!=2 or any(i<=acquire for i in closed) or not read['handlers']:
        raise ValueError('normal/exceptional closed observation belongs after release in outer finally')
    body=bytecode.one([m for m in methods if 'lambda$read$' in m['header']
        and any('$Session.start:' in o[2] for o in m['ops'])],'protected session action')
    registered=bytecode.index_of(body,'Field pending:')
    if body['ops'][registered][1]!='putfield' or any(o[1] not in ('aload_0','aload_1','aload_2','aload_3','aload')
        for o in body['ops'][:registered]):
        raise ValueError('only primitive reference loads before pending registration')
    verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-v','-classpath',
        str(run/'source/src/schubert-nk-bootstrap/target/classes'),CLASS],text=True)
    if 'REF_invokeInterface dev/codex/schubert/nk/bootstrap/SystemManagerObservation$Factory.create:' not in verbose:
        raise ValueError('original factory directly returns actual owned session')
    value.update(sourceClass=hashed,pendingRegistrationFirst=True,closedAfterReleaseNormalAndExceptional=True,
        factoryDirectMethodReference=True,newJavaCasesInGroup=2,implementationDecision='PG-D428')
    proof.publish(entry,value,OUT)


if __name__=='__main__':main()
