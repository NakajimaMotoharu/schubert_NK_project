"""Read only original4043 XML/Jars/counters; no repeated PT or actual runtime operations."""
import inspect
import pg6198_original4024_artifacts as prior
from pg6298_web_send_qualification import original_source

OLD='b4230118efcc429ee29d6e6f5761c55175f1e85e'


def definitions():
    scope={**vars(prior),'OLD':OLD,'original_source':original_source}
    for name in ('new_case_identities','main'):
        raw=inspect.getsource(getattr(prior,name))
        for before,after in (
            ('!=36','!=3'),('exact36','exact3'),('len(owners)!=13','len(owners)!=2'),('exact13','exact2'),
            ('pg6196-management-ownership-six-v1','pg6302-web-send-six-v1'),('PG6196-six-v1','PG6302-six-v1'),('PG6196','PG6302'),
            ('PG6118-current3988-cases','PG6272-current4040-cases'),
            ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23','dc3e2e9b2cb435307b3c248964452e93dfc008a23a69072d8d4e9046dec8eed5'),
            ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47','976a384def5907769df7cee4ea2848bc5f29aad3a9504a35bf7cde30a1fb4ae7'),
            ('PG6193-management-primary-qualification-v2','PG6298-web-send-qualification-v1'),
            ('pg6193-management-primary-qualification-v2','pg6298-web-send-qualification-v1'),
            ('(60,20)','(84,15)'),('source60','source84'),('[4024,605,1667]','[4043,607,1667]'),
            ('pg6198-original4024-artifacts-v1','pg6304-original4043-artifacts-v1'),
            ('PG6198-original4024-v1','PG6304-original4043-v1'),('PG6302-current4024-cases','PG6302-current4043-cases')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<original4043 '+name+'>','exec'),scope)
    return scope


def new_case_identities(source):return definitions()['new_case_identities'](source)
def main():return definitions()['main']()


if __name__=='__main__':main()
