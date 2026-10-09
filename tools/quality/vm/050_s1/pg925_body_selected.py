"""Two changed leaves, qualified protocol/storage unchanged, no root-am offline prefix."""
import inspect,json,hashlib,zipfile
from pathlib import Path
import pg743_closing_selected as selected
selected.D=selected.W/'pg925-body-selected-v1'
selected.TESTS={'bootstrap':['ChildBrokerTest','ChildCaddyTest','ChildStartupContextTest','MaintenanceOwnerFrameTest'],
                'api':['InspectorApplicationTest','InspectorEntryBoundaryTest','InspectorLauncherTest','InspectorProcessTest']}
def dependencies():
    result={};host=selected.W/'pg915-snapshot-six-host-v1'
    def classes(p):
        with zipfile.ZipFile(p)as z:return{n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
    for m in ('protocol','storage'):
        name='schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar';frozen=host/m/name;cached=Path('/home/mini/codex/project1/work/toolchain/m2/repository/dev/codex/schubert')/('schubert-nk-'+m)/'0.1.0-SNAPSHOT'/name
        assert classes(frozen)==classes(cached);result[m]=len(classes(frozen))
    return result
if __name__=='__main__':
    print(json.dumps({'dependencyMainClasses':dependencies(),'classByteMismatch':0}),flush=True)
    raw=inspect.getsource(selected.main)
    marker="'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',";assert raw.count(marker)==1
    raw=raw.replace(marker,"'src/schubert-nk-bootstrap,src/schubert-nk-api',").replace('PG743-closing-selected-v1','PG925-body-selected-v1').replace('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','e01612fcd7f2752df5ae0836b78538fd5e87f120')
    env=dict(selected.__dict__);exec(compile(raw,'<PG925 new body/UID candidate>','exec'),env);env['main']()
