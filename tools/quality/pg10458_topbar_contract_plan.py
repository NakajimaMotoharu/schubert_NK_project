"""Two independent pure view assertions, no fixture or production change."""
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from pg10398_role_view_preflight import canonical
from pg10130_uid_oracle_preflight import tokens

BASE_SOURCE = '65bcd70a1dec722bd70be03468d9343142a7e789'
TARGET = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioHierarchyViewModelTest.java'
OUT = data.BASE/'PG10458-topbar-contract-plan-v1'
ADDITIONS = (
    'assertThrows(NullPointerException.class, () -> TopBarViewModel.from(null));',
    'assertEquals("TopBarViewModel[REDACTED]", a.getTopBar().toString());')


def remove_additions(text):
    values = tokens(text)
    for statement in ADDITIONS:
        needle = tokens(statement)
        starts = [i for i in range(len(values)) if values[i:i+len(needle)] == needle]
        if len(starts) != 1:
            raise ValueError('one exact independent TopBar assertion required')
        i, = starts
        values[i:i+len(needle)] = []
    return ' '.join(values)


def check(text,previous):
    if canonical(remove_additions(text)) != canonical(previous):
        raise ValueError('only two independent assertions allowed')


def main():
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10434-pure-view-six-compile-v1/manifest.json',
        'd202203f8377e778f1c8b43af42cbad0e8a97614cb0b82e7e97b3143652b5f7e')
    assert normal['source'] == BASE_SOURCE and normal['actualExit'] == 0
    previous = subprocess.check_output(['git','show',BASE_SOURCE+':'+TARGET],cwd=data.ROOT).decode()
    text = (data.ROOT/TARGET).read_text()
    check(text,previous)
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p != TARGET)
    negatives = []
    for label,damaged in [
        ('wrong-diagnostic',text.replace('"TopBarViewModel[REDACTED]"','"TopBarViewModel[VALUES]"')),
        ('missing-null',text.replace(ADDITIONS[0],'')),
        ('missing-diagnostic',text.replace(ADDITIONS[1],'')),
        ('wrong-null-contract',text.replace(ADDITIONS[0],ADDITIONS[0].replace('NullPointerException','IllegalArgumentException'))),
        ('missing-original-assertion',text.replace('assertEquals("GameListViewModel[REDACTED]", a.toString());',''))]:
        assert damaged != text
        try:
            check(damaged,previous)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid contract/source accepted')
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=None,baseSource=BASE_SOURCE,
        path=TARGET,beforeSha256=data.sha(previous.encode()),sha256=data.sha(text.encode()),
        addedIndependentAssertions=list(ADDITIONS),originalAllTokensAndAssertionsPreserved=True,
        actualOriginalAssertionInvocationCounts=None,metadataNegatives=negatives,
        productTestsExecuted=0,newTestIds=0,externalActions=0,newAccepted=0,formalUpdated=False,
        bug='BUG-1832',ykt='YKT-1583'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
