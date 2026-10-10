"""New-only explicit signed-template/effective vs fixed host-env Backup capture."""
import inspect
import pg1257_fresh_independent_terminal_post as transport
from pg1260_fresh_backup_independent_capture import payload as previous,SEALS
import pg1261_backup_config_source_contract as config_contract

def payload(seals):
    s=previous(seals).replace('pg1260-fresh-backup-independent-v1','pg1262-fresh-backup-independent-v2').replace('PG1260-fresh-backup-independent-v1','PG1262-fresh-backup-independent-v2')
    marker='backup_identity=pwd.getpwnam(\'schubert-backup\')'
    if s.count(marker)!=1:raise ValueError('fixed independent config source module insertion required')
    s='CONFIG_SOURCE='+repr(inspect.getsource(config_contract))+'\n'+s
    s=s.replace(marker,"import grp\nconfig_oracle=types.ModuleType('explicit_config_responsibility');exec(CONFIG_SOURCE,config_oracle.__dict__)\n"+marker)
    old="require(len(body)==m.size and body==source.read_bytes()and hashlib.sha256(body).hexdigest()==signed_hashes['config/effective/'+m.name]and metadata9(source.lstat())==metadata9(st))"
    if s.count(old)!=1:raise ValueError('fixed erroneous blanket config source boundary required')
    new="require(len(body)==m.size and st.st_nlink==1 and not os.listxattr(source))\n   expected_gid=pwd.getpwnam('schubert-api').pw_gid if m.name=='api.env'else pwd.getpwnam('schubert-web').pw_gid if m.name=='web.env'else grp.getgrnam('schubert').gr_gid\n   config_oracle.verify_member(m.name,body,source.read_bytes(),(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode)),(m.uid,m.gid,m.mode),expected_gid,signed_hashes)\n   require(metadata9(source.lstat())==metadata9(st))"
    s=s.replace(old,new)
    compile(s,'<complete explicit config responsibility Backup capture>','exec');return s

def main():
    entry=inspect.getsource(transport.main).replace('pg1257-fresh-terminal-post-v1','pg1262-fresh-backup-independent-v2')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only corrected independent Backup>', 'exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
