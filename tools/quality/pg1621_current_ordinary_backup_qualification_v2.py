"""New-slot independent current Backup with existing approved fixture override."""
import inspect
import pg1619_current_ordinary_backup_qualification as prior
import pg1620_current_backup_config_fixture_oracle as fixture

def payload():
    raw=prior.payload()
    old="config_oracle.verify_member(m.name,body,source.read_bytes(),(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode)),(m.uid,m.gid,m.mode),expected_gid,signed_hashes)"
    new="""if m.name=='api.yml':
    fixture_api.verify_fixture_api(body,source.read_bytes(),pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1544/config/templates/api.yml').read_bytes(),(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode)),(m.uid,m.gid,m.mode),expected_gid,signed_hashes)
   else:
    config_oracle.verify_member(m.name,body,source.read_bytes(),(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode)),(m.uid,m.gid,m.mode),expected_gid,signed_hashes)"""
    if raw.count(old)!=1:raise ValueError('current fixed api fixture comparison boundary refused')
    # The reused reader is nested in qualify_backup, hence one extra indentation.
    raw=raw.replace(old,new.replace('\n','\n '))
    raw=raw.replace("config_oracle=types.ModuleType('explicit_config_responsibility');exec(CONFIG_SOURCE,config_oracle.__dict__)","config_oracle=types.ModuleType('explicit_config_responsibility');exec(CONFIG_SOURCE,config_oracle.__dict__)\n fixture_api=types.ModuleType('approved_fixture_api');exec(FIXTURE_SOURCE,fixture_api.__dict__)")
    raw='FIXTURE_SOURCE='+repr(inspect.getsource(fixture))+'\n'+raw
    raw=raw.replace('pg1619-current-ordinary-backup-qualified-v1','pg1621-current-ordinary-backup-qualified-v2')
    compile(raw,'<current Backup approved fixture oracle>','exec');return raw

def main():
    raw=inspect.getsource(prior.main).replace('out=W/SLOT','out=W/\'pg1621-current-ordinary-backup-qualified-v2\'')
    ns={**prior.__dict__,'payload':payload};exec(compile(raw,'<new current Backup qualification transport>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
