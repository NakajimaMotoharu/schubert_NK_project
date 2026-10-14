"""Actual persisted cutoff contradiction and foreign run refusal; frozen current Main/native."""
import pg2758_backup_completion_selected as previous

SOURCE=previous.SOURCE
FILES=[previous.FILES[0],'tools/quality/vm/050_s1/Pg2762PostBeginIdentityLauncher.java',*previous.FILES[2:]]


def server():
    raw=previous.server().replace('PG2758','PG2762').replace('Pg2758BackupCompletionFailureLauncher','Pg2762PostBeginIdentityLauncher')
    compile(raw,'<actual persisted post-begin identity>','exec');return raw


def transport_body():
    raw=previous.transport_body().replace('PG2758','PG2762').replace('pg2758','pg2762')
    if raw.count('PG2762-selected-v1')!=5 or 'PG2758' in raw:
        raise ValueError('complete new-only post-begin transport required')
    compile(raw,'<current post-begin transport>','exec');return raw


def main():
    base=previous.previous.previous
    ns={**base.transport.__dict__,'SOURCE':SOURCE,'FILES':FILES,'SLOT':'pg2762-post-begin-identity-selected-v1',
        'SERVER':server(),'native_input':base.native_input}
    exec(compile(transport_body(),'<actual post-begin selected source>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
