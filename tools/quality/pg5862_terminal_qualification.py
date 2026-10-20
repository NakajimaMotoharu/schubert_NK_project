"""Independent original3971 source/Jar/XML/coverage reader; never starts PT or runtime."""
import ast
import inspect
import re
import subprocess
from pyflakes.api import check
import pg5834_isolation_qualification as previous
from pg5860_terminal_whole import SOURCE,ROOT,W,SLOT as ORIGINAL,NEW_TESTS,CHANGED_TESTS
from pg5858_terminal_static import MODIFIED,class_key
from pg5848_protocol_expression_static import MODIFIED as PROTOCOL
from pg5756_private_contract_qualification import target_counters

SLOT='pg5862-terminal-qualified-v1'
PHYSICAL_KINDS={class_key(p):'COMMITTED_TERMINAL_ADMISSION_HALT'for p in MODIFIED}
PHYSICAL_KINDS.update({class_key(p):'PROTOCOL_EXPRESSION_ONLY'for p in PROTOCOL})
PHYSICAL_KINDS.update({'protocol:dev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog'+s+'.class':'PROTOCOL_OWNER_DEBUG_ONLY'for s in('$1','$MutableFields')})


def physical_difference(old,new,candidate):
    if len(old)!=1666 or len(new)!=1666 or new!=candidate or set(old)!=set(new)or{k for k in old if old[k]!=new[k]}!=set(PHYSICAL_KINDS):raise ValueError('all1666 actual bytes; exact12 modified,1654 unchanged; no added/removed')
    if any(re.fullmatch('[0-9a-f]{64}',v)is None for m in(old,new,candidate)for v in m.values()):raise ValueError('actual SHA256 only')
    return[{'oldClass':k,'class':k,'oldSha256':old[k],'newSha256':new[k],'action':'MODIFIED','physicalKind':PHYSICAL_KINDS[k]}for k in sorted(PHYSICAL_KINDS)],1654


def added_cases():
    cases=[];newfiles=set();changed=set()
    for row in subprocess.check_output(['git','diff','--name-status',previous.SOURCE,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines():
        action,path=row.split('\t')
        if '/src/test/'not in path:continue
        if not path.endswith('.java')or'/src/test/java/dev/codex/schubert/nk/'not in path:raise ValueError('test resources unchanged')
        key=path.split('/src/test/java/dev/codex/schubert/nk/')[1][:-5];raw=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT,text=True);names=previous.previous.names(raw);cls=path.split('/src/test/java/')[1][:-5].replace('/','.')
        if action=='A'and key in NEW_TESTS:newfiles.add(key);cases.extend((cls,n)for n in names)
        elif action=='M'and key in CHANGED_TESTS:
            before=subprocess.check_output(['git','show',previous.SOURCE+':'+path],cwd=ROOT,text=True)
            if previous.previous.names(before)!=names:raise ValueError('original Test identities retained')
            changed.add(key)
        else:raise ValueError('only declared new four and six Test/fixture supplements')
    if newfiles!=NEW_TESTS or changed!=CHANGED_TESTS or len(cases)!=4 or len(set(cases))!=4:raise ValueError('exact four independent Test identities')
    return sorted(cases)


def qualifier_source():
    raw=previous.qualifier_source()
    replacements={"out = base / 'runs/PG5832-six-v1'":"out = base / 'runs/PG5860-six-v1'","source = base / 'source-full-PG5832'":"source = base / 'source-full-PG5860'","old = base / 'runs/PG5808-six-v1'":"old = base / 'runs/PG5832-six-v1'",'transfer/PG5832-source.tar':'transfer/PG5860-source.tar','len(oldcases) == 3955':'len(oldcases) == 3967','len(additions) == 12':'len(additions) == 4','len(cases) == 3967':'len(cases) == 3971',"== 590)":"== 592)","'tests': 3967, 'suites': 590":"'tests': 3971, 'suites': 592",'all3955 original identities retained plus exact12 independent isolation contracts; four cause supplements and one finite helper explicitly declared':'all3967 original identities retained plus exact4 terminal admission contracts; five SS-derived oracle corrections and one fixture supplement declared'}
    for old,new in replacements.items():
        if raw.count(old)!=1:raise ValueError('one original/prior artifact binding: '+old)
        raw=raw.replace(old,new,1)
    return raw


def emitted(data):
    counters=inspect.getsource(target_counters).replace('source-full-PG5754','source-full-PG5860')
    raw='import re\nPHYSICAL_KINDS='+repr(PHYSICAL_KINDS)+'\n'+inspect.getsource(physical_difference)+'\n'+qualifier_source()+'\n'+counters+'\ndata='+repr(data)+'\nvalue=qualify(data)\nvalue["changedTargetCounters"]=target_counters(data)\nvalue["coreReceiverTargetFour100"]=all(c[k]["missed"]==0 and(c[k]["covered"]>0 or k=="BRANCH")for c in value["changedTargetCounters"].values()for k in("LINE","METHOD","CLASS","BRANCH"))\nvalue["targetScopeNote"]="Eight actual receiver targets, not global coverage; missing branches remain missing."\nprint(__import__("json").dumps(value))\n'
    if check(raw,'<original3971 independent reader>'):raise ValueError('complete emitted namespace')
    for n in ast.walk(ast.parse(raw)):
        if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and(n.func.attr in('write_text','write_bytes','unlink','mkdir')or isinstance(n.func.value,ast.Name)and n.func.value.id in('subprocess','socket','dbus')):raise ValueError('artifact reader only, no PT/runtime/write')
    return raw


def main():
    raw=inspect.getsource(previous.main)
    replacements={'PG5832-six-v1':'PG5860-six-v1',"['tests']==3967":"['tests']==3971",'PG5808-current3955-cases':'PG5832-current3967-cases','42bdfb97cdc1f3b1944e28e144e91993ed2f05bc269a289ba6f20e6d7f29a376':'fcceece52ccd16cf81f0b0e67060464ce0414a723417d2f827b8e29a9bcd9023','PG5830-isolation-static-v1':'PG5858-terminal-static-v1','pg5830-isolation-static-v1':'pg5858-terminal-static-v1','PG5834-qualified-v1':'PG5862-qualified-v1'}
    for old,new in replacements.items():
        if raw.count(old)!=1:raise ValueError('one independent3971 operator binding: '+old)
        raw=raw.replace(old,new,1)
    scope={**vars(previous),'SOURCE':SOURCE,'ROOT':ROOT,'W':W,'ORIGINAL':ORIGINAL,'SLOT':SLOT,'PHYSICAL_KINDS':PHYSICAL_KINDS,'physical_difference':physical_difference,'added_cases':added_cases,'emitted':emitted}
    exec(compile(raw,'<original3971 qualification operator>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
