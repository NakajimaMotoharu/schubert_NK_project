"""BUG1640 same-oracle GREEN: one common Main plus one new source-run guard test."""
import json
import subprocess

import pg6966_chr_adapter_host as host
import pg6968_chr_adapter_host_v2 as selected
from pg6972_chr_path_red import TEST

MAIN = 'program/characterization/src/main/java/dev/codex/schubert/characterization/GateCli.java'


def main():
    red = host.BASE/'PG6974-chr-path-red-original-v1/manifest.json'
    host.require(host.sha(red) == '909ddd0b190c4a552b88b2710e5b78e69799f82aa1aba4b65c4a2887d159b3d9', 'genuine original red two failures')
    red_source = json.loads(red.read_bytes())['source']
    source = subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip()
    changed = subprocess.check_output(['git','diff','--name-status',host.SOURCE,source,'--',
                                      'src','pom.xml','.mvn','mvnw','program/characterization'],cwd=host.ROOT,text=True).splitlines()
    host.require(set(changed) == {'M\t'+MAIN,'M\t'+TEST}, 'only targeted common Main/Test, Production six untouched')
    red_text = subprocess.check_output(['git','show',red_source+':'+TEST],cwd=host.ROOT,text=True)
    now = (host.ROOT/TEST).read_text()
    marker = '\n  @Test\n  @org.junit.jupiter.api.DisplayName("PT-CHR-PATH-003'
    start = now.index(marker)
    end = now.index('\n  @Test\n  void baselinePromotionIsImmutableCommitBoundAndSymlinkSafe()',start)
    host.require(now[:start]+now[end:] == red_text, 'two red assertions and all old oracle bytes unchanged')
    selected.validate()
    host.main(host.W/'pg6976-chr-path-green-v1',selected.FILES,source)


if __name__ == '__main__':
    main()
