"""Current PG715 existing-only ADMIN, same actual55ac DONE and sealed736 full21."""
from pathlib import Path
import pg702_sources as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def current(raw):
    raw=previous.current(raw)
    pairs=(
        ('pg702','pg737'),('Pg702','Pg737'),('PG702','PG737'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
        ('PG682','PG715'),('pg682-release-v1','pg715-release-v1'),
        ('pg630-retention-factory-six-host-v1','pg713-expiry-six-host-v1'),
        ('076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480','74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'),
        ('pg701-completed-baseline-v1','pg736-completed-baseline-v1'),
        ('bde365dd6ec48fb6c59cd9f8a255cdf664be4a3246283825ba429bb59754038a','c69d13e43a14525d2e2ec894378e5fd1f6735574f1c63dadadb2306324936f0b'),
        ('==524)','==534)'),
        ('8633b77f-77dc-4a78-88b4-41165f159b43','55ac70e7-0180-4c32-8c91-5a379ebedf24'),
        ('2026-10-09T00:43:10.150245Z','2026-10-09T03:00:51.014287Z'),
        ('c6815985-26c5-4f5f-aed0-abc81fa8f71e','ab8895ca-4fb1-440d-b174-bc9f1f27505a'),
        ('2026-10-09T01:12:17.452418Z','2026-10-09T03:30:40.608594Z'),
        ('6b3dd954959c43c1bbac2164ec9d0c6b','2aff8ecf3b7d4d15b24a8af0f73a8745'),
        ("JOB='122726'","JOB='132812'"),('START=119288459330','START=127549297774'),
        ('==121040711116','==129343844863'),('pg696-native-stop-v1','pg728-native-stop-v1'),
    )
    return replace(raw,tuple((a,b)for a,b in pairs if a in raw))


def java():return current(previous.old.java())
def receipt():return current(previous.old.receipt())
def join():return current(previous.old.join())
def argument_test():return current(previous.old.argument_test())
def native():return current(previous.old.native())
def compile_script():return current(previous.old.compile_script())


def refs():
    raw=current(previous.old.refs())
    check="""  require(set(baseline['currentBootstrapProofs'])=={'pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1','pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1'})
  for directory,value in baseline['currentBootstrapProofs'].items():
   require(tree(pathlib.Path('/var/lib/pgpt-s1-preservation')/directory)==value)
"""
    return replace(raw,((" def verify_fixed_fields():\n"," def verify_fixed_fields():\n"+check),))


def python_files():
    values={'pg737_bootstrap_existing.py':refs(),'pg737_parent_receipt.py':receipt(),'pg737_parent_join.py':join()}
    for name in ('pg535_bootstrap_contract.py','pg536_bootstrap_execution_contract.py','pg529_dependency_graph.py',
                 'pg556_parent_receipt.py','pg559_terminal_refs.py','pg457_stable_actor.py','pg570_directory_identity.py'):
        values[name]=(R/name).read_text()
    return values
