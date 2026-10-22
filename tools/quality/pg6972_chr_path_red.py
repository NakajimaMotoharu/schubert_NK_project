"""BUG1640 red: only two new contract tests; every common Main remains original."""
import subprocess
import pg6966_chr_adapter_host as host
import pg6968_chr_adapter_host_v2 as selected

TEST = 'program/characterization/tests/java/dev/codex/schubert/characterization/GateCliTest.java'


def main():
    source = subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip()
    changed = subprocess.check_output(['git','diff','--name-status',host.SOURCE,source,'--','src','pom.xml','.mvn','mvnw','program/characterization'],
                                      cwd=host.ROOT,text=True).splitlines()
    host.require(changed == ['M\t'+TEST], 'test-only RED; all four Main/old oracle/current baseline untouched')
    old = subprocess.check_output(['git','show',host.SOURCE+':'+TEST],cwd=host.ROOT,text=True)
    now = (host.ROOT/TEST).read_text()
    host.require(old.count('void ') + 2 == now.count('void '), 'two new negative contract methods only')
    start = now.index('\n  @Test\n  @org.junit.jupiter.api.DisplayName("PT-CHR-PATH-001')
    end = now.index('\n  @Test\n  void reportMapsEveryGateAndRejectsSecretCanaries()',start)
    host.require(now[:start]+now[end:] == old, 'all old test/oracle bytes untouched, not just method count')
    selected.validate()
    host.main(host.W/'pg6972-chr-path-red-v1',selected.FILES,source)


if __name__ == '__main__':
    main()
