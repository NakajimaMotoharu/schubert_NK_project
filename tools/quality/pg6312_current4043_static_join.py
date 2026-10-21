"""Bind current reasons only to original4043 after its genuine independent qualification."""
import inspect
import pg6282_current4040_static_join as prior
from pg6306_current4043_trace import SOURCE,read_qualified
from pg6308_current4043_static_plan import PRIOR,PRIOR_SHA,OLD

INPUT=prior.BASE/'PG6310-web321-static-review-v1/manifest.json'
INPUT_SHA='d848def968743126450d2e5d770c986e00e23352f0bdb57a42ef6b5e07425fe9'


def definitions():
    scope={**vars(prior),'SOURCE':SOURCE,'read_qualified':read_qualified,'PRIOR':PRIOR,'PRIOR_SHA':PRIOR_SHA,
        'OLD':OLD,'INPUT':INPUT,'INPUT_SHA':INPUT_SHA}
    raw=inspect.getsource(prior.main)
    for a,b in (('4040','4043'),('1350','1357'),('PG6272','PG6302'),
        ('PG6268-outbox-failure-qualification-v1','PG6298-web-send-qualification-v1'),
        ('pg6268-outbox-failure-qualification-v1','pg6298-web-send-qualification-v1'),
        ('d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225','00b8f41991bf05c2aaf439cc502ecf6afba47f9247587684941ee168dbc75c27'),
        ('pg6266-outbox-failure-selected-v1','pg6296-web-send-selected-v1'),('PG6282-current4043-static-join-v1','PG6312-current4043-static-join-v1')):
        if a not in raw:raise ValueError('explicit current source/whole static binding '+a)
        raw=raw.replace(a,b)
    exec(compile(raw,'<actual4043 semantic join>','exec'),scope)
    return scope


def main():return definitions()['main']()


if __name__=='__main__':main()
