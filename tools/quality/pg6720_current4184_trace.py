"""Refresh current943 only from original4184, retaining historical acceptance and budgets."""
import argparse
import inspect
import pg6532_current4073_trace as previous
from pg6708_original4184_artifacts import read_whole

ROOT,PMO,NAMES,W,BASE=previous.ROOT,previous.PMO,previous.NAMES,previous.W,previous.BASE
SOURCE='d48f8ebf8ed4047763c77fe487c44f7caa03e8f8'
OUT=W/'pg6720-current4184-trace-v1'
PUBLIC=BASE/'PG6720-current4184-host-measurement-v1'
require,sha,trace,audit=previous.require,previous.sha,previous.trace,previous.audit


def read_qualified():
    qp,q,_=read_whole();require(q['productionSource']==SOURCE,'frozen genuine original4184 source')
    return qp,q


def definitions(qsha,csha):
    scope={**vars(previous),'prior':previous.prior,'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,
           'read_qualified':read_qualified,'candidates':candidates}
    raw=inspect.getsource(previous.definitions)
    for before,after in (('4073','4184'),('614','643'),('PG6524-six-v1','PG6706-six-v1'),
                         ('PG6532-current943-trace-v1','PG6720-current943-trace-v1')):
        raw=raw.replace(before,after)
    exec(compile(raw,'<original4184 trace definitions>','exec'),scope)
    return scope['definitions'](qsha,csha)


def authenticated():
    qp,_=read_qualified();return definitions(sha(qp.read_bytes()),sha(qp.with_name('cases.json').read_bytes()))


def measurement():return authenticated()['measurement']()


def candidates(texts,before_head):
    scope={**vars(previous.prior),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'measurement':measurement}
    raw=inspect.getsource(previous.prior.candidates)
    raw=raw.replace('870010d6681d74519237be7a7ca6381a190f471a','f16f717d4e5338e7f5b44faef179ada0cf19aae0').replace('4034','4184')
    exec(compile(raw,'<current943 refresh preserving oldf16f history>','exec'),scope)
    return scope['candidates'](texts,before_head)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['publish','stage','apply','report'])
    args=parser.parse_args();authenticated()[args.action]()
