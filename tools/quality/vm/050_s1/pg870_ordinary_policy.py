"""SSC242: signed default noargs plus unchanged fixed PT agent, never resume DONE."""
def ordinary_argv(base,native):
    if not isinstance(base,bytes)or not isinstance(native,bytes):raise ValueError('ordinary declaration refused')
    starts=[line.removeprefix(b'ExecStart=')for line in base.splitlines()if line.startswith(b'ExecStart=')]
    if len(starts)!=1 or not starts[0].startswith(b'/usr/bin/java ')or not starts[0].endswith(b' dev.codex.schubert.nk.batch.file.MorningProcessMain')or b'--resume'in starts[0]or b'-javaagent'in starts[0]:raise ValueError('ordinary declaration refused')
    agent=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false '
    argv=starts[0].replace(b'/usr/bin/java ',agent,1)
    expected=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
    if native!=expected:raise ValueError('fixed native declaration refused')
    return argv.decode('ascii')
