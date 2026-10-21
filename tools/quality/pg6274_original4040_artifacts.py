"""Read only the original4040 XML/Jars/counters; no repeated PT or runtime actions."""
import inspect
import pg6198_original4024_artifacts as prior
from pg6268_outbox_failure_qualification import original_source

OLD='97dd2ba6185143632439f32dfc1d663061f1e55c'


def definitions():
    scope={**vars(prior),'OLD':OLD,'original_source':original_source}
    for name in ('new_case_identities','main'):
        raw=inspect.getsource(getattr(prior,name))
        for before,after in (
            ('!=36','!=6'),('exact36','exact6'),('len(owners)!=13','len(owners)!=2'),('exact13','exact2'),
            ('pg6196-management-ownership-six-v1','pg6272-outbox-failure-six-v1'),
            ('PG6196-six-v1','PG6272-six-v1'),('PG6196','PG6272'),
            ('PG6118-current3988-cases','PG6244-current4034-cases'),
            ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23','129f400938285f04cb016292b8e0822835f22d67bf3f899ec2f6e6b7b23004e9'),
            ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47','1f54f48b8ffd26d9739e74a0aa80ef4296c95a6096edb145783b274c44d638a8'),
            ('PG6193-management-primary-qualification-v2','PG6268-outbox-failure-qualification-v1'),
            ('pg6193-management-primary-qualification-v2','pg6268-outbox-failure-qualification-v1'),
            ('(60,20)','(51,11)'),('source60','source51'),('[4024,605,1667]','[4040,607,1667]'),
            ('pg6198-original4024-artifacts-v1','pg6274-original4040-artifacts-v1'),
            ('PG6198-original4024-v1','PG6274-original4040-v1'),
            ('PG6272-current4024-cases','PG6272-current4040-cases')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<original4040 '+name+'>','exec'),scope)
    return scope


def new_case_identities(source):return definitions()['new_case_identities'](source)
def main():return definitions()['main']()


if __name__=='__main__':main()
