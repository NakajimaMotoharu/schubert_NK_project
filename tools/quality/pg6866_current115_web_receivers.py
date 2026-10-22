"""Current4209 original SQL115 join, no new PT or runtime operation."""
import inspect
import pg6672_current115_receivers as prior
from pg6864_original4209_artifacts import read_whole


def definition():
    raw=inspect.getsource(prior.main)
    if raw.count('PG6672-current115-receivers-v1')!=1 or raw.count('currentWholeTests=4170')!=1:raise ValueError('one SQL115 output/count binding')
    raw=raw.replace('PG6672-current115-receivers-v1','PG6866-current115-web-receivers-v1').replace('currentWholeTests=4170','currentWholeTests=4209')
    scope={**vars(prior),'read_whole':read_whole};exec(compile(raw,'<current4209 SQL115>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
