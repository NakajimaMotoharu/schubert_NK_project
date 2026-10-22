"""Existing943 refreshed from original4197/1669 only; acceptance/history/cost immutable."""
import argparse
import inspect
import pg6532_current4073_trace as previous
from pg6770_original4197_transfer_artifacts import read_whole

ROOT,PMO,NAMES,W,BASE=previous.ROOT,previous.PMO,previous.NAMES,previous.W,previous.BASE
SOURCE='d549f8855fe1733bdb67543e310048dc271a8a56'
OUT=W/'pg6778-current4197-transfer-trace-v1'
PUBLIC=BASE/'PG6778-current4197-transfer-host-measurement-v1'
require,sha,trace,audit=previous.require,previous.sha,previous.trace,previous.audit


def read_qualified():
    qp,q,_=read_whole();require(q['productionSource']==SOURCE,'frozen genuine4197/1669 Transfer source');return qp,q


def definitions(qsha,csha):
    scope={**vars(previous),'prior':previous.prior,'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'read_qualified':read_qualified,'candidates':candidates}
    raw=inspect.getsource(previous.definitions)
    for before,after in (('4073','4197'),('614','646'),('PG6524-six-v1','PG6768-six-v1'),('PG6532-current943-trace-v1','PG6778-current943-trace-v1')):raw=raw.replace(before,after)
    exec(compile(raw,'<Transfer4197 trace definitions>','exec'),scope);d=scope['definitions'](qsha,csha)
    # Method bodies share the same dictionary; update measurement dimensions before publish/stage.
    body=inspect.getsource(previous.base.measurement)
    old="run='PG6088-six-v1', tests=3985, suites=595, mainClasses=1667"
    if body.count(old)!=1:raise ValueError('one full original measurement dimension tuple')
    body=body.replace(old,"run='PG6768-six-v1', tests=4197, suites=646, mainClasses=1669",1)
    exec(compile(body,'<exact original4197/1669 measurement>','exec'),d)
    return d


def authenticated():
    qp,_=read_qualified();return definitions(sha(qp.read_bytes()),sha(qp.with_name('cases.json').read_bytes()))


def measurement():return authenticated()['measurement']()


def candidates(texts,before_head):
    scope={**vars(previous.prior),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'measurement':measurement}
    raw=inspect.getsource(previous.prior.candidates)
    raw=raw.replace('870010d6681d74519237be7a7ca6381a190f471a','bad7b45337d10341e9972cc9b3f7a0b43d21e465').replace('4034','4197')
    exec(compile(raw,'<existing943 preserving original4189 history>','exec'),scope);return scope['candidates'](texts,before_head)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['publish','stage','apply','report']);authenticated()[p.parse_args().action]()
