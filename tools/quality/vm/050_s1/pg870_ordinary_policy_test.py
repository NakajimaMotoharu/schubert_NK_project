"""Independent literal ordinary argv/agent declaration and unknown/null negatives."""
from pg870_ordinary_policy import ordinary_argv
base=b'[Service]\nExecStart=/usr/bin/java -cp literal dev.codex.schubert.nk.batch.file.MorningProcessMain\n'
argv=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false -cp literal dev.codex.schubert.nk.batch.file.MorningProcessMain'
native=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
assert ordinary_argv(base,native)==argv.decode('ascii')
for a,b in [(None,native),(base,None),(b'',native),(base+base,native),(base.replace(b'MorningProcessMain',b'MorningProcessMain --resume literal'),native),(base.replace(b'/usr/bin/java ',b'/usr/bin/java -javaagent:foreign '),native),(base,native.replace(b'MorningProcessMain',b'MorningProcessMain --resume literal')),(base,native+b'Environment=foreign\n')]:
    caught=False
    try:ordinary_argv(a,b)
    except ValueError:caught=True
    assert caught
print('ORD870001 literal noargs/native declaration +8 unknown/null/resume negatives PASS; mutation0')
