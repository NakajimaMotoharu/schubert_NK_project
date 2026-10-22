"""BUG1639: scope format to the actual common four Main/five host Tests only."""
import pg6966_chr_adapter_host as p

MAIN = ('ArtifactComparator','GateCli','GateContractValidator','TargetAdapter')
FILES = tuple('src/main/java/dev/codex/schubert/characterization/'+s+'.java' for s in MAIN) + tuple(
    'tests/java/dev/codex/schubert/characterization/'+s+'.java' for s in p.SELECTED)


def validate():
    expected = {'src/main/java/dev/codex/schubert/characterization/'+s+'.java' for s in MAIN}
    expected.update('tests/java/dev/codex/schubert/characterization/'+s+'.java' for s in p.SELECTED)
    p.require(set(FILES) == expected and len(FILES) == 9, 'exact actual four Main/five Test format scope')
    p.require(not any('*' in v or 'Native' in v or 'CurrentCharacterization' in v for v in FILES),
              'no wildcard widening or unknown native test added')


if __name__ == '__main__':
    validate()
    p.main(p.W/'pg6968-chr-adapter-host-v2',FILES)
