"""Root13 Backup existing archives/read-only whole scope; no Backup replay."""
import ast
import inspect
import pg1619_current_ordinary_backup_qualification as engine
import pg1621_current_ordinary_backup_qualification_v2 as fixture
from pg1776_warning_stop_independent_post import payload as previous_post
from pg1833_readonly_parent_state_sources import SOURCE,TOOLS

SLOT='pg1847-warning-backup-readonly-v1'


def whole_post(seals):
    raw=previous_post(seals).replace('pg1772','pg1833').replace('Pg1772','Pg1833').replace('PG1772','PG1833')
    matches=[n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)and type(n.value)is bytes and n.value.startswith(b'genuineParentDone=true\n')]
    if len(matches)!=1:raise ValueError('one exact current WARNING stop seal required')
    node=matches[0];new=node.value.replace(b'genuineParentDone=true\n',b'genuineParentWarningOriginal=true\nmanagerFailureRetained=true\n',1)
    literal=ast.get_source_segment(raw,node)
    if raw.count(literal)!=1:raise ValueError('one completion literal required')
    return raw.replace(literal,repr(new),1)


def payload():
    raw=inspect.getsource(engine.payload)
    replacements=[('pg1613-current-ordinary-terminal-post-v1.safe.json','pg1838-warning-terminal-independent-post-v1/manifest.safe.json'),('pg1609_parent_receipt.py','pg1833_parent_receipt.py'),('0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','4148e3e8-f107-431a-ab27-d6e6d1f1772e'),('2026-10-12T06:23:13.176261Z','2026-10-12T18:20:32.598894Z')]
    for old,new in replacements:
        if old not in raw:raise ValueError('one explicit Root13 Backup input role required')
        raw=raw.replace(old,new)
    ns={**engine.__dict__,'whole_post':whole_post,'SOURCE':SOURCE,'TOOLS':TOOLS,'SAVE':engine.SAVE.replace('pg1619-current-ordinary-backup-qualified-v1',SLOT)}
    exec(compile(raw,'<Root13 Backup independent reader generator>','exec'),ns)
    base=ns['payload']()
    wrapper=inspect.getsource(fixture.payload).replace('raw=prior.payload()','raw=BASE_PAYLOAD').replace('0.1.0-PG1544','0.1.0-PG1638')
    wrapper=wrapper.replace("raw=raw.replace('pg1619-current-ordinary-backup-qualified-v1','pg1621-current-ordinary-backup-qualified-v2')",'')
    env={**fixture.__dict__,'BASE_PAYLOAD':base};exec(compile(wrapper,'<approved fixture config reader>','exec'),env)
    raw=env['payload']();compile(raw,'<actual Root13 Backup byte readback>','exec');return raw


def main():
    ns={**engine.__dict__,'payload':payload,'SLOT':SLOT}
    exec(compile(inspect.getsource(engine.main),'<readonly whole/Backup transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
