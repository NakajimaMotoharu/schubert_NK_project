"""Current943 refreshed from original4209 only; formal/history17/cost immutable."""
import argparse
import inspect
import pg6838_current4203_trace as previous
import pg6778_current4197_transfer_trace as core
from pg6864_original4209_artifacts import read_whole

ROOT,PMO,NAMES,W,BASE=previous.ROOT,previous.PMO,previous.NAMES,previous.W,previous.BASE
SOURCE='2b2e4f70746bd1e1e405e18427dfd45616f51623'
OUT=W/'pg6872-current4209-trace-v1'
PUBLIC=BASE/'PG6872-current4209-host-measurement-v1'
require,sha,trace,audit=previous.require,previous.sha,previous.trace,previous.audit


def read_qualified():
    qp,q,_=read_whole();require(q['productionSource']==SOURCE,'genuine current4209 source');return qp,q


def definitions(qsha,csha):
    scope={**vars(previous),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'read_qualified':read_qualified,'candidates':candidates}
    raw=inspect.getsource(previous.definitions)
    for before,after in(('4203','4209'),('650','653'),('PG6828-six-v1','PG6862-six-v1'),('PG6838-current943-trace-v1','PG6872-current943-trace-v1')):raw=raw.replace(before,after)
    exec(compile(raw,'<current4209 trace definitions>','exec'),scope);return scope['definitions'](qsha,csha)


def authenticated():
    qp,_=read_qualified();return definitions(sha(qp.read_bytes()),sha(qp.with_name('cases.json').read_bytes()))


def measurement():return authenticated()['measurement']()


def candidates(texts,before_head):
    scope={**vars(core),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'measurement':measurement}
    raw=inspect.getsource(core.candidates).replace('bad7b45337d10341e9972cc9b3f7a0b43d21e465','4c0343a55b5fe41dad766a520558363e81f01541').replace("'4197'","'4209'")
    exec(compile(raw,'<preserve4c034 current943 history>','exec'),scope);return scope['candidates'](texts,before_head)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['publish','stage','apply','report']);authenticated()[p.parse_args().action]()
