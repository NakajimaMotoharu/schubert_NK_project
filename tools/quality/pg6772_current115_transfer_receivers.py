"""Current4197 original SQL115 join only, no PT or operations."""
import inspect
import pg6672_current115_receivers as prior
from pg6770_original4197_transfer_artifacts import read_whole


def definition():
    raw=inspect.getsource(prior.main)
    if raw.count("'PG6672-current115-receivers-v1'")!=1 or raw.count('currentWholeTests=4170')!=1:raise ValueError('exact current115 binding')
    raw=raw.replace('PG6672-current115-receivers-v1','PG6772-current115-transfer-receivers-v1').replace('currentWholeTests=4170','currentWholeTests=4197')
    scope={**vars(prior),'read_whole':read_whole};exec(compile(raw,'<Transfer4197 SQL115>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
