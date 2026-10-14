"""Actual DB pair guard; independent per-row-valid timestamp drift, committed SQL unchanged."""
import pg2780_resume_skip_history_selected as previous

SOURCE=previous.SOURCE
FILES=[previous.FILES[0],'tools/quality/vm/050_s1/Pg2788PairTimestampLauncher.java',*previous.FILES[2:]]


def server():
    raw=previous.server().replace('PG2780','PG2788').replace('Pg2780ResumeSkippedLauncher','Pg2788PairTimestampLauncher')
    compile(raw,'<actual paired timestamp refusal server>','exec');return raw


def transport_body():
    raw=previous.transport_body().replace('PG2780','PG2788').replace('pg2780','pg2788')
    if raw.count('PG2788-selected-v1')!=5:raise ValueError('complete one new-only transport required')
    compile(raw,'<pair timestamp complete transport>','exec');return raw


def main():
    base=previous.previous
    ns={**base.transport.__dict__,'SOURCE':SOURCE,'FILES':FILES,'SLOT':'pg2788-success-pair-timestamp-selected-v1','SERVER':server(),'native_input':previous.native_input}
    exec(compile(transport_body(),'<actual timestamp pair input>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
