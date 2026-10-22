"""Current943/4202 original measurement only; preserve d549 history and canonical17/formal."""
import argparse
import inspect
import pg6778_current4197_transfer_trace as prior
from pg6804_original4202_artifacts import read_whole

ROOT,PMO,NAMES,W,BASE=prior.ROOT,prior.PMO,prior.NAMES,prior.W,prior.BASE
SOURCE='484c92f1ba158a669be3bf68d26b59d8d4622cbd'
OUT=W/'pg6816-current4202-trace-v1'
PUBLIC=BASE/'PG6816-current4202-host-measurement-v1'
require,sha,trace,audit=prior.require,prior.sha,prior.trace,prior.audit


def read_qualified():
    qp,q,_=read_whole();require(q['productionSource']==SOURCE,'current combined4202 source');return qp,q


def definitions(qsha,csha):
    scope={**vars(prior),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'read_qualified':read_qualified,'candidates':candidates}
    raw=inspect.getsource(prior.definitions)
    for before,after in (('4197','4202'),('646','649'),('PG6768-six-v1','PG6802-six-v1'),('PG6778-current943-trace-v1','PG6816-current943-trace-v1')):raw=raw.replace(before,after)
    exec(compile(raw,'<current4202/1669 trace definitions>','exec'),scope);return scope['definitions'](qsha,csha)


def authenticated():
    qp,_=read_qualified();return definitions(sha(qp.read_bytes()),sha(qp.with_name('cases.json').read_bytes()))


def measurement():return authenticated()['measurement']()


def candidates(texts,before_head):
    scope={**vars(prior),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'measurement':measurement}
    raw=inspect.getsource(prior.candidates).replace('bad7b45337d10341e9972cc9b3f7a0b43d21e465','d549f8855fe1733bdb67543e310048dc271a8a56').replace("'4197'","'4202'")
    exec(compile(raw,'<preserve d549 current943 history>','exec'),scope);return scope['candidates'](texts,before_head)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['publish','stage','apply','report']);authenticated()[p.parse_args().action]()
