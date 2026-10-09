"""Current 9bd signed existing-only ADMIN; old sources are inert templates.

BOOT702001: fresh current21 seal, genuine parent and one immutable new tool slot.
Historical dependencies retain their actual names; no old operation is invoked.
"""
from pathlib import Path
import pg664_sources as old
from pg662_sources import replace

R = Path(__file__).resolve().parent


def current(raw):
    pairs = (
        ('pg664', 'pg702'), ('Pg664', 'Pg702'), ('PG664', 'PG702'),
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5', '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
        ('PG631', 'PG682'), ('pg631-release-v1', 'pg682-release-v1'),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe', '076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
        ('pg661-completed-baseline-v1', 'pg701-completed-baseline-v1'),
        ('8963796af5d95b30f01169d79bed2d6055782988af497dd09903b8f73a8af4d8', 'bde365dd6ec48fb6c59cd9f8a255cdf664be4a3246283825ba429bb59754038a'),
        ('len(baseline)==20', 'len(baseline)==21'), ('==514)', '==524)'),
        ('601297d0-a8ba-47da-852b-0ffeae409965', '8633b77f-77dc-4a78-88b4-41165f159b43'),
        ('2026-10-08T21:33:23.332578Z', '2026-10-09T00:43:10.150245Z'),
        ('ad15ac4a-8d8e-4970-bcb3-2e000050ce77', 'c6815985-26c5-4f5f-aed0-abc81fa8f71e'),
        ('2026-10-08T22:03:10.738020Z', '2026-10-09T01:12:17.452418Z'),
        ('095f6d1d7f8442b7b2b44ae59a4314f5', '6b3dd954959c43c1bbac2164ec9d0c6b'),
        ("JOB='111752'", "JOB='122726'"), ('START=107901545407', 'START=119288459330'),
        ('==109694780700', '==121040711116'), ('pg655-native-stop-v1', 'pg696-native-stop-v1'),
    )
    return replace(raw, tuple((a, b) for a, b in pairs if a in raw))


def java(): return current(old.java())
def receipt(): return current(old.receipt())
def join(): return current(old.join())
def argument_test(): return current(old.argument_test())
def native(): return current(old.native())
def compile_script(): return current(old.compile_script())


def refs():
    raw = current(old.refs())
    # These are preserved old proofs, NOT new output directories. Insert after
    # rebinding so pg664 literals can never become authority for new tools.
    check = """  require(set(baseline['currentBootstrapProofs'])=={'pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1'})
  for directory,value in baseline['currentBootstrapProofs'].items():
   require(tree(pathlib.Path('/var/lib/pgpt-s1-preservation')/directory)==value)
"""
    return replace(raw, ((" def verify_fixed_fields():\n", " def verify_fixed_fields():\n" + check),))


def python_files():
    values = {'pg702_bootstrap_existing.py': refs(), 'pg702_parent_receipt.py': receipt(),
              'pg702_parent_join.py': join()}
    for name in ('pg535_bootstrap_contract.py', 'pg536_bootstrap_execution_contract.py',
                 'pg529_dependency_graph.py', 'pg556_parent_receipt.py', 'pg559_terminal_refs.py',
                 'pg457_stable_actor.py', 'pg570_directory_identity.py'):
        values[name] = (R / name).read_text()
    return values
