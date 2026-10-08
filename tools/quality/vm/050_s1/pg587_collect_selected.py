"""Reuse independent PG586 collector policy with exact sealed run substitutions."""
import pathlib
import hashlib


def main():
    source=pathlib.Path(__file__).with_name('pg586_collect_selected.py').read_text()
    replacements={
        'pg586-access-selected-v3':'pg587-access-returns-v1',
        'PG586-access-selected-v3':'PG587-access-returns-v1',
        '55363131eb0d071869c48c8468a7aa1be0724ea9':'5dfc332d2467765fea3828b61f2dfd5486f19511',
        "log.count('BUILD SUCCESS')==2":"log.count('BUILD SUCCESS')==1",
        "('MorningDatabaseAccessContractTest',7)":"('MorningDatabaseAccessContractTest',9)",
        "'selectedTests':27,'newTests':3":"'selectedTests':29,'newTests':2",
        "'selectedPT':27,'newTests':3":"'selectedPT':29,'newTests':2",
        "'dependencyBuildOnlyTestsNotAccepted':True":"'dependencyBuildOnlyTestsNotAccepted':False",
        "result={'actualExit':0":"assert all(access_counts[k]['missed']==0 and access_counts[k]['covered']>0 for k in ('LINE','METHOD','CLASS','BRANCH'))\n    result={'actualExit':0",
    }
    policy_sha=hashlib.sha256(source.encode()).hexdigest()
    for old,new in replacements.items():
        assert source.count(old)==1
        source=source.replace(old,new)
    source=source.replace("'collectorSourceSha256':sha(pathlib.Path(__file__))", "'collectorSourceSha256':sha(pathlib.Path(__file__)),'collectorPolicySha256':"+repr(policy_sha))
    exec(compile(source,'<sealed PG587 collector>','exec'),{'__name__':'__main__','__file__':__file__})


if __name__=='__main__':main()
