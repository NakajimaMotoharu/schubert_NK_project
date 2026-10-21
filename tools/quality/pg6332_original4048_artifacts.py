"""Read only genuine original4048 artifacts, never restart PT for missing results."""
import inspect
import pg6198_original4024_artifacts as prior
from pg6326_web_graph_qualification import original_source

OLD='5eb040421ae9ea06ecc70c6eb2e152871c2d0d42'


def definitions():
    scope={**vars(prior),'OLD':OLD,'original_source':original_source}
    for name in ('new_case_identities','main'):
        raw=inspect.getsource(getattr(prior,name))
        for before,after in (
            ('!=36','!=5'),('exact36','exact5'),('len(owners)!=13','len(owners)!=4'),('exact13','exact4'),
            ('pg6196-management-ownership-six-v1','pg6330-outbox-graph-six-v1'),('PG6196-six-v1','PG6330-six-v1'),('PG6196','PG6330'),
            ('PG6118-current3988-cases','PG6302-current4043-cases'),
            ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23','eed16f1405f305011467e1a0154747ae0c3483bb0d37e98888a2f9f2816b79a1'),
            ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47','9ebb095baca6637058bcf3361c8b71428405827f6deb464f69ad65269cfee770'),
            ('PG6193-management-primary-qualification-v2','PG6326-web-graph-qualification-v1'),
            ('pg6193-management-primary-qualification-v2','pg6326-web-graph-qualification-v1'),
            ('(60,20)','(89,15)'),('source60','source89'),('[4024,605,1667]','[4048,607,1667]'),
            ('pg6198-original4024-artifacts-v1','pg6332-original4048-artifacts-v1'),
            ('PG6198-original4024-v1','PG6332-original4048-v1'),('PG6330-current4024-cases','PG6330-current4048-cases')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<original4048 '+name+'>','exec'),scope)
    return scope


def new_case_identities(source):return definitions()['new_case_identities'](source)
def main():return definitions()['main']()


if __name__=='__main__':main()
