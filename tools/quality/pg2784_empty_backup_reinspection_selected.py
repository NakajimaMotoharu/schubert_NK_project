"""Actual DB boundary must reject empty reinspection; genuine committed SQL facts retained."""
import pg2780_resume_skip_history_selected as previous

SOURCE=previous.SOURCE
FILES=[previous.FILES[0],'tools/quality/vm/050_s1/Pg2784EmptyReinspectionLauncher.java',*previous.FILES[2:]]


def server():
    raw=previous.server().replace('PG2780','PG2784').replace('Pg2780ResumeSkippedLauncher','Pg2784EmptyReinspectionLauncher')
    compile(raw,'<actual empty reinspection server>','exec');return raw


def transport_body():
    raw=previous.transport_body().replace('PG2780','PG2784').replace('pg2780','pg2784')
    if raw.count('PG2784-selected-v1')!=5:raise ValueError('completed one new-only transport required')
    compile(raw,'<empty reinspection completed transport>','exec');return raw


def main():
    base=previous.previous
    ns={**base.transport.__dict__,'SOURCE':SOURCE,'FILES':FILES,'SLOT':'pg2784-empty-backup-reinspection-selected-v1','SERVER':server(),'native_input':previous.native_input}
    exec(compile(transport_body(),'<actual empty reinspection fixed input>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
