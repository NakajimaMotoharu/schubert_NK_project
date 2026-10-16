"""SS342 fixed ordinary pool bounds; ownership/TCP proofs remain mandatory in callers."""
ROLES={'schubert_app':('schubert-nk-api.service',2,8),
       'schubert_web_session':('schubert-nk-web.service',1,2)}


def counts_valid(counts,completed,owned_count,total):
    if type(counts)is not dict or set(counts)!=set(ROLES)or type(completed)is not set or not completed<={v[0]for v in ROLES.values()}:
        raise ValueError('fixed two-role pool shape required')
    if type(owned_count)is not int or owned_count not in (0,1)or type(total)is not int:
        raise ValueError('separate owned connection count required')
    if any(type(n)is not int or n<0 for n in counts.values()):raise ValueError('nonnegative pool counts required')
    if total!=sum(counts.values())+owned_count:return False
    return all((counts[role]==0 if unit in completed else lo<=counts[role]<=hi)for role,(unit,lo,hi)in ROLES.items())
