"""Exact115 SQL rebind to the genuine observer4184, no replay."""
import inspect
import pg6672_current115_receivers as prior
from pg6728_original4184_observer_artifacts import read_whole


def definition():
    raw=inspect.getsource(prior.main)
    if raw.count("'PG6672-current115-receivers-v1'")!=1 or raw.count('currentWholeTests=4170')!=1:
        raise ValueError('one original115 publication/count binding')
    raw=raw.replace('PG6672-current115-receivers-v1','PG6730-current115-observer-receivers-v1').replace('currentWholeTests=4170','currentWholeTests=4184')
    scope={**vars(prior),'read_whole':read_whole}
    exec(compile(raw,'<observer4184 SQL115>','exec'),scope)
    return scope['main']


if __name__=='__main__':definition()()
