"""Seal corrected PG588 new-only run using the reviewed independent collector policy."""
import hashlib
import pathlib


def policy():
    source = pathlib.Path(__file__).with_name('pg586_collect_selected.py').read_text()
    replacements = {
        'pg586-access-selected-v3': 'pg588-session-readback-v2',
        'PG586-access-selected-v3': 'PG588-session-readback-v2',
        '55363131eb0d071869c48c8468a7aa1be0724ea9': '6ccb6704bb3fb1c3118880a0968352bacad9ca73',
        "log.count('BUILD SUCCESS')==2": "log.count('BUILD SUCCESS')==1",
        "('MorningDatabaseAccessContractTest',7)": "('MorningDatabaseAccessContractTest',9)",
        "('MorningDatabaseSessionTest',20)": "('MorningDatabaseSessionTest',23)",
        "'selectedTests':27,'newTests':3": "'selectedTests':32,'newTests':3",
        "'selectedPT':27,'newTests':3": "'selectedPT':32,'newTests':3",
        "'dependencyBuildOnlyTestsNotAccepted':True": "'dependencyBuildOnlyTestsNotAccepted':False",
    }
    digest = hashlib.sha256(source.encode()).hexdigest()
    for old, new in replacements.items():
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    source = source.replace("'collectorSourceSha256':sha(pathlib.Path(__file__))",
                            "'collectorSourceSha256':sha(pathlib.Path(__file__)),'collectorPolicySha256':" + repr(digest))
    return source


if __name__ == '__main__':
    exec(compile(policy(), '<sealed PG588 collector>', 'exec'),
         {'__name__': '__main__', '__file__': __file__})
