"""Seven Directory owners plus direct helper refs; all optional nested method-code differences explicit."""
import subprocess
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5288_morning_launch_selected as entry
import pg5265_owned_factory_proof as proof

SOURCE='6f8d42065ce19f79edc8e54dd99f991eda1a06a4'
OUT='PG5290-morning-launch-bytecode-v1'


def enclosing(snapshot,name):
    classes=snapshot/'src/schubert-nk-batch/target/classes'
    raw=subprocess.check_output([str(bytecode.JAVAP),'-p','-v','-classpath',str(classes),name],text=True)
    return [line.partition('//')[2].strip() for line in raw.splitlines() if line.startswith('EnclosingMethod:')]


def main():
    run,value=proof.prove(entry=entry,run_name='pg5288-morning-launch-green-v1',
        prior_name='pg5280-morning-execution-green-v1',source=SOURCE,tests=1005,suites=124,
        package='dev.codex.schubert.nk.batch.file.',
        scopes={'MorningNewRunAdmission$1':1,'MorningResumeAdmission$1':1,'MorningStartupLaunchOwner':3,'MorningProcessMain':2},
        kinds={'MorningNewRunAdmission$1':{},'MorningResumeAdmission$1':{},
               'MorningStartupLaunchOwner':{'OwnedTransferDirectory.open:':3},
               'MorningProcessMain':{'OwnedTransferDirectory.open:':2}},out_name=OUT)
    package='dev.codex.schubert.nk.batch.file.';refs=[]
    for name,helper in [('MorningNewRunAdmission$1','MorningNewRunAdmission.openCredentials'),
                        ('MorningResumeAdmission$1','MorningNewRunAdmission.openCredentials'),
                        ('MorningProcessMain','MorningProcessMain.openRequests'),
                        ('MorningProcessMain','MorningProcessMain.openCurrent')]:
        raw=subprocess.check_output([str(bytecode.JAVAP),'-p','-v','-classpath',
            str(run/'source/src/schubert-nk-batch/target/classes'),package+name],text=True)
        needle='REF_invokeStatic dev/codex/schubert/nk/batch/file/'+helper+':()Ldev/codex/schubert/nk/storage/OwnedTransferDirectory;'
        if needle not in raw:raise ValueError('exact raw helper reference '+helper)
        refs.append({'class':name,'helper':helper})
    methods,hashed=bytecode.decode(run/'source','batch',package+'MorningNewRunAdmission')
    helper=bytecode.one([m for m in methods if bytecode.named(m,'openCredentials')],'fixed credential helper')
    tail=caller.tail(helper,'OwnedTransferDirectory.open:')
    prior=entry.selected.ROOT.parent/'pgpt-runs/PG379/pg5280-morning-execution-green-v1/source'
    for row in value['nestedDebugEquivalent']:
        before=enclosing(prior,row['class']);after=enclosing(run/'source',row['class'])
        row.update(enclosingMethodBefore=before,enclosingMethodAfter=after,
            enclosingMethodEqual=before==after,pureDebugDifferenceNotAsserted=True)
    value.update(rawDirectoryFactories=7,directHelperReferences=refs,credentialHelperRawReturnPcs=tail,
        credentialHelperClass=hashed,nativeOwnerExecutionQualified=False)
    proof.publish(entry,value,OUT)


if __name__=='__main__':main()
