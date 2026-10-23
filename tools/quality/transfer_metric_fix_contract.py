"""BUG1657: only the nine explicit private-field declaration/assignment/read tokens may differ."""
RENAMES=(
 (b'private final Counts part;',b'private final Counts partCounts;'),
 (b'private final Counts ready;',b'private final Counts readyCounts;'),
 (b'this.part = Objects.requireNonNull(part, "part counts");',b'partCounts = Objects.requireNonNull(part, "part counts");'),
 (b'this.ready = Objects.requireNonNull(ready, "ready counts");',b'readyCounts = Objects.requireNonNull(ready, "ready counts");'),
 (b'return part;',b'return partCounts;'),(b'return ready;',b'return readyCounts;'),
 (b'private final String label;',b'private final String suffixLabel;'),
 (b'this.label = label;',b'suffixLabel = label;'),(b'return label;',b'return suffixLabel;'))

def verify_private_rename(before,after):
    expected=before
    for old,new in RENAMES:
        if expected.count(old)!=1:raise ValueError('each declared original private token occurs once')
        expected=expected.replace(old,new)
    if expected!=after:raise ValueError('no public API/oracle/other source change beyond nine private tokens')
    return dict(privateFieldRenames=3,exactTokenReplacements=len(RENAMES),allOtherBytesUnchanged=True)
