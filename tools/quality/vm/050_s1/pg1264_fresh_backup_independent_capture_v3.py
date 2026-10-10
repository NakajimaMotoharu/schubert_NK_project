"""New-only qualified release-template vs deployed-host responsibilities."""
import ast
import inspect
import pg1257_fresh_independent_terminal_post as transport
from pg1262_fresh_backup_independent_capture_v2 import payload as previous,SEALS
import pg1263_backup_config_responsibility_v2 as contract

def payload(seals):
    s=previous(seals).replace('pg1262-fresh-backup-independent-v2','pg1264-fresh-backup-independent-v3').replace('PG1262-fresh-backup-independent-v2','PG1264-fresh-backup-independent-v3')
    node=next(n for n in ast.parse(s).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CONFIG_SOURCE'for t in n.targets))
    old=ast.get_source_segment(s,node.value);s=s.replace(old,repr(inspect.getsource(contract)),1)
    s=s.replace("'staticConfigAllowlistEntriesVerified':8","'staticConfigAllowlistEntriesVerified':8,'signedEffectiveProfileCount':1,'registeredReleaseTemplateCount':4,'deployedHostConfigNotClaimedAsTemplateByteSignature':True,'externalHostEnvCount':3")
    compile(s,'<actual separated release and host config Backup oracle>','exec');return s

def main():
    entry=inspect.getsource(transport.main).replace('pg1257-fresh-terminal-post-v1','pg1264-fresh-backup-independent-v3')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only bounded Backup v3 actual>', 'exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
