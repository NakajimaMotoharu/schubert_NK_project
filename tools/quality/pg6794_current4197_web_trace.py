"""Refresh existing943 from current4197 original Web source, preserve formal/history/cost."""
import inspect
import pg6778_current4197_transfer_trace as prior
from pg6786_original4197_web_artifacts import read_whole

ROOT,PMO,NAMES,W,BASE=prior.ROOT,prior.PMO,prior.NAMES,prior.W,prior.BASE
SOURCE='3c5f03d4aca569e4f5e722d7357e04749ad0998c'
OUT=W/'pg6794-current4197-web-trace-v1'
PUBLIC=BASE/'PG6794-current4197-web-host-measurement-v1'
require,sha,trace,audit=prior.require,prior.sha,prior.trace,prior.audit


def read_qualified():
    qp,q,_=read_whole();require(q['productionSource']==SOURCE,'current Web original4197 source');return qp,q


def definitions(qsha,csha):
    scope={**vars(prior),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'read_qualified':read_qualified,'candidates':candidates}
    raw=inspect.getsource(prior.definitions).replace('PG6768-six-v1','PG6784-six-v1').replace('PG6778-current943-trace-v1','PG6794-current943-trace-v1')
    exec(compile(raw,'<Web4197 trace definitions>','exec'),scope);return scope['definitions'](qsha,csha)


def authenticated():
    qp,_=read_qualified();return definitions(sha(qp.read_bytes()),sha(qp.with_name('cases.json').read_bytes()))


def measurement():return authenticated()['measurement']()


def candidates(texts,before_head):
    scope={**vars(prior),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'measurement':measurement}
    raw=inspect.getsource(prior.candidates).replace('bad7b45337d10341e9972cc9b3f7a0b43d21e465','d549f8855fe1733bdb67543e310048dc271a8a56')
    exec(compile(raw,'<preserve d549 current943 history>','exec'),scope);return scope['candidates'](texts,before_head)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('action',choices=['publish','stage','apply','report']);authenticated()[p.parse_args().action]()
