"""BUG1640 same-green source static; preserve original RED and old raw findings."""
import json
import subprocess

import pg6970_chr_common_static as static
import pg6966_chr_adapter_host as host


if __name__ == '__main__':
    prior = host.W/'pg6976-chr-path-green-v1'
    begin = json.loads((prior/'begin.safe.json').read_bytes())
    subprocess.run(['git','diff','--exit-code',begin['source'],'--','src','pom.xml','.mvn','mvnw','program/characterization'],
                   cwd=host.ROOT,check=True,stdout=subprocess.DEVNULL)
    static.main(prior,host.W/'pg6978-chr-path-static-v1')
