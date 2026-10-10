"""Current40ef eight qualified streams + one Bootstrap process/two dumps, no old source."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
    raw=(R/'pg903_bootstrap_native_counter.py').read_text()
    changes=(('e01612fcd7f2752df5ae0836b78538fd5e87f120','40ef6e894573d2ffab1d1732124960f9c98d5f97'),('pg894','pg983'),('pg901-bootstrap-post-v3','pg989-bootstrap-post-v4'),('pg892-current-sixteen-native-v1','pg972-current-eight-native-v2'),('56387c9cd6fc198ca5fd1fd8824b6d5e794ef743c82e5e3e657891a9f4cb5d48','043e7c88400840fd945512548c70a2d8dda2e53a6d9e2f6b5b5855bd0bab3d8b'),("old_record['qualifiedCohortManifestHashes'].items()","[(old.name,sha(old/'manifest.safe.json'))]"),('len(prior)==16','len(prior)==8'),('for s in sessions})==16','for s in sessions})==8'),('pg903-current-eighteen-native-v1','pg992-current-ten-native-v1'),('PG903-current-eighteen-native-v1','PG992-current-ten-native-v1'),('pg857-completed-reference-six-host-v1','pg926-body-six-host-v1'),("h['tests']==3541","h['tests']==3560"),("cohorts[0]['hostExecHashes']==cohorts[1]['hostExecHashes']","len(cohorts)==1 and cohorts[0]['hostExecHashes']==old_record['hostExecHashes']"),("'hostRun':'PG857'","'hostRun':'PG926'"),('previousSixteenManifestSha256','previousEightManifestSha256'),("'currentNativeStreams':18","'currentNativeStreams':10"),("'distinctCurrentProcesses':17","'distinctCurrentProcesses':9"),('incrementalVsPG892','incrementalVsPG972'),("'streams':18","'streams':10"))
    for a,b in changes:assert raw.count(a)>0,a;raw=raw.replace(a,b)
    # Root-to-ordinary exec can keep one OS PID. Unique sessions are JVM executions.
    assert raw.count("'distinctCurrentProcesses':9")==1
    raw=raw.replace("'distinctCurrentProcesses':9","'distinctCurrentJvmExecutions':9,'distinctOsProcessCount':None")
    marker="post=json.loads((W/'pg989-bootstrap-post-v4.safe.json').read_bytes());";assert raw.count(marker)==1
    raw=raw.replace(marker,marker+"assert post['run']=='PG989-bootstrap-post-v4';")
    ast.parse(raw);return raw
if __name__=='__main__':exec(compile(source(),'<992 ten current native only>','exec'),{'__file__':str(R/'pg992_current_bootstrap_native_counter.py'),'__name__':'__main__'})
