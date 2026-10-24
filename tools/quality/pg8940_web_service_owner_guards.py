"""Actual new ownership source/field guards and original retained-Valve counterexample, PT0."""
import ast
import datetime
import json
from pathlib import Path
import subprocess
import pg8934_web_service_metric_fixed_host as current
from host_tool_invocation import capture,verify

host=current.run.host
MAIN='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebServiceMetricBinding.java'

def main():
    invocation=capture(Path(__file__))
    out=host.BASE/'PG8940-web-service-owner-guards-v1'
    assert not out.exists()
    tool=host.ROOT/'tools/quality/pg8938_web_service_metric_fixed_trace.py'
    tree=ast.parse(tool.read_text())
    fn=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='protocol')
    namespace={};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(tool),'exec'),namespace)
    validate=namespace['protocol'];text=(host.ROOT/MAIN).read_text();validate(text)
    old=subprocess.check_output(['git','show','96575ba67dc4fabb335df8481e2cb2fbe7ef233b:'+MAIN],cwd=host.ROOT,text=True)
    rejected=[]
    for name,bad in [('original-retained-valve-getter',old),('retained-factory-result',text.replace('private final HttpMetricRecorder http;','private final HttpMetricValve http;',1)),('return-shared-valve',text.replace('return new HttpMetricValve(http, terminal);','return http;',1)),('drop-retained-recorder',text.replace('private final HttpMetricRecorder http;','private HttpMetricRecorder http;',1))]:
        assert bad!=text
        try: validate(bad)
        except AssertionError: rejected.append(name)
        else: raise AssertionError('every ownership regression rejects')
    unit=host.ROOT/MAIN.replace('/main/','/test/').replace('.java','Test.java')
    body=''.join(unit.read_text().split())
    assert 'assertNotSame(first,second);' in body and 'registry.get("nk_http_requests_total")' in body and '.counter().count());' in body
    assert 'first.log(firstRequest,response,1);' in body and 'second.log(secondRequest,response,1);' in body
    snapshot=current.COMPILE/'snapshot'
    assert host.sha(snapshot/MAIN)==host.sha(host.ROOT/MAIN)
    verify(invocation);out.mkdir()
    host.write(out/'manifest.json',dict(actualExit=0,source=current.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,bug='BUG-1724',ykt='YKT-1475',actualTraceValidatorSha256=host.sha(tool),actualMainSha256=host.sha(host.ROOT/MAIN),unitSha256=host.sha(unit),metadataCounterexamples=rejected,oracleRevision='INTERNAL_MUTABLE_PIPELINE_OWNERSHIP_CORRECTION; EXTERNAL_NAME_TAG_VALUES_CLAIM_UNCHANGED',productPtExecuted=0,coverage=None,formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,metadataCounterexamples=len(rejected),manifestSha256=host.sha(out/'manifest.json'))))

if __name__=='__main__':
    main()
