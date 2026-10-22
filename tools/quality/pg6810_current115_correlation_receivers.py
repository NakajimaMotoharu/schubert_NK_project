"""Current4202 original SQL115 join, not additional PT."""
import inspect
import pg6672_current115_receivers as prior
from pg6804_original4202_artifacts import read_whole


def definition():
    raw=inspect.getsource(prior.main)
    if raw.count('PG6672-current115-receivers-v1')!=1 or raw.count('currentWholeTests=4170')!=1:raise ValueError('one exact SQL115 output/count binding')
    raw=raw.replace('PG6672-current115-receivers-v1','PG6810-current115-correlation-receivers-v1').replace('currentWholeTests=4170','currentWholeTests=4202')
    scope={**vars(prior),'read_whole':read_whole};exec(compile(raw,'<current4202 SQL115>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
