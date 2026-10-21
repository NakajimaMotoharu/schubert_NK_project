"""Refresh current943 from original4158; historical941/17/costs/formal stay immutable."""
import argparse
import inspect
import pg6532_current4073_trace as previous
from pg6638_current115_receivers import read_whole

ROOT,PMO,NAMES,W,BASE=previous.ROOT,previous.PMO,previous.NAMES,previous.W,previous.BASE
SOURCE='2d4633fb25e2c47b2adcbada8c932aba727f20fd'
OUT=W/'pg6642-current4158-trace-v1'
PUBLIC=BASE/'PG6642-current4158-host-measurement-v1'
require,sha,trace,audit=previous.require,previous.sha,previous.trace,previous.audit


def read_qualified():
    qp,q,_=read_whole()
    require(q['productionSource']==SOURCE,'frozen original4158 source')
    return qp,q


def definitions(qsha,csha):
    scope={**vars(previous),'prior':previous.prior,'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,
           'read_qualified':read_qualified,'candidates':candidates}
    raw=inspect.getsource(previous.definitions)
    for before,after in (('4073','4158'),('614','635'),('PG6524-six-v1','PG6634-six-v1'),
                         ('PG6532-current943-trace-v1','PG6642-current943-trace-v1')):
        raw=raw.replace(before,after)
    exec(compile(raw,'<original4158 trace definitions>','exec'),scope)
    return scope['definitions'](qsha,csha)


def authenticated():
    qp,_=read_qualified()
    return definitions(sha(qp.read_bytes()),sha(qp.with_name('cases.json').read_bytes()))


def measurement():return authenticated()['measurement']()


def candidates(texts,before_head):
    scope={**vars(previous.prior),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'measurement':measurement}
    raw=inspect.getsource(previous.prior.candidates)
    raw=raw.replace('870010d6681d74519237be7a7ca6381a190f471a',previous.SOURCE).replace('4034','4158')
    exec(compile(raw,'<immutable current943 refresh to4158>','exec'),scope)
    return scope['candidates'](texts,before_head)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['publish','stage','apply','report'])
    args=parser.parse_args();authenticated()[args.action]()
