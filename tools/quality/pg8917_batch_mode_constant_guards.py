"""Actual host preflight assertions + original literal mutation; no target initialization or PT."""
import ast
import datetime
import json
from pathlib import Path
import pg8912_batch_full_text_static_fixed_host as current
from host_tool_invocation import capture,verify

host=current.run.host
MAIN='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricText.java'

def main():
    invocation=capture(Path(__file__))
    out=host.BASE/'PG8917-batch-mode-constant-guards-v1'
    assert not out.exists()
    tool=Path(current.__file__);tree=ast.parse(tool.read_text())
    nodes=[node for node in ast.walk(tree) if isinstance(node,ast.Assert) and any(isinstance(child,ast.Name) and child.id=='main' for child in ast.walk(node))]
    assert len(nodes)==3
    program=compile(ast.Module(body=nodes,type_ignores=[]),str(tool),'exec')
    source=(host.ROOT/MAIN).read_text();exec(program,{'main':source})
    current.fixture_contract((host.ROOT/MAIN.replace('/main/','/test/').replace('.java','Test.java')).read_text())
    rejected=[]
    for name,bad in [('original-if-literal',source.replace('if (STANDARD_MODE.equals(mode))','if ("STANDARD".equals(mode))',1)),('constant-missing',source.replace('  private static final String STANDARD_MODE = "STANDARD";','',1)),('constant-value-change',source.replace('STANDARD_MODE = "STANDARD"','STANDARD_MODE = "DEBUG"',1))]:
        assert bad!=source
        try: exec(program,{'main':bad})
        except AssertionError: rejected.append(name)
        else: raise AssertionError('every mode contract mutation must reject')
    others={}
    for role in ('api','web'):
        path=f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{role.title()}CustomMetricPayload.java'
        text=(host.ROOT/path).read_text()
        assert 'private static final String STANDARD_MODE = "STANDARD";' in text and 'if (STANDARD_MODE.equals(mode))' in text
        others[path]=dict(sha256=host.sha(host.ROOT/path),status='EXISTING_NAMED_CONSTANT_NO_CHANGE_NO_PT_REPLAY')
    verify(invocation);out.mkdir()
    host.write(out/'manifest.json',dict(actualExit=0,source=current.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,bug='BUG-1723',ykt='YKT-1474',hostGuardSha256=host.sha(tool),extractedActualAssertions=3,mainSourceSha256=host.sha(host.ROOT/MAIN),metadataCounterexamples=rejected,otherTargets=others,productPtExecuted=0,coverage=None,formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,actualAssertions=3,metadataCounterexamples=len(rejected),manifestSha256=host.sha(out/'manifest.json'))))

if __name__=='__main__':
    main()
