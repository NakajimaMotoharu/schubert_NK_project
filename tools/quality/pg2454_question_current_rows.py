"""All24 independent same-day new-run rows oracle at the exact new before image."""
import inspect
import types
import pg2184_newsource_same_day_rows as prior
from pg2446_question_current_observer import SOURCE,BOOT

SLOT='pg2454-question-current-rows-v1'
BEFORE='b89bdd48eecd46af684341c5d0c27f639ce1282a9732086419ca2060bdb2c251'


def payload():
    raw=inspect.getsource(prior.prior.payload)
    for a,b in [('pg2074-current-newrun-live-binding-v1','pg2450-question-current-live-binding-v1'),
                ('pg2072-current-noargs-newrun-once-v1','pg2448-question-current-noargs-once-v1'),
                ('796965f389b631bf8abb49f6cbccf88955fbf3afe39edec0194316df35248a05',BEFORE),
                ('pg2079-current-same-day-rows-capture-v1',SLOT),
                ('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT)]:raw=raw.replace(a,b)
    ns={**prior.prior.__dict__,'transport':types.SimpleNamespace(SOURCE=SOURCE)}
    exec(compile(raw,'<current all24 independent oracle>','exec'),ns);return ns['payload']()


def entry():
    raw=inspect.getsource(prior.prior.transport.main).replace('pg2021-fresh-resume-terminal-receipt-v1','pg2452-question-current-terminal-v1')
    ns={**prior.prior.transport.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<current all24 read-only capture>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
