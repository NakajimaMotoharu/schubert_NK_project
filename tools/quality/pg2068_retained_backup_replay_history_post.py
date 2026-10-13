"""New read-only current Backup slot, exact retained handle plus later skip oracle."""
import ast
import types
from pyflakes.api import check
import pg2064_current_retained_backup_content as previous
import pg2060_fresh_runtime_retirement_independent_post as transport
from pg2066_retained_backup_handle_oracle import source

SLOT='pg2068-retained-backup-replay-history-post-v1'


def payload(seals):
    raw=previous.payload(seals).replace(previous.SLOT,SLOT)
    nodes=[n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ORACLE_SOURCE'for t in n.targets)]
    if len(nodes)!=1:raise ValueError('one retained manifest oracle role required')
    raw=raw.replace(ast.get_source_segment(raw,nodes[0]),'ORACLE_SOURCE='+repr(source()),1)
    if check('HASHES={}\nRECEIPT="fixed"\n'+raw,'<complete retained Backup skip post>'):raise ValueError('all actual oracle globals required')
    compile(raw,'<retained Backup skip post>','exec');return raw


def entry():
    return types.FunctionType(transport.main.__code__,{**transport.__dict__,'payload':payload,'SLOT':SLOT},'current_retained_backup_entry')


def main():return entry()()


if __name__=='__main__':raise SystemExit(main())
