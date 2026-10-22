"""Current4197 Web SQL115 original join, no PT or operations."""
import inspect
import pg6772_current115_transfer_receivers as prior
from pg6786_original4197_web_artifacts import read_whole


def definition():
    raw=inspect.getsource(prior.prior.main)
    if raw.count('PG6672-current115-receivers-v1')!=1 or raw.count('currentWholeTests=4170')!=1:raise ValueError('one exact115 output/count binding')
    raw=raw.replace('PG6672-current115-receivers-v1','PG6788-current115-web-receivers-v1').replace('currentWholeTests=4170','currentWholeTests=4197')
    scope={**vars(prior.prior),'read_whole':read_whole};exec(compile(raw,'<Web4197 SQL115>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
