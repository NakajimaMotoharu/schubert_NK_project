"""BUG1177: actual state18 plus separate configuration2, no fabricated field."""
import ast
from pg1808_warning_identity_bound_sources import sources as previous_sources,UUID
import pg1808_warning_identity_bound_sources as previous

TOOLS='pg1821-warning-owned-stop-tools-v1'
SOURCE=previous.SOURCE
context=previous.context


def sources():
    result={}
    for name,raw in previous_sources().items():
        bound=raw.replace('pg1808','pg1821').replace('Pg1808','Pg1821').replace('PG1808','PG1821')
        if UUID.findall(bound)!=UUID.findall(raw):raise ValueError('all UUIDs unchanged required')
        name=name.replace('1808','1821')
        if name=='pg1821_native_owned_stop.py':
            marker=" fields=show('schubert-nk-morning-controller.service')\n qualify_warning_parent(fields,True)"
            if bound.count(marker)!=1:raise ValueError('one exact actual parent configuration boundary required')
            bound=bound.replace(marker,""" fields=show('schubert-nk-morning-controller.service')
 config=parent_configuration()
 require(config['Type']==fields['Type'])
 qualify_warning_parent({**fields,**config},True)
 require(show('schubert-nk-morning-controller.service')==fields and parent_configuration()==config)""")
            tree=ast.parse(bound);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='parent_receipt')
            helper="""def parent_configuration():
 raw=command(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=Type,SuccessExitStatus']).decode('ascii')
 require(raw.endswith('\\n'))
 items=[]
 for line in raw.splitlines():
  key,sep,value=line.partition('=');require(sep=='='and key in {'Type','SuccessExitStatus'});items.append((key,value))
 fields=unique(items);require(set(fields)=={'Type','SuccessExitStatus'})
 return fields
"""
            bound=bound.replace(ast.get_source_segment(bound,node),helper+ast.get_source_segment(bound,node),1)
        if name.endswith('.py'):
            from pyflakes.api import check
            if check(bound,'<actual state18-config2 stop helper>'):raise ValueError('closed actual emitted globals required')
            compile(bound,'<actual state18 and config2>','exec')
        result[name]=bound
    return result
