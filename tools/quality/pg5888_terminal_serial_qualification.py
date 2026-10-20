"""Read original3973 source/Jar/XML/actual coverage only; never PT or runtime execution."""
import inspect
import re
import subprocess
from pyflakes.api import check
import pg5862_terminal_qualification as previous
from pg5886_terminal_serial_whole import SOURCE,ROOT,W,SLOT as ORIGINAL,CHANGED_TESTS,NEW_METHODS
from pg5882_terminal_serial_static import MODIFIED,class_key
from pg5814_rollback_qualification import names

SLOT='pg5888-terminal-serial-qualified-v1'
PHYSICAL_KINDS={class_key(p):'DEDICATED_SESSION_SERIAL_TERMINAL_DECISION'for p in MODIFIED}


def physical_difference(old,new,candidate):
    if len(old)!=1666 or len(new)!=1666 or new!=candidate or set(old)!=set(new)or{k for k in old if old[k]!=new[k]}!=set(PHYSICAL_KINDS):raise ValueError('all1666 bytes; exact three modified/1663 unchanged, no added/removed')
    if any(re.fullmatch('[0-9a-f]{64}',v)is None for m in(old,new,candidate)for v in m.values()):raise ValueError('actual SHA256 only')
    return[{'oldClass':k,'class':k,'oldSha256':old[k],'newSha256':new[k],'action':'MODIFIED','physicalKind':PHYSICAL_KINDS[k]}for k in sorted(PHYSICAL_KINDS)],1663


def added_cases():
    cases=[];changed=set()
    for row in subprocess.check_output(['git','diff','--name-status',previous.SOURCE,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines():
        action,path=row.split('\t')
        if '/src/test/'not in path:continue
        key=path.split('/src/test/java/dev/codex/schubert/nk/')[1][:-5]
        if action!='M'or key not in CHANGED_TESTS:raise ValueError('only existing class two new methods and fixture supplement')
        before=names(subprocess.check_output(['git','show',previous.SOURCE+':'+path],cwd=ROOT,text=True));after=names(subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT,text=True))
        if not before<=after or after-before!=(NEW_METHODS if key.endswith('/CommittedTerminalAdmissionContractTest')else set()):raise ValueError('all old methods retained; exactly two declared Sync cases')
        cls=path.split('/src/test/java/')[1][:-5].replace('/','.');cases.extend((cls,n)for n in after-before);changed.add(key)
    if changed!=CHANGED_TESTS or len(cases)!=2 or len(set(cases))!=2:raise ValueError('exact new two identities')
    return sorted(cases)


def qualifier_source():
    raw=previous.qualifier_source()
    changes={"out = base / 'runs/PG5860-six-v1'":"out = base / 'runs/PG5886-six-v1'","source = base / 'source-full-PG5860'":"source = base / 'source-full-PG5886'","old = base / 'runs/PG5832-six-v1'":"old = base / 'runs/PG5860-six-v1'",'transfer/PG5860-source.tar':'transfer/PG5886-source.tar','len(oldcases) == 3967':'len(oldcases) == 3971','len(additions) == 4':'len(additions) == 2','len(cases) == 3971':'len(cases) == 3973',"'tests': 3971, 'suites': 592":"'tests': 3973, 'suites': 592",'all3967 original identities retained plus exact4 terminal admission contracts; five SS-derived oracle corrections and one fixture supplement declared':'all3971 original identities retained plus exact2 legal Sync concurrency contracts; no oracle change'}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one original3973 qualifier binding')
        raw=raw.replace(old,new,1)
    return raw


def emitted(data):
    raw=previous.emitted(data)
    # Replace complete known definitions, not partial globals or an old result.
    old=inspect.getsource(previous.physical_difference)
    if raw.count(old)!=1 or raw.count(previous.qualifier_source())!=1:raise ValueError('one emitted physical and XML reader definition')
    raw=raw.replace(old,inspect.getsource(physical_difference),1).replace(previous.qualifier_source(),qualifier_source(),1).replace('source-full-PG5860','source-full-PG5886')
    oldprefix='PHYSICAL_KINDS='+repr(previous.PHYSICAL_KINDS)
    if raw.count(oldprefix)!=1:raise ValueError('one declared physical map')
    raw=raw.replace(oldprefix,'PHYSICAL_KINDS='+repr(PHYSICAL_KINDS),1)
    if check(raw,'<original3973 independent reader>'):raise ValueError('complete generated namespace')
    compile(raw,'<original3973 reader>','exec');return raw


def operator_source():
    raw=previous.operator_source()
    changes={'PG5860-six-v1':'PG5886-six-v1',"['tests']==3971":"['tests']==3973",'PG5832-current3967-cases':'PG5860-current3971-cases','fcceece52ccd16cf81f0b0e67060464ce0414a723417d2f827b8e29a9bcd9023':'a937e6dc41450d13b2874299d28f19caafc5b0b070fffdd4c96669bc410c3d02','PG5858-terminal-static-v1':'PG5882-terminal-serial-static-v1','pg5858-terminal-static-v1':'pg5882-terminal-serial-static-v1','PG5862-qualified-v1':'PG5888-qualified-v1'}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one original3973 operator binding')
        raw=raw.replace(old,new,1)
    compile(raw,'<original3973 operator>','exec');return raw


def main():
    scope={**vars(previous.previous),'SOURCE':SOURCE,'ROOT':ROOT,'W':W,'ORIGINAL':ORIGINAL,'SLOT':SLOT,'PHYSICAL_KINDS':PHYSICAL_KINDS,'physical_difference':physical_difference,'added_cases':added_cases,'emitted':emitted}
    exec(compile(operator_source(),'<original3973 operator>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
