"""SSC231 current completed-source existing ADMIN route; old tools are templates only.

No operation runs on import. Generated sources are pinned in a new immutable
tool directory, separately verified before the one durable execute reservation.
"""
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = '36fe7a0b938489d61d17d49c1c30a6fbbef699d5'
BOM = '57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'
BASELINE = '8963796af5d95b30f01169d79bed2d6055782988af497dd09903b8f73a8af4d8'


def replace(raw, pairs):
    for old, new in pairs:
        if old not in raw:
            raise ValueError('current bootstrap source template changed: '+old)
        raw = raw.replace(old, new)
    return raw


def current(raw):
    return replace(raw, (
        ('pg570', 'pg662'), ('Pg570', 'Pg662'), ('PG570', 'PG662'),
        ('PG548', 'PG631'),
        ('969d8ded10c0bf5841d9e3a5c531e922caf4a24a', SOURCE),
    ))


def java():
    return replace(current((R/'Pg570BootstrapExisting.java').read_text()), (
        ('b7e73994-b951-4696-bdd1-cfbc8a10e734', '601297d0-a8ba-47da-852b-0ffeae409965'),
        ('2026-10-08T04:03:00.714124Z', '2026-10-08T21:33:23.332578Z'),
        ('12f1af04-180e-405c-8738-853bbd875443', 'ad15ac4a-8d8e-4970-bcb3-2e000050ce77'),
        ('2026-10-08T04:27:59.110604Z', '2026-10-08T22:03:10.738020Z'),
        ('a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b', BOM),
    ))


def receipt():
    return replace((R/'pg609_parent_receipt.py').read_text(), (
        ('5a1acaa0c35e484c979401e3b6dfb36a', '095f6d1d7f8442b7b2b44ae59a4314f5'),
        ("JOB='87863'", "JOB='111752'"), ('START=86264628081', 'START=107901545407'),
        ('3a53b979-fa01-47dd-92a6-7b26affcfb5c', '601297d0-a8ba-47da-852b-0ffeae409965'),
        ('2026-10-08T15:32:46.368375Z', '2026-10-08T21:33:23.332578Z'),
        ('970bbce1-6bba-4db0-ace1-680ee7dfde92', 'ad15ac4a-8d8e-4970-bcb3-2e000050ce77'),
    ))


def join():
    return replace((R/'pg569_parent_join.py').read_text(), (
        ('from pg556_parent_receipt import completed', 'from pg662_parent_receipt import completed'),
    ))


def refs():
    raw = replace((R/'pg570_bootstrap_existing.py').read_text(), (
        ('pg570', 'pg662'), ('Pg570', 'Pg662'), ('PG570', 'PG662'),
        ('pg569_parent_join', 'pg662_parent_join'),
        ('pg662_directory_identity', 'pg570_directory_identity'),
        ('pg559-terminal-readback-v2/after.private.json', 'pg661-completed-baseline-v1/before.private.json'),
        ('23263d00948c5df5aca9aa4741a4d0266d9b8d20ebe400c7d180f89bb9ce6677', BASELINE),
        ("len(baseline['units'])==10", "len(baseline)==20 and len(baseline['units'])==10"),
        ("==472)", "==514)"),
        ('075ad6644b284056a6cccf7af252519b', '095f6d1d7f8442b7b2b44ae59a4314f5'),
        ('12f1af04-180e-405c-8738-853bbd875443.done', 'ad15ac4a-8d8e-4970-bcb3-2e000050ce77.done'),
        ('==46382089521', '==109694780700'),
        ('pg557-native-stop-v1', 'pg655-native-stop-v1'),
        ('0.1.0-PG548', '0.1.0-PG631'),
        ("bytearray(b'pgpt_bootstrap_570_existing')", "bytearray(('pgpt_'+secrets.token_hex(16)).encode('ascii'))"),
        ("return {'units':current", "verify_fixed_fields()\n  return {'units':current"),
    ))
    insert = """ def verify_fixed_fields():
  require(baseline['runtime']is None and not list(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir()))
  for key,directory in (('bootstrapOldProofs','pg570-bootstrap-existing-v1'),('bootstrapTools','pg570-bootstrap-tools-v1')):
   require(tree(pathlib.Path('/var/lib/pgpt-s1-preservation')/directory)==baseline[key])
  require(show('caddy.service',{'ExecStartPre'})['ExecStartPre']==baseline['caddyPre'])
  for collection in ('unitFiles','pid1Stop'):
   for name,value in baseline[collection].items():
    path=name if collection=='unitFiles'else '/var/lib/pgpt-s1-preservation/pg655-native-stop-v1/'+name+'.stopped.private'
    raw=strict(pathlib.Path(path),value['metadata'][4]&0o777,33554432)
    require(metadata(pathlib.Path(path))==value['metadata']and hashlib.sha256(raw).hexdigest()==value['sha256'])
  path=pathlib.Path('/etc/schubert-nk/release-approval/current');value=baseline['approval']
  require(metadata(path)==value['metadata']and hashlib.sha256(path.read_bytes()).hexdigest()==value['sha256'])
  require(baseline['current']=='/opt/schubert-nk/releases/0.1.0-PG631')
"""
    return replace(raw, ((" def snapshot(present):", insert+" def snapshot(present):"),))


def argument_test():
    return replace((R/'Pg570BootstrapArgumentTest.java').read_text(), (
        ('Pg570', 'Pg662'), ('PG570', 'PG662'), ('SSC225', 'SSC231'),
    ))


def native():
    raw = replace((R/'pg570_bootstrap_native_v1.py').read_text(), (
        ('pg570', 'pg662'), ('Pg570', 'Pg662'), ('PG570', 'PG662'),
        ('0.1.0-PG548', '0.1.0-PG631'),
        ('969d8ded10c0bf5841d9e3a5c531e922caf4a24a', SOURCE),
        ("('pg569_parent_join_test.py', 'pg662_directory_identity_test.py',\n                 'pg662_bootstrap_contract_test.py')", "('pg662_sources_test.py', 'pg570_directory_identity_test.py', 'pg662_receipt_test.py')"),
        ('pg662_directory_identity.py', 'pg570_directory_identity.py'),
        ('pg556_parent_receipt.py', 'pg662_parent_receipt.py'),
        ('pg569_parent_join.py', 'pg662_parent_join.py'),
        ("files[name] = R / name", "files[name] = CLASSDIR / name if name in ('pg662_bootstrap_existing.py','pg662_parent_receipt.py','pg662_parent_join.py') else R / name"),
    ))
    return raw


def compile_script():
    return replace((R/'pg570_bootstrap_compile_v1.sh').read_text(), (
        ('pg570', 'pg662'), ('Pg570', 'Pg662'), ('PG570', 'PG662'),
        ('pg548-release-v1', 'pg631-release-v1'),
        ('tools/quality/vm/050_s1/Pg662BootstrapExisting.java tools/quality/vm/050_s1/Pg662BootstrapArgumentTest.java', '"$task_target/Pg662BootstrapExisting.java" "$task_target/Pg662BootstrapArgumentTest.java"'),
        ('mkdir -m 700 "$task_target"', '# new-only output directory created by pg662_compile.py'),
        ('test ! -e "$task_target"', 'test -d "$task_target"'),
        ('pg662_bootstrap_contract_test.py', 'pg662_sources_test.py'),
    ))
