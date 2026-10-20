"""Only original4027 XML/Jars/counters; never invokes PT or actual runtime."""
import inspect
import pg6198_original4024_artifacts as prior
from pg6208_keeper_faults_qualification import original_source

OLD='4e3a75a5e43518904d6dcb45f47b9ecf90327257'


def definitions():
    scope={**vars(prior),'OLD':OLD,'original_source':original_source}
    for name in ('new_case_identities','main'):
        raw=inspect.getsource(getattr(prior,name))
        replacements=(('!=36','!=3'),('exact36','exact3'),('13','7'),
            ('pg6196-management-ownership-six-v1','pg6212-keeper-ownership-six-v1'),
            ('PG6196-six-v1','PG6212-six-v1'),('PG6196','PG6212'),
            ('PG6118-current3988-cases','PG6196-current4024-cases'),
            ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23','4a89ed9b4c4f065c936b102a5740306be738ad8c55eef690e7c7484556a401d1'),
            ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47','50f54e2954bf8d8e248d7ec652fbb2e1920cd597ae9f71841161b5028eb99d7b'),
            ('PG6193-management-primary-qualification-v2','PG6208-keeper-faults-qualification-v1'),
            ('pg6193-management-primary-qualification-v2','pg6208-keeper-faults-qualification-v1'),
            ('(60,20)','(63,20)'),('source60','source63'),('[4024,605,1667]','[4027,605,1667]'),
            ('pg6198-original4024-artifacts-v1','pg6214-original4027-artifacts-v1'),
            ('PG6198-original4024-v1','PG6214-original4027-v1'),
            ('PG6212-current4024-cases','PG6212-current4027-cases'))
        # Do not replace arbitrary digits inside immutable hashes or identifiers.
        for before,after in replacements:
            if before=='13':
                raw=raw.replace('len(owners)!=13','len(owners)!=7').replace('exact13','exact7')
            else:raw=raw.replace(before,after)
        exec(compile(raw,'<original4027 '+name+'>','exec'),scope)
    return scope


def new_case_identities(source):return definitions()['new_case_identities'](source)
def main():return definitions()['main']()


if __name__=='__main__':main()
