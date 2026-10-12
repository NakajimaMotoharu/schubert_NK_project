"""BUG1178: fixed read-only parent_state, never expand stop ORDER/show scope."""
import ast
from pg1821_warning_parent_configuration_sources import sources as previous_sources
import pg1821_warning_parent_configuration_sources as previous
from pg1808_warning_identity_bound_sources import UUID

TOOLS='pg1833-warning-owned-stop-tools-v1'
SOURCE=previous.SOURCE
context=previous.context


def sources():
    result={}
    for name,raw in previous_sources().items():
        bound=raw.replace('pg1821','pg1833').replace('Pg1821','Pg1833').replace('PG1821','PG1833')
        if UUID.findall(raw)!=UUID.findall(bound):raise ValueError('all UUID identities required')
        name=name.replace('1821','1833')
        if name=='pg1833_native_owned_stop.py':
            node=next(n for n in ast.parse(bound).body if isinstance(n,ast.FunctionDef)and n.name=='parent_receipt')
            body=ast.get_source_segment(bound,node)
            if body.count("show('schubert-nk-morning-controller.service')")!=2:raise ValueError('two exact readonly parent reads required')
            body=body.replace("show('schubert-nk-morning-controller.service')",'parent_state()')
            helper="""def parent_state():
 raw=command(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property='+','.join(sorted(FIELDS))]).decode('ascii')
 require(raw.endswith('\\n'))
 items=[]
 for line in raw.splitlines():
  key,sep,value=line.partition('=');require(sep=='='and key in FIELDS);items.append((key,value))
 fields=unique(items);require(set(fields)==FIELDS)
 return fields
"""
            bound=bound.replace(ast.get_source_segment(bound,node),helper+body,1)
        if name.endswith('.py'):
            from pyflakes.api import check
            if check(bound,'<fixed readonly parent state helper>'):raise ValueError('actual emitted closure required')
            compile(bound,'<fixed parent state18/read config2>','exec')
        result[name]=bound
    return result
