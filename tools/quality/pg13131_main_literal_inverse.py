"""Full token inverse: only one year threshold and four exact fixed-symbol literals."""
from public_java_digest_provenance import LEX


def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def inverse(path,old,new):
    if path.endswith('/TransferCleanup.java'):
        declaration = 'private static final int MINIMUM_SUPPORTED_DATE_YEAR = 1;'
        assert new.count(declaration) == 1 and new.count('MINIMUM_SUPPORTED_DATE_YEAR') == 2
        assert new.count('date.getYear() < MINIMUM_SUPPORTED_DATE_YEAR') == 1
        restored = new.replace(declaration,'').replace('MINIMUM_SUPPORTED_DATE_YEAR','1')
        references = 1
    else:
        assert path.endswith('/LinuxSystemdSession.java')
        declaration = 'private static final String LIBC_FREE_SYMBOL = "free";'
        assert new.count(declaration) == 1 and new.count('LIBC_FREE_SYMBOL') == 5 and old.count('"free"') == 4
        restored = new.replace(declaration,'').replace('LIBC_FREE_SYMBOL','"free"')
        references = 4
    assert tokens(restored) == tokens(old)
    return dict(originalTokens=len(tokens(old)),privateConstantsAdded=1,referencesReplaced=references,wholeSourceTokensRecovered=True)


def negative(path,old,new):
    if path.endswith('/TransferCleanup.java'):
        values = [new.replace('MINIMUM_SUPPORTED_DATE_YEAR = 1','MINIMUM_SUPPORTED_DATE_YEAR = 0',1),
            new.replace('MINIMUM_SUPPORTED_DATE_YEAR = 1','MINIMUM_SUPPORTED_DATE_YEAR = 2',1),
            new.replace('date.getYear() < MINIMUM_SUPPORTED_DATE_YEAR','date.getYear() <= MINIMUM_SUPPORTED_DATE_YEAR',1),
            new.replace('guard.verify();','',1),new.replace('counts.retained();','counts.failed();',1)]
    else:
        values = [new.replace('LIBC_FREE_SYMBOL = "free"','LIBC_FREE_SYMBOL = "abort"',1),
            new.replace('releaseOutput(1, LIBC_FREE_SYMBOL)','releaseOutput(2, LIBC_FREE_SYMBOL)',1),
            new.replace('"sd_bus_new"','"sd_bus_new_bad"',1),
            new.replace('code < 0','code <= 0',1),new.replace('4096','4095',1)]
    values.append(new.rstrip()[:-1])
    for value in values:
        assert value != new
        try:inverse(path,old,value)
        except AssertionError:pass
        else:raise AssertionError('non-equivalent Main mutation accepted')
    return len(values)
