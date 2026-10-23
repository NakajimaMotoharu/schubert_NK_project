"""Bounded AST-only project imports and negative guards, not Product PT or target initialization."""
import ast
import json
from pathlib import Path
import pg6966_chr_adapter_host as host
import pg7862_api_query_duration_six_compile_v3 as compilation
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG7866-api-query-import-contract-v1'
NAMES=('pg7850_api_query_duration_six_post_v2.py','pg7852_api_query_duration_trace_v3.py',
 'pg7854_api_query_duration_review_v3.py','pg7858_api_query_duration_host_v3.py',
 'pg7862_api_query_duration_six_compile_v3.py','pg7864_api_query_duration_post_v4.py')
def check(code,known):
    modules=[]
    for node in ast.walk(ast.parse(code)):
        if isinstance(node,ast.Import):modules.extend(item.name for item in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module:modules.append(node.module)
    project=sorted(set(m for m in modules if m.startswith('pg') or m in known))
    if any(m not in known for m in project):raise ValueError('missing project module')
    return project
def main():
    invocation=capture(Path(__file__))
    if OUT.exists():raise ValueError('new-only contract')
    root=host.ROOT/'tools/quality';known={p.stem for p in root.glob('*.py')};rows=[]
    for name in NAMES:
        p=root/name;modules=check(p.read_bytes(),known)
        rows.append(dict(path=str(p.relative_to(host.ROOT)),sha256=host.sha(p),projectImports=modules,missing=[]))
    negative=[]
    for code in ('import pg7844_api_query_duration_host','from pg7844_api_query_duration_host import SLOT'):
        try:check(code,known)
        except ValueError:negative.append(dict(code=code,rejected=True))
        else:raise ValueError('missing module mutation accepted')
    old=root/'pg7846_api_query_duration_post_v2.py'
    try:check(old.read_bytes(),known)
    except ValueError:historical_rejected=True
    else:raise ValueError('original defect not reproduced by AST guard')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,rows=rows,negativeGuards=negative,
      historicalDefect=dict(path=str(old.relative_to(host.ROOT)),sha256=host.sha(old),missingRejected=historical_rejected,executed=False),
      bugs=['BUG-1677'],horizontal=['YKT-1428'],productTestsExecuted=0,metadataChecks=9,targetInitialization=False,
      actualVmActions=0,actualDatabaseActions=0,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,files=6,negativeGuards=2,originalDefectRejected=True,manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
