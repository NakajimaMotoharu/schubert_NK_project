"""Join all115 SQL identities to genuine4189 XML; no PT or operational action."""
import inspect
import pg6672_current115_receivers as prior
from pg6750_original4189_owned_artifacts import read_whole


def definition():
    raw=inspect.getsource(prior.main)
    if raw.count("'PG6672-current115-receivers-v1'")!=1 or raw.count('currentWholeTests=4170')!=1:raise ValueError('one SQL115 publication/count binding')
    raw=raw.replace('PG6672-current115-receivers-v1','PG6752-current115-owned-receivers-v1').replace('currentWholeTests=4170','currentWholeTests=4189')
    scope={**vars(prior),'read_whole':read_whole}
    exec(compile(raw,'<owned4189 SQL115>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
