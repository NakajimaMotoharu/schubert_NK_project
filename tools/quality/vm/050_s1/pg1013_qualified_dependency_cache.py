"""Install qualified926 dependency artifacts with exact preimage preservation, no new PT credit."""
import inspect
import json
from pg831_manager_collect import classes, sha
import pg913_frozen_dependency_cache as previous

def dependency_bytes():
    host=previous.W/'pg926-body-six-host-v1'
    record=json.loads((host/'manifest.safe.json').read_bytes())
    assert sha(host/'manifest.safe.json')=='4ae512d3b3a8e85d81fcd8e9ef04279fff58114c42e9b158adc61299d8211fdf'
    counts={}
    for module in ('protocol','storage','bootstrap'):
        name='schubert-nk-'+module
        jar=name+'-0.1.0-SNAPSHOT.jar'
        original=host/module/jar
        assert sha(original)==record['moduleResults'][module]['jarSha256']
        assert classes(original)==classes(previous.M2/'dev/codex/schubert'/name/'0.1.0-SNAPSHOT'/jar)
        counts[module]=len(classes(original))
    return counts

def code():
    raw=inspect.getsource(previous.main)
    for before,after in (
      ('pg857-completed-reference-six-host-v1','pg926-body-six-host-v1'),
      ('e01612fcd7f2752df5ae0836b78538fd5e87f120','40ef6e894573d2ffab1d1732124960f9c98d5f97'),
      ('pg913-frozen-dependency-cache-v1','pg1013-qualified-dependency-cache-v1')):
        assert raw.count(before)>0;raw=raw.replace(before,after)
    return raw

if __name__=='__main__':
    env=dict(previous.__dict__);env['dependency_bytes']=dependency_bytes
    exec(compile(code(),'<PG1013 byte-qualified cache install>','exec'),env);env['main']()
