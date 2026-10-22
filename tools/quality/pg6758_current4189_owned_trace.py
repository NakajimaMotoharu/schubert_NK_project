"""Refresh943 original4189 host measurement only; historical acceptance/cost immutable."""
import argparse
import inspect
import pg6532_current4073_trace as previous
from pg6750_original4189_owned_artifacts import read_whole

ROOT,PMO,NAMES,W,BASE=previous.ROOT,previous.PMO,previous.NAMES,previous.W,previous.BASE
SOURCE='bad7b45337d10341e9972cc9b3f7a0b43d21e465'
OUT=W/'pg6758-current4189-owned-trace-v1'
PUBLIC=BASE/'PG6758-current4189-owned-host-measurement-v1'
require,sha,trace,audit=previous.require,previous.sha,previous.trace,previous.audit


def read_qualified():
    qp,q,_=read_whole();require(q['productionSource']==SOURCE,'frozen genuine owned4189 source');return qp,q


def definitions(qsha,csha):
    scope={**vars(previous),'prior':previous.prior,'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,
      'read_qualified':read_qualified,'candidates':candidates}
    raw=inspect.getsource(previous.definitions)
    for before,after in (('4073','4189'),('614','645'),('PG6524-six-v1','PG6748-six-v1'),('PG6532-current943-trace-v1','PG6758-current943-trace-v1')):raw=raw.replace(before,after)
    exec(compile(raw,'<owned4189 trace definitions>','exec'),scope);return scope['definitions'](qsha,csha)


def authenticated():
    qp,_=read_qualified();return definitions(sha(qp.read_bytes()),sha(qp.with_name('cases.json').read_bytes()))


def measurement():return authenticated()['measurement']()


def candidates(texts,before_head):
    scope={**vars(previous.prior),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'measurement':measurement}
    raw=inspect.getsource(previous.prior.candidates)
    raw=raw.replace('870010d6681d74519237be7a7ca6381a190f471a','01e41088c6562c3b7d103ae0bacc9f693bc1aad4').replace('4034','4189')
    exec(compile(raw,'<current943 preserve observer4184 history>','exec'),scope);return scope['candidates'](texts,before_head)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['publish','stage','apply','report'])
    authenticated()[p.parse_args().action]()
