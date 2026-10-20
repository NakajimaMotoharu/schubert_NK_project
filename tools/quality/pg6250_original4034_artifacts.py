"""Collect only the original4034 whole XML/Jars/counters; never restart PT or actual runtime."""
import inspect
import pg6198_original4024_artifacts as prior
from pg6248_normal_phase_qualification import original_source

OLD='55109c74737208f906b69c04cd0931b466d2fadd'


def definitions():
    scope={**vars(prior),'OLD':OLD,'original_source':original_source}
    for name in ('new_case_identities','main'):
        raw=inspect.getsource(getattr(prior,name))
        for before,after in (
            ('!=36','!=7'),('exact36','exact7'),('len(owners)!=13','len(owners)!=10'),('exact13','exact10'),
            ('pg6196-management-ownership-six-v1','pg6244-confirmed-rollback-six-v1'),
            ('PG6196-six-v1','PG6244-six-v1'),('PG6196','PG6244'),
            ('PG6118-current3988-cases','PG6212-current4027-cases'),
            ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23','477bacaf70d4ad8dfe7310af0f85304d1a9fdd42e7f09db31afbbdd83a603166'),
            ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47','13e042309e312ee779e67a81a5866f6448138604355b2fccea764b6e914dbb30'),
            ('PG6193-management-primary-qualification-v2','PG6248-normal-phase-qualification-v1'),
            ('pg6193-management-primary-qualification-v2','pg6248-normal-phase-qualification-v1'),
            ('(60,20)','(113,28)'),('source60','source113'),('[4024,605,1667]','[4034,606,1667]'),
            ('pg6198-original4024-artifacts-v1','pg6250-original4034-artifacts-v1'),
            ('PG6198-original4024-v1','PG6250-original4034-v1'),
            ('PG6244-current4024-cases','PG6244-current4034-cases')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<original4034 '+name+'>','exec'),scope)
    return scope


def new_case_identities(source):return definitions()['new_case_identities'](source)
def main():return definitions()['main']()


if __name__=='__main__':main()
