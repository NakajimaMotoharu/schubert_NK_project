"""Reauthenticate raw1356 current source/families; all fourteen unresolved bindings stay held."""
import inspect
import json
import os
import pg6308_current4043_static_plan as prior
from pg6326_web_graph_qualification import original_source
from static_disposition_overlay import load

ROOT,W,BASE,sha=prior.ROOT,prior.W,prior.BASE,prior.sha
PRIOR=BASE/'PG6312-current4043-static-join-v1/manifest.json'
PRIOR_SHA='657a16a4c95104cc295229882b21a8c2acc14db9ece42414268b61b04ca31cc0'
OLD='5eb040421ae9ea06ecc70c6eb2e152871c2d0d42'


def calculate():
    scope={**vars(prior),'PRIOR':PRIOR,'PRIOR_SHA':PRIOR_SHA,'OLD':OLD,'original_source':original_source,'load':load}
    raw=inspect.getsource(prior.calculate)
    for before,after in (
        ('PG6298-web-send-qualification-v1','PG6326-web-graph-qualification-v1'),
        ('pg6298-web-send-qualification-v1','pg6326-web-graph-qualification-v1'),
        ('00b8f41991bf05c2aaf439cc502ecf6afba47f9247587684941ee168dbc75c27','e8e0961898824f64eb493a18995ca9f8ddb27be84a1805314fac703426a426bf'),
        ('PG6272-current4040-cases','PG6302-current4043-cases'),
        ('dc3e2e9b2cb435307b3c248964452e93dfc008a23a69072d8d4e9046dec8eed5','eed16f1405f305011467e1a0154747ae0c3483bb0d37e98888a2f9f2816b79a1'),
        ('1357','1356'),('selected84','selected89')):
        if before not in raw:raise ValueError('one explicit current1356/static binding '+before)
        raw=raw.replace(before,after)
    exec(compile(raw,'<current1356 source-family reauthentication>','exec'),scope)
    return scope['calculate']()


def main():
    rows,value=calculate();os.umask(0o077);out=BASE/'PG6336-current4048-static-plan-v1';out.mkdir()
    with(out/'findings.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['inventorySha256']=sha(out/'findings.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=value['source'],statusCounts=value['statusCounts'],strictReboundPriorDecided=value['strictReboundPriorDecided'],priorUnresolvedRetained=14,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
