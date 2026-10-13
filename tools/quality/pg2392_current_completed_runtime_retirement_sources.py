"""Current actual completed-run fragment retirement; reuse proven held-FD normal scope engine."""
import inspect
import pg2050_fresh_completed_runtime_retirement_sources as previous
from pg2374_current_resume_owned_sources import sources as stop_sources,SOURCE

TOOLS='pg2392-current-completed-runtime-retirement-tools-v1'
BASE='/var/lib/pgpt-s1-preservation/pg2374-native-stop-v1/after.private.json'
SHA='3e53dda6fb86861684601f9d0c2a9473be90ca0832939dc22dee8dbbcc14cfe2'


def contract_source():
    raw=previous.contract_source().replace('zz-pg1980-once-resume.conf','zz-pg2316-once-resume.conf').replace('4148e3e8-f107-431a-ab27-d6e6d1f1772e','91f5484b-9702-4c7c-97f3-dd5110a853f9').replace('78f1488383951e0fc2716bcf63ab41f75c64e975440e7f5e079fd6129f8612ec','888ee8561e9c25da302470c2561cdbf65cbf10cdebf668f7196f27b485bc5035')
    compile(raw,'<current exact644byte retirement contract>','exec');return raw


def sources():
    raw=inspect.getsource(previous.sources)
    for a,z in [('pg2040-fresh-normal-warning-terminal-post-v1','pg2380-current-resume-owned-post-v1'),('2050','2392'),('2030','2374'),('pg2025-fresh-resume-full-live-seal-v1','pg2368-current-resume-full-seal-v1'),('8a7d42b110a047d60a3b10d948cf51731dab4b37b59d85052332acaa42942788','79c934ae247523f5914c4e8964b2b649ed44b884619210531115619d3cab04fc')]:raw=raw.replace(a,z)
    ns={**previous.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'BASE':BASE,'SHA':SHA,'stop_sources':stop_sources,'contract_source':contract_source}
    exec(compile(raw,'<current exact completed runtime graph>','exec'),ns)
    values=ns['sources']()
    return {n:s.replace('pg2392-current-resume-owned-stop-tools-v1',TOOLS)for n,s in values.items()}
