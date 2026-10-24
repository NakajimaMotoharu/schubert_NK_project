"""Replay only exact pure AST descriptor assertions from the qualified trace, never product PT."""
import ast
import copy
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import pg8696_api_standard_source_lock_trace as trace
from host_tool_invocation import capture,verify

if __name__=='__main__':
    invocation=capture(Path(__file__))
    host=trace.host
    out=host.BASE/'PG8697-standard-owner-pom-guard-metadata-v1'
    assert not out.exists()
    manifest=host.BASE/'PG8696-api-standard-source-lock-trace-v1/manifest.json'
    assert host.sha(manifest)=='aa45bd6f57291f35a1ca7f9c96c94d898f956f07b8a09acd9e5fb870cdbcbd27'
    original=json.loads(manifest.read_text())
    verify(original['invocation'])
    tool=host.ROOT/'tools/quality/pg8696_api_standard_source_lock_trace.py'
    tree=ast.parse(tool.read_text())
    body=next(node.body for node in tree.body if isinstance(node,ast.If) and '__name__' in ast.unparse(node.test))
    first=next(i for i,node in enumerate(body) if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='dependencies' for target in node.targets))
    last=next(i for i,node in enumerate(body) if isinstance(node,ast.Assign) and any(isinstance(target,ast.Tuple) and any(isinstance(name,ast.Name) and name.id=='previous' for name in target.elts) for target in node.targets))
    selected=body[first:last]
    assert len(selected)==5 and all(isinstance(node,(ast.Assign,ast.Assert,ast.Expr)) for node in selected)
    # These exact statements only inspect/remove XML nodes in private in-memory copies.
    code=compile(ast.Module(body=selected,type_ignores=[]),str(tool),'exec')
    old=trace.normalized_xml(subprocess.check_output(['git','show',trace.BEFORE+':'+trace.POM],cwd=host.ROOT))
    new=trace.normalized_xml((trace.COMPILE/'snapshot'/trace.POM).read_bytes())
    ns={'m':'http://maven.apache.org/POM/4.0.0'}
    def check(value):
        exec(code,dict(ET=ET,ns=ns,new_pom=copy.deepcopy(value),old_pom=copy.deepcopy(old)))
    check(new)
    rejected=[]
    for label in ('wrong-version','duplicate-added-dependency','unrelated-dependency-change'):
        candidate=copy.deepcopy(new)
        deps=candidate.find('m:dependencies',ns)
        added=next(node for node in deps if node.findtext('m:artifactId',namespaces=ns)=='micrometer-registry-prometheus')
        if label=='wrong-version':added.find('m:version',ns).text='1.17.2'
        elif label=='duplicate-added-dependency':deps.append(copy.deepcopy(added))
        else:next(node for node in deps if node is not added).find('m:version',ns).text='999'
        try:check(candidate)
        except AssertionError:rejected.append(label)
        else:raise AssertionError('descriptor mutation must reject')
    guards=[node for node in body if isinstance(node,ast.Assert) and isinstance(node.test,ast.Compare) and isinstance(node.test.left,ast.SetComp) and any(isinstance(comp,ast.Set) and any(isinstance(name,ast.Name) and name.id=='POM' for name in comp.elts) for comp in node.test.comparators)]
    assert len(guards)==1
    path_code=compile(ast.Module(body=guards,type_ignores=[]),str(tool),'exec')
    other='src/schubert-nk-web/pom.xml'
    before={trace.POM:'old',other:'old'}
    after={trace.POM:'new',other:'new'}
    try:exec(path_code,dict(POM=trace.POM,before=before,after=after))
    except AssertionError:rejected.append('foreign-pom-change')
    else:raise AssertionError('foreign POM mutation must reject')
    verify(invocation)
    out.mkdir()
    host.write(out/'manifest.json',dict(actualExit=0,source=trace.SOURCE,invocation=invocation,qualifiedTraceSha256=host.sha(manifest),actualGuardToolSha256=host.sha(tool),descriptorGuardAst=ast.dump(ast.Module(body=selected,type_ignores=[])),pathGuardAst=ast.dump(guards[0]),positiveMetadataCases=1,rejectedMetadataCases=rejected,productionTestsExecuted=0,productionFilesChanged=0,formalUpdated=False,newAccepted=0,coverageQualified=False,actualVmActions=0,actualNetworkActions=0))
    print(json.dumps(dict(actualExit=0,metadataRejected=rejected,manifestSha256=host.sha(out/'manifest.json'))))
