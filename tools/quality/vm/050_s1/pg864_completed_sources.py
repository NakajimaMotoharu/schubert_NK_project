"""Explicit module-scope complete source assembly; no genuine/pending old profile."""
import ast,inspect
from pathlib import Path
from pg863_stage_candidate_v6 import source as stage_source
from pg835_pending_v5 import METHOD,ORACLE
R=Path(__file__).resolve().parent
def java():
    raw=(R/'Pg864CompletedDeployment.java').read_text()
    marker='  static boolean readOnlyMount(String table,String target){throw new AssertionError("assembly required");}'
    assert raw.count(marker)==1
    method=METHOD.replace('PG832','PG862').replace('\\\\n','\\n')
    return raw.replace(marker,method)
def java_test():
    raw=(R/'Pg864CompletedDeploymentTest.java').read_text()
    return raw.replace('// MOUNT_ORACLE',ORACLE.replace('Pg835PendingDeployment','Pg864CompletedDeployment').replace('PG832','PG862').replace('PG835','PG864').replace('\\\\n','\\n'))
def refs():
    from pg864_finite_delta import finite_trees
    tree=ast.parse(stage_source());payload=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='PAYLOAD'for x in n.targets))
    p=ast.parse(payload);outer=next(n for n in p.body if isinstance(n,ast.With))
    stop=next(i for i,n in enumerate(outer.body)if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='before'for x in n.targets))
    definitions=p.body[:p.body.index(outer)]+outer.body[:stop]
    raw=ast.unparse(ast.Module(body=definitions,type_ignores=[]))+'\n'
    raw=raw.replace('validate_baseline(comparable, baseline, list(pathlib.Path(\'/run/systemd/system/schubert-nk-morning-controller.service.d\').iterdir()))','validate_current(comparable, baseline, list(pathlib.Path(\'/run/systemd/system/schubert-nk-morning-controller.service.d\').iterdir()))')
    assert 'validate_current(comparable' in raw
    raw+=(R/'pg864_finite_delta.py').read_text()+'\n'+(R/'pg864_completed_refs_body.py').read_text()
    ast.parse(raw);return raw
def sources():
    result={'Pg864CompletedDeployment.java':java(),'Pg864CompletedDeploymentTest.java':java_test(),'pg864_completed_refs.py':refs()}
    for name in ('Pg797OwnedDatabase.java','Pg797OwnedDatabaseTest.java','Pg798DatabaseScope.java','Pg798DatabaseScopeTest.java'):result[name]=(R/name).read_text()
    return result
