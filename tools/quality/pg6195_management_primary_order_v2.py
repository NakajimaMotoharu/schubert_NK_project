"""Read original v2 JVM/source and exact fixed primary policy; no app invocation."""
import inspect
import pg6186_native_ownership_order as prior
from pg6193_management_primary_qualification_v2 import original_source
from pg6194_management_primary_order import normal_primary_policy


def runner_source():
    raw=inspect.getsource(prior.main)
    for before,after in (
        ('PG6184-unstarted-management-qualification-v1','PG6193-management-primary-qualification-v2'),
        ('pg6184-unstarted-management-qualification-v1','pg6193-management-primary-qualification-v2'),
        ('(59,20,1667)','(60,20,1667)'),
        ('pg6182-unstarted-management-selected-v1/source','pg6191-management-primary-selected-v2/source'),
        ('PG6186-native-ownership-order-v1','PG6195-management-primary-order-v2'),
        ('    value=dict(actualExit=0','    primary=normal_primary_policy(management)\n    value=dict(actualExit=0'),
        ('ownershipReviewed=True,\n','ownershipReviewed=True,normalPrimaryPolicy=primary,\n')):
        if raw.count(before)!=1:raise ValueError('one actual current-source JVM binding '+before)
        raw=raw.replace(before,after,1)
    compile(raw,'<v2 current JVM/source>','exec')
    return raw


def main():
    scope={**vars(prior),'original_source':original_source,'normal_primary_policy':normal_primary_policy}
    exec(compile(runner_source(),'<v2 current60 proof>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
