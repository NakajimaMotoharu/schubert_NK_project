"""Conservative exact-candidate/public-blob proof; shapes and nearby values never suffice."""
import re


def classify(text, rule, first, end, public_hashes):
    if type(first) is not int or type(end) is not int or not 1 <= first <= end:
        raise ValueError('explicit finding range required')
    lines=text.splitlines(keepends=True)
    if end>len(lines):
        raise ValueError('finding outside public input')
    low=max(0,first-2);high=min(len(lines),end+1)
    window=''.join(lines[low:high])
    candidates=set()
    for match in re.compile(rule['regex'],re.ASCII).finditer(window):
        start=low+window[:match.start(1)].count('\n')+1
        finish=low+window[:match.end(1)].count('\n')+1
        if first<=start<=finish<=end:
            candidates.add(match.group(1))
    if not candidates:
        return dict(disposition='UNCLASSIFIED',reason='EXACT_CAPTURE_NOT_BOUND_TO_FINDING_RANGE')
    if len(candidates)!=1:
        return dict(disposition='UNCLASSIFIED',reason='MULTIPLE_DISTINCT_CAPTURES')
    candidate=next(iter(candidates))
    if candidate not in public_hashes:
        return dict(disposition='UNCLASSIFIED',reason='EXACT_CAPTURE_NOT_A_PROVEN_PUBLIC_BLOB_HASH')
    return dict(disposition='FALSE_POSITIVE_PUBLIC_BLOB_SHA256',
                reason='EXACT_RULE_CAPTURE_EQUALS_INDEPENDENTLY_HASHED_PUBLIC_GIT_BLOB',
                publicArtifactProof=public_hashes[candidate])
