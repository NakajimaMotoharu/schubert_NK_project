"""BUG2194 finite static/profile evidence check; no Product or old successful tool reexecution."""
import ast
import difflib
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17073-partial-source-profile-finite-audit-v1'
PROFILES=[
('pg17030_current2535_previous_broker_journal_registry_post.py','ae437bf33659f9615b70c15f70b7b4dd984698b1d0a200896e330ba6285c4a0a',('PG17028-current2535-previous-broker-journal-registry-v1','3d54a9744a796cb753a308bd56cb77e5ce4adbb8451d7ff5cba250cecc162725'),('PG17012-current2531-inspector-static-environment-registry-v1','c9545527a3a6663fd7488e7da0241e3e74c23474ae88a7b38e6a84ddc5138c51'),True),
('pg17046_current2539_inspector_run_environment_registry_post.py','c5ad5b88bfc3c978d47295e5f149aac7594152e3d22763858a3e55633d314695',('PG17044-current2539-inspector-run-environment-registry-v1','294c86adb70497b9b38a630721c587e8ac015f0c3c31f49de000c729ca1740fe'),('PG17028-current2535-previous-broker-journal-registry-v1','3d54a9744a796cb753a308bd56cb77e5ce4adbb8451d7ff5cba250cecc162725'),True),
('pg17062_current2547_no_prior_broker_registry_post.py','7d9756eca2ea462085a93c2ebf93fa9beb528595c822508f1dd4b348933f0737',('PG17060-current2547-no-prior-broker-registry-v1','ef523fa81539f44dd15dcf0ac3df1f50acce34183615ad21ed9514e15f534a87'),('PG17044-current2539-inspector-run-environment-registry-v1','294c86adb70497b9b38a630721c587e8ac015f0c3c31f49de000c729ca1740fe'),True),
('pg17078_current2564_morning_gate_evidence_registry_post.py','889485e62a0c2d16969df086268674c738a665dec29f25abdfaa40b3d3fbaf55',('PG17076-current2564-morning-gate-evidence-registry-v1','b2d956a16015cad96c7ee106ace35071b4ca5d37b54c72a08777f0896adda540'),('PG17060-current2547-no-prior-broker-registry-v1','ef523fa81539f44dd15dcf0ac3df1f50acce34183615ad21ed9514e15f534a87'),False),
('pg17079_current2564_morning_gate_evidence_registry_post_v2.py','a9cdc891dc313663b7e76fb184e4936c28c807c5c7a976265c384881be29faec',('PG17076-current2564-morning-gate-evidence-registry-v1','b2d956a16015cad96c7ee106ace35071b4ca5d37b54c72a08777f0896adda540'),('PG17060-current2547-no-prior-broker-registry-v1','ef523fa81539f44dd15dcf0ac3df1f50acce34183615ad21ed9514e15f534a87'),True)]
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def value(node):
    if isinstance(node,ast.Constant) and isinstance(node.value,str):return node.value
    if isinstance(node,ast.Name) and node.id=='root':return 'dev/codex/schubert/nk/batch/platform/'
    if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Add):return value(node.left)+value(node.right)
    raise ValueError('closed static literal expression required')
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=[]
    for name,pin,current,previous,should_match in PROFILES:
        blob=(data.ROOT/'tools/quality'/name).read_bytes();assert data.sha(blob)==pin
        tree=ast.parse(blob);main_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        assignment=next(n for n in main_node.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='expected_new' for t in n.targets))
        assert isinstance(assignment.value,ast.Set);declared={value(v) for v in assignment.value.elts}
        checks=[n for n in ast.walk(tree) if isinstance(n,ast.Compare) and isinstance(n.left,ast.Call) and isinstance(n.left.func,ast.Name) and n.left.func.id=='len' and len(n.left.args)==1 and isinstance(n.left.args[0],ast.Name) and n.left.args[0].id=='partial_names']
        assert len(checks)==1 and len(checks[0].comparators)==1 and isinstance(checks[0].ops[0],ast.Eq)
        expected=ast.literal_eval(checks[0].comparators[0]);assert type(expected) is int
        now,old=read(current),read(previous)
        assert now['actualExit']==old['actualExit']==0 and now['source']==old['source']==SOURCE
        fresh=set(now['fullSourceUnits'])-old['fullSourceUnits'].keys();assert fresh==declared
        actual=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for n,u in now['fullSourceUnits'].items() if n in fresh)
        assert (expected==actual) is should_match
        verify(now['invocation']);verify(old['invocation'])
        rows.append(dict(tool=name,sha256=pin,newSources=sorted(fresh),expectedPartial=expected,actualPartial=actual,classification='NON_APPLICABLE_MATCH' if should_match else 'OLD_FAILED_RETAINED_NOT_ACCEPTED'))
    original=(data.ROOT/'tools/quality'/PROFILES[3][0]).read_text();fixed=(data.ROOT/'tools/quality'/PROFILES[4][0]).read_text()
    changed=[line for line in difflib.ndiff(original.splitlines(),fixed.splitlines()) if line[:2] in ['- ','+ ']]
    assert len(changed)==4 and fixed==original.replace('PG17078-current2564-morning-gate-evidence-registry-post-v1','PG17079-current2564-morning-gate-evidence-registry-post-v2').replace('len(partial_names)==1','len(partial_names)==2')
    assert not (data.BASE/'PG17078-current2564-morning-gate-evidence-registry-post-v1').exists()
    post=read(('PG17079-current2564-morning-gate-evidence-registry-post-v2','69003c60592808a842b21cebd12d3bce3fcee3de2ee86f195a839d18ce7b0eec'))
    assert post['actualExit']==0 and post['metadataNegativeVectors']==34 and post['newSourcePrograms']==2 and post['newUniqueMethods']==17
    checks=[(0,0,True),(1,1,True),(2,2,True),(1,2,False),(2,1,False),(0,2,False),(2,0,False)]
    assert all((expected==actual) is outcome for expected,actual,outcome in checks)
    verify(post['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bug='BUG-2194',crossDeployment='YKT-1941',profiles=rows,newPostSha256='69003c60592808a842b21cebd12d3bce3fcee3de2ee86f195a839d18ce7b0eec',oldExecutedToolBytesPreserved=True,exactChangedLines=changed,staticArityNegativeAndBoundaryVectors=len(checks),productTestsExecuted=0,newAccepted=0,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
