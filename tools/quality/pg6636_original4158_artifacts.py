"""Qualify the one original4158 whole; never rebuild/replay missing results."""
import inspect
from types import SimpleNamespace
import pg6042_original3976_artifacts as reader
import pg6198_original4024_artifacts as prior
from pg6634_jdbc_jms_whole import original_source,OLD


def emitted(data_hash,remote):
    raw=reader.emitted(data_hash,remote)
    anchor="('PG6490', (4064, 612, 1667), 1))"
    if raw.count(anchor)!=1 or raw.count("'PG6490')")!=1:raise ValueError('one explicit original whole/counter export guard')
    raw=raw.replace(anchor,"('PG6490', (4064, 612, 1667), 1), ('PG6634', (4158, 635, 1667), 45))",1)
    raw=raw.replace("'PG6490')","'PG6490', 'PG6634')",1)
    compile(raw,'<original4158 explicit reader>','exec')
    return raw


def collect(*args,**kwargs):
    raw=inspect.getsource(reader.collect)
    if raw.count("'PG6490')")!=1:raise ValueError('one original coverage import guard')
    scope={**vars(reader),'emitted':emitted}
    exec(compile(raw.replace("'PG6490')","'PG6490', 'PG6634')",1),'<original4158 collect>','exec'),scope)
    return scope['collect'](*args,**kwargs)


def definitions():
    scope={**vars(prior),'OLD':OLD,'original_source':original_source,
           'reader':SimpleNamespace(**{**vars(reader),'collect':collect})}
    for name in ('new_case_identities','main'):
        raw=inspect.getsource(getattr(prior,name))
        for before,after in (
          ('!=36','!=85'),('exact36','exact85'),('len(owners)!=13','len(owners)!=45'),('exact13','exact45'),
          ('pg6196-management-ownership-six-v1','pg6634-jdbc-jms-six-v1'),
          ('PG6196-six-v1','PG6634-six-v1'),('PG6196','PG6634'),
          ('PG6118-current3988-cases','PG6524-current4073-cases'),
          ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23','411c8764bba9ae6fa01c24d27c2b4f2cacf02686b568d9d1d6912cc5ef4da936'),
          ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47','624114713fa21f7f6f600c81cfb553fa3a8445464fd2d3785e3e6a256f0eead8'),
          ('PG6193-management-primary-qualification-v2','PG6632-jms-secondary-qualification-v1'),
          ('pg6193-management-primary-qualification-v2','pg6632-jms-secondary-qualification-v1'),
          ('(60,20)','(86,17)'),('source60','source86'),('[4024,605,1667]','[4158,635,1667]'),
          ('pg6198-original4024-artifacts-v1','pg6636-original4158-artifacts-v1'),
          ('PG6198-original4024-v1','PG6636-original4158-v1'),
          ('PG6634-current4024-cases','PG6634-current4158-cases')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<original4158 '+name+'>','exec'),scope)
    return scope


def new_case_identities(source):return definitions()['new_case_identities'](source)
def main():return definitions()['main']()


if __name__=='__main__':main()
