"""Refresh existing943 from original4203 API source; keep history/formal17/cost unchanged."""
import argparse
import inspect
import pg6816_current4202_trace as previous
import pg6778_current4197_transfer_trace as core
from pg6830_original4203_artifacts import read_whole

ROOT,PMO,NAMES,W,BASE=previous.ROOT,previous.PMO,previous.NAMES,previous.W,previous.BASE
SOURCE='4c0343a55b5fe41dad766a520558363e81f01541'
OUT=W/'pg6838-current4203-trace-v1'
PUBLIC=BASE/'PG6838-current4203-host-measurement-v1'
require,sha,trace,audit=previous.require,previous.sha,previous.trace,previous.audit


def read_qualified():
    qp,q,_=read_whole();require(q['productionSource']==SOURCE,'current original4203 source');return qp,q


def definitions(qsha,csha):
    scope={**vars(previous),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'read_qualified':read_qualified,'candidates':candidates}
    raw=inspect.getsource(previous.definitions)
    for before,after in (('4202','4203'),('649','650'),('PG6802-six-v1','PG6828-six-v1'),('PG6816-current943-trace-v1','PG6838-current943-trace-v1')):raw=raw.replace(before,after)
    exec(compile(raw,'<current4203/1669 trace definitions>','exec'),scope);return scope['definitions'](qsha,csha)


def authenticated():
    qp,_=read_qualified();return definitions(sha(qp.read_bytes()),sha(qp.with_name('cases.json').read_bytes()))


def measurement():return authenticated()['measurement']()


def candidates(texts,before_head):
    scope={**vars(core),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'measurement':measurement}
    raw=inspect.getsource(core.candidates).replace('bad7b45337d10341e9972cc9b3f7a0b43d21e465','484c92f1ba158a669be3bf68d26b59d8d4622cbd').replace("'4197'","'4203'")
    exec(compile(raw,'<preserve484c current943 history>','exec'),scope);return scope['candidates'](texts,before_head)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['publish','stage','apply','report']);authenticated()[p.parse_args().action]()
