"""SSC251: recognize the one fixed exchanged-but-not-saved state, no authority."""
import copy
from pg1083_cold_publication_contract import CURRENT,OLD_LINK,verify,verify_retained


def partial(before,actual,epoch,begin,end):
    if type(actual)is not dict or CURRENT not in actual or type(actual[CURRENT])is not dict:
        raise ValueError('partial graph refused')
    stage=CURRENT+'/pg1088-current.part'
    if stage not in actual[CURRENT]:raise ValueError('fixed linked original absent')
    normalized=copy.deepcopy(actual)
    old=normalized[CURRENT].pop(stage)
    verify(before,normalized,'after',epoch,begin,end)
    if old.get('target')!=OLD_LINK:raise ValueError('linked original target refused')
    verify_retained(CURRENT+'/current',before[CURRENT][CURRENT+'/current'],old,'after',normalized,begin,end)
    return True
