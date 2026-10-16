"""SSC300: current825e existing20 tool graph; history is a template, never authority."""
import ast
import inspect
import json
from pathlib import Path
import pg1719_current_bootstrap_sources as template
import pg1728_bootstrap_abi_sources as abi
import pg4818_new_current_bootstrap_before as before

SOURCE,BOM,W=before.SOURCE,before.BOM,before.admission.W
TOOLS='pg4820-new-current-bootstrap-tools-v2'
BASELINE='d8fbc2f16e781ae7dcaa3b90a4f41768ac2aeb8d086c9318e1e5e56741c2a9b8'


def current_text(raw):
    pairs=[('Pg1719','Pg4820'),('PG1719','PG4820'),('pg1719-current-bootstrap-tools-v1',TOOLS),('pg1719','pg4820'),
           ('2741c4546afad6c1e8b6efbd53dfb58144edf7bb',SOURCE),
           ('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',BOM),
           ('PG1638','PG4702'),('pg1638','pg4702'),
           ('3d69f5af-6bac-46b1-a540-7591c4a79a0d','79a3260a-e16d-42bf-942a-b914ed144c28'),
           ('3d69f5af6bac46b1a5407591c4a79a0d','79a3260ae16d42bf942ab914ed144c28'),
           ('02e941b9-1c52-4018-a193-63dd00b269af','fff841d9-2554-4680-b17d-9548bfa79cbb'),
           ('2026-10-12T14:19:28.968927Z','2026-10-16T22:12:38.570783Z'),
           ('40da389f-23fc-4ad4-a71b-cf72a6bd5a62','7ab6c953-b2fc-47ae-be96-26a3196ca76d'),
           ('2026-10-12T14:45:34.509749Z','2026-10-16T22:39:38.673291Z'),
           ('fe43e94b1fbf4886bb4ab3922fd16f9c','b414b0e1e5ac47e8b5fb8c5ae3d94348'),
           ('68542820690','189659374308'),('pg1718-current-bootstrap-before-v1',before.SLOT),
           ('pg1703','pg4772'),('==674','==874')]
    for old,new in pairs:raw=raw.replace(old,new)
    return raw


def _template_function(module,discard,bindings):
    """Extract code after the explicitly replaced historical eligibility prefix."""
    node=ast.parse(inspect.getsource(module.files)).body[0]
    if not isinstance(node,ast.FunctionDef)or not isinstance(node.body[discard],ast.Assign):
        raise ValueError('exact template construction boundary')
    if [ast.unparse(n.targets[0])for n in node.body if isinstance(n,ast.Assign)][:2]not in (['before','result'],['post','result']):
        raise ValueError('historical prefix shape changed')
    node.body=node.body[discard:]
    ns={**vars(module),**bindings}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<template, not eligibility>','exec'),ns)
    return ns['files']


def eligibility(baseline_sha):
    value=json.loads((W/before.SLOT/'manifest.safe.json').read_bytes());result=value['result']
    if not(type(value['actualExit'])is int and value['actualExit']==0 and value['source']==SOURCE
           and result['productionSource']==SOURCE and result['actualExit']==0
           and result['beforeSha256']==baseline_sha==BASELINE and result['batchRows']==874
           and result['nativePhysicalFiles']==70 and all(result[k]is True for k in
           ('whole24Full32Signed187AndResourcesUnchanged','existingSingleAdminVerified',
            'bootstrapCredentialsAbsent','emptyFourNamespacesVerified','normalNewReferences','startsStopsWrites0'))):
        raise ValueError('actual4818 full current baseline required; history cannot authorize')
    return result


def files(baseline_sha):
    eligibility(baseline_sha)
    # Original constructors are reused; old success receipts are not read as permissions.
    raw=_template_function(template,2,{}) (baseline_sha)
    values={current_text(n):current_text(v)for n,v in raw.items()}
    values['pg4772_parent_receipt.py']=(W/'pg4772-new-current-owned-tools-v1/pg4772_parent_receipt.py').read_text()
    # Preserve the proven constructor/null/liveness fixes without old recovery1727 authority.
    def rebind(text):
        for old,new in [('Pg1728','Pg4820'),('PG1728','PG4820'),('pg1728', 'pg4820')]:text=text.replace(old,new)
        return text
    built=values
    root=Path(template.__file__).parent/'vm/050_s1'
    db=(root/'Pg797OwnedDatabase.java').read_text().replace('Pg797OwnedDatabase','Pg4820OwnedDatabase').replace('PG[0-9]{3}-','PG[0-9]{3,4}-')
    db=db.replace('Objects.requireNonNull(role);Objects.requireNonNull(application);Objects.requireNonNull(database);','if(role==null||application==null||database==null)throw new IllegalArgumentException("fixed database expectation unavailable");')
    built['Pg4820OwnedDatabase.java']=db
    built['Pg4820OwnedDatabaseTest.java']=(root/'Pg797OwnedDatabaseTest.java').read_text().replace('Pg797OwnedDatabase','Pg4820OwnedDatabase')
    built['Pg4820BootstrapExpectedTest.java']=rebind(abi.EXPECTED_TEST)
    java=built['Pg4820BootstrapExisting.java']
    # The actual current parent ended with the approved WARNING10, not historical SUCCESS0.
    if java.count('done.outcome()==MaintenanceCompletion.Outcome.SUCCESS')!=1:raise ValueError('one genuine parent outcome')
    java=java.replace('done.outcome()==MaintenanceCompletion.Outcome.SUCCESS','done.outcome()==MaintenanceCompletion.Outcome.WARNING')
    java=java.replace('Pg797OwnedDatabase','Pg4820OwnedDatabase')
    old='beforeOwnership(Pg4820BootstrapExisting::verifyInputClosure);'
    new='beforeOwnership(()->{verifyInputClosure();expectedBeforeOwnership(2,"schubert_batch","PG4820-bootstrap-guard","schubert_nk",true,true);});'
    if java.count(old)!=1:raise ValueError('one current preownership boundary')
    java=java.replace(old,new)
    marker='  public static void main(String[] args)throws Exception{'
    if java.count(marker)!=1:raise ValueError('one current entry')
    java=java.replace(marker,'  static Pg4820OwnedDatabase.Expected expectedBeforeOwnership(int backend,String role,String application,String database,boolean readOnly,boolean advisory){return new Pg4820OwnedDatabase.Expected(backend,role,application,database,readOnly,advisory);}\n'+marker)
    built['Pg4820BootstrapExisting.java']=java
    built.pop('pg1703_parent_receipt.py',None)
    for name,text in built.items():
        if name.endswith('.py'):compile(text,'<current Bootstrap '+name+'>','exec')
    return built
