"""All Main bytes unchanged; exact1404 diagnostics rejoin original4189 without raw suppression."""
import inspect
import pg6716_current4184_static_join as prior
from pg6750_original4189_owned_artifacts import read_whole

ROOT,W,BASE,sha=prior.ROOT,prior.W,prior.BASE,prior.sha
OLD='01e41088c6562c3b7d103ae0bacc9f693bc1aad4'
PRIOR=BASE/'PG6732-current4184-observer-static-join-v1/manifest.json'
PRIOR_SHA='4c7ea9a3eac942a4d6b85dc5836156561bae564bdd9ad7f7677ff2e48d93c359'
QSHA='af3dcb55d39916cd4883ddfa37337c92033b60080e6e9c7c44de760a35b1714a'
EXPECTED_RAW=EXPECTED_PAIRS=1404


def bindings():
    scope={**vars(prior),'OLD':OLD,'PRIOR':PRIOR}
    exec(compile(inspect.getsource(prior.bindings),'<owned4189 bindings>','exec'),scope)
    return scope['bindings']()


def review_changed(row):raise ValueError('no changed Main diagnostic allowed in Test-only source')


def definition():
    raw=inspect.getsource(prior.main)
    for before,after in (('PG6712-broker-parent-qualification-v3','PG6746-request-read-original-v1'),
      ('pg6712-broker-parent-qualification-v3','pg6746-request-read-original-v1'),
      ('PG6716-current4184-static-join-v1','PG6754-current4189-owned-static-join-v1'),
      ('pg6716_current4184_static_join.py','pg6754_current4189_owned_static_join.py')):raw=raw.replace(before,after)
    scope={**vars(prior),'OLD':OLD,'PRIOR':PRIOR,'PRIOR_SHA':PRIOR_SHA,'QSHA':QSHA,
      'EXPECTED_RAW':EXPECTED_RAW,'EXPECTED_PAIRS':EXPECTED_PAIRS,'read_whole':read_whole,'bindings':bindings,'review_changed':review_changed}
    exec(compile(raw,'<owned4189 raw1404 join>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
