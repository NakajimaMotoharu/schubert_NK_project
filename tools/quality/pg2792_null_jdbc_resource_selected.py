"""Reproduce null JDBC boundary against unchanged current Main before any production fix."""
import pg2780_resume_skip_history_selected as previous

SOURCE=previous.SOURCE
FILES=[previous.FILES[0],'tools/quality/vm/050_s1/Pg2792NullJdbcResourcesLauncher.java',*previous.FILES[2:]]


def server():
    raw=previous.server().replace('PG2780','PG2792').replace('Pg2780ResumeSkippedLauncher','Pg2792NullJdbcResourcesLauncher').replace('PG2792-selected-v1','PG2792-selected-v2')
    compile(raw,'<actual null JDBC resource baseline>','exec');return raw


def transport_body():
    raw=previous.transport_body().replace('PG2780','PG2792').replace('pg2780','pg2792').replace('PG2792-selected-v1','PG2792-selected-v2')
    if raw.count('PG2792-selected-v2')!=5:raise ValueError('completed one new-only baseline required')
    compile(raw,'<null-resource complete transport>','exec');return raw


def main():
    base=previous.previous
    ns={**base.transport.__dict__,'SOURCE':SOURCE,'FILES':FILES,'SLOT':'pg2792-null-jdbc-resource-selected-v2','SERVER':server(),'native_input':previous.native_input}
    exec(compile(transport_body(),'<actual unmodified Main null boundary>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
