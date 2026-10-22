"""Same-source raw1404 join after stateless ordinary observer sharing; held scopes unchanged."""
import inspect
import pg6716_current4184_static_join as prior
from pg6728_original4184_observer_artifacts import read_whole

ROOT,W,BASE,sha=prior.ROOT,prior.W,prior.BASE,prior.sha
OLD='d48f8ebf8ed4047763c77fe487c44f7caa03e8f8'
PRIOR=BASE/'PG6716-current4184-static-join-v1/manifest.json'
PRIOR_SHA='a7f15b08a802804a10ca8fec5217c4af7a407515f55ef36f8fb7f86aae008a82'
QSHA='70670e2540807bf2c8357d285d50c9aa0a19434b04406cfab8b344ef4dae2fd6'
EXPECTED_RAW=1404
EXPECTED_PAIRS=1382


def bindings():
    scope={**vars(prior),'OLD':OLD,'PRIOR':PRIOR}
    exec(compile(inspect.getsource(prior.bindings),'<observer4184 bindings>','exec'),scope)
    return scope['bindings']()


def review_changed(row):
    name=row['sourcePath'].rsplit('/',1)[-1].removesuffix('.java')
    if name not in ('ArtemisConnectionFactoryProvider','WebBrokerContexts'):
        raise ValueError('only two exact same-token observer source contexts')
    value=prior.review_changed(row)
    value['reason']+=' PG-D500/1474: private stateless ordinary callback shared; all six old callsites expand exactly to prior tokens, including native choices. No authority or outcome change.'
    value['ordinaryObserverExpansionPrivateSha256']='1f53283b55fb4ebc7a7cf6c13cdfd8141ebe8b6da369f65d676ecbbfa0e29608'
    return value


def definition():
    raw=inspect.getsource(prior.main)
    for before,after in (
      ('PG6712-broker-parent-qualification-v3','PG6724-broker-observer-qualification-v1'),
      ('pg6712-broker-parent-qualification-v3','pg6724-broker-observer-qualification-v1'),
      ('PG6716-current4184-static-join-v1','PG6732-current4184-observer-static-join-v1'),
      ('pg6716_current4184_static_join.py','pg6732_current4184_observer_static_join.py')):
        raw=raw.replace(before,after)
    scope={**vars(prior),'OLD':OLD,'PRIOR':PRIOR,'PRIOR_SHA':PRIOR_SHA,'QSHA':QSHA,
      'EXPECTED_RAW':EXPECTED_RAW,'EXPECTED_PAIRS':EXPECTED_PAIRS,
      'read_whole':read_whole,'bindings':bindings,'review_changed':review_changed}
    exec(compile(raw,'<observer4184 static join>','exec'),scope)
    return scope['main']


if __name__=='__main__':definition()()
