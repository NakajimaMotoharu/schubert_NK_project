"""PG-D400 strict single Morning retention factory class delta, no authority."""
MODULES=('protocol','storage','bootstrap','api','web','batch')
CHANGED=frozenset({'dev/codex/schubert/nk/batch/file/MorningBackupRetention.class'})


def verify_delta(old,candidate):
    if type(old)is not dict or type(candidate)is not dict or set(old)!=set(MODULES)or set(candidate)!=set(MODULES):raise ValueError('candidate module inventory')
    count=0
    for module in MODULES:
        before,after=old[module],candidate[module]
        if type(before)is not dict or type(after)is not dict or not before or set(before)!=set(after):raise ValueError('candidate class inventory')
        for rows in (before,after):
            if any(type(n)is not str or not n.endswith('.class')or type(h)is not str or len(h)!=64 or set(h)-set('0123456789abcdef')for n,h in rows.items()):raise ValueError('candidate class digest')
        changed={n for n in before if before[n]!=after[n]}
        if changed!=(CHANGED if module=='batch'else set()):raise ValueError('candidate class delta')
        count+=len(after)
    return count
