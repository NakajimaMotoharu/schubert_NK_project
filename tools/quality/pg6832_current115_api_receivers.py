"""Current4203 original SQL115 join; no extra PT or operations."""
import inspect
import pg6672_current115_receivers as prior
from pg6830_original4203_artifacts import read_whole


def definition():
    raw=inspect.getsource(prior.main)
    if raw.count('PG6672-current115-receivers-v1')!=1 or raw.count('currentWholeTests=4170')!=1:raise ValueError('one SQL115 output/count binding')
    raw=raw.replace('PG6672-current115-receivers-v1','PG6832-current115-api-receivers-v1').replace('currentWholeTests=4170','currentWholeTests=4203')
    scope={**vars(prior),'read_whole':read_whole};exec(compile(raw,'<current4203 SQL115>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
