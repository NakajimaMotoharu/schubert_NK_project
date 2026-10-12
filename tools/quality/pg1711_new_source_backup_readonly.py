"""SameSource completed ordinary Backup bytes/SQL/config/list, never re-Backup."""
import inspect
import pg1619_current_ordinary_backup_qualification as engine
import pg1621_current_ordinary_backup_qualification_v2 as fixture
from pg1707_new_source_stop_independent_post import payload as whole_post
from pg1703_new_source_owned_stop_sources import SOURCE,TOOLS

SLOT='pg1711-new-source-backup-readonly-v1'


def payload():
    raw=inspect.getsource(engine.payload)
    for old,new in [
        ('pg1613-current-ordinary-terminal-post-v1.safe.json','pg1707-new-source-terminal-post-v1.safe.json'),
        ('pg1609_parent_receipt.py','pg1703_parent_receipt.py'),
        ('0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','02e941b9-1c52-4018-a193-63dd00b269af'),
        ('2026-10-12T06:23:13.176261Z','2026-10-12T14:19:28.968927Z')]:
        if old not in raw:raise ValueError('new Source Backup actual input join required')
        raw=raw.replace(old,new)
    ns={**engine.__dict__,'whole_post':whole_post,'SOURCE':SOURCE,'TOOLS':TOOLS,
        'SAVE':engine.SAVE.replace('pg1619-current-ordinary-backup-qualified-v1',SLOT)}
    exec(compile(raw,'<new Source completed backup readonly generator>','exec'),ns)
    base=ns['payload']()
    # Reuse the independent approved api-fixture responsibility, not old results.
    wrapper=inspect.getsource(fixture.payload)
    wrapper=wrapper.replace('raw=prior.payload()','raw=BASE_PAYLOAD')
    wrapper=wrapper.replace('0.1.0-PG1544','0.1.0-PG1638')
    wrapper=wrapper.replace("raw=raw.replace('pg1619-current-ordinary-backup-qualified-v1','pg1621-current-ordinary-backup-qualified-v2')",'')
    env={**fixture.__dict__,'BASE_PAYLOAD':base}
    exec(compile(wrapper,'<approved independent fixture config generator>','exec'),env)
    result=env['payload']()
    compile(result,'<actual current sameSource Backup verification>','exec')
    return result


def main():
    raw=inspect.getsource(engine.main)
    ns={**engine.__dict__,'payload':payload,'SLOT':SLOT}
    exec(compile(raw,'<sameSource readonly Backup transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
