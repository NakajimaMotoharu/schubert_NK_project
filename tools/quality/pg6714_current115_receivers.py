"""Rebind the immutable115 SQL catch identities to the genuine original4184 only."""
import inspect
import pg6672_current115_receivers as prior
from pg6708_original4184_artifacts import read_whole


def definition():
    raw=inspect.getsource(prior.main)
    if raw.count("'PG6672-current115-receivers-v1'")!=1 or raw.count('currentWholeTests=4170')!=1:
        raise ValueError('one original115 publication/count binding')
    raw=raw.replace('PG6672-current115-receivers-v1','PG6714-current115-receivers-v1').replace('currentWholeTests=4170','currentWholeTests=4184')
    scope={**vars(prior),'read_whole':read_whole}
    exec(compile(raw,'<original4184 SQL115>','exec'),scope)
    return scope['main']


if __name__=='__main__':definition()()
