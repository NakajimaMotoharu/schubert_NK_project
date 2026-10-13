"""Readonly actual once-issued Job/current boot/new run and Root identity binding."""
import inspect
import pg2180_newsource_live_binding as prior
from pg2446_question_current_observer import SOURCE,BOM,BOOT

SLOT='pg2450-question-current-live-binding-v1'


def body():
    raw=prior.body().replace('PG2126','PG2428').replace(
        '3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT).replace(
        '3d69f5af6bac46b1a5407591c4a79a0d',BOOT.replace('-',''))
    marker="require(fields[1]!='a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'and fields[3]!='9026b2ab-bb42-49cd-a2bd-4c661049dce3')"
    if raw.count(marker)!=1:raise ValueError('explicit prior source completion guard required')
    return raw.replace(marker,marker+"\nrequire(fields[1]!='91f5484b-9702-4c7c-97f3-dd5110a853f9'and fields[3]!='e1429ac8-f3dd-4e8c-83d2-1926c4ba8440')")


def entry():
    raw=inspect.getsource(prior.prior.transport.main).replace('pg2015-completed-run-fresh-resume-once-v1','pg2448-question-current-noargs-once-v1')
    ns={**prior.prior.transport.__dict__,'SOURCE':SOURCE,'BOM':BOM,'SLOT':SLOT,'body':body}
    exec(compile(raw,'<new current read-only live binding transport>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
