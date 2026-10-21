"""Bind current1356 only after original4048 genuinely qualifies; unresolved14 stay held."""
import inspect
import pg6282_current4040_static_join as prior
from pg6334_current4048_trace import SOURCE,read_qualified
from pg6336_current4048_static_plan import PRIOR,PRIOR_SHA,OLD

INPUT=prior.BASE/'PG6338-outbox-graph-static-review-v1/manifest.json'
INPUT_SHA='913d5fb156d4e7c99a679f4699b829bed01cab175fa06427c1769f871929499a'


def definitions():
    scope={**vars(prior),'SOURCE':SOURCE,'read_qualified':read_qualified,'PRIOR':PRIOR,'PRIOR_SHA':PRIOR_SHA,
        'OLD':OLD,'INPUT':INPUT,'INPUT_SHA':INPUT_SHA}
    raw=inspect.getsource(prior.main)
    for a,b in (('4040','4048'),('1350','1356'),('PG6272','PG6330'),
        ('PG6268-outbox-failure-qualification-v1','PG6326-web-graph-qualification-v1'),
        ('pg6268-outbox-failure-qualification-v1','pg6326-web-graph-qualification-v1'),
        ('d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225','e8e0961898824f64eb493a18995ca9f8ddb27be84a1805314fac703426a426bf'),
        ('pg6266-outbox-failure-selected-v1','pg6324-web-graph-selected-v1'),('PG6282-current4048-static-join-v1','PG6340-current4048-static-join-v1')):
        if a not in raw:raise ValueError('explicit current source/whole static binding '+a)
        raw=raw.replace(a,b)
    exec(compile(raw,'<actual4048 semantic join>','exec'),scope)
    return scope


def main():return definitions()['main']()


if __name__=='__main__':main()
