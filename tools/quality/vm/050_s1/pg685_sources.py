"""SSC233 current completed21 binding; source generation only, never executes old tools."""
import hashlib
from pathlib import Path

R = Path(__file__).resolve().parent
OLD = '/opt/schubert-nk/releases/0.1.0-PG631'
NEXT = '/opt/schubert-nk/releases/0.1.0-PG682'
SOURCE = '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'
DIGEST = '076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'


def replace(raw, pairs):
    for old, new in pairs:
        assert old in raw, old
        raw = raw.replace(old, new)
    return raw


def bind(raw):
    pairs = (
        ('pg624', 'pg685'), ('Pg624', 'Pg685'), ('PG624', 'PG685'),
        ('0.1.0-PG600', '0.1.0-PG631'), ('0.1.0-PG621', '0.1.0-PG682'),
        ('72fb7440697ee1048a5c0145055dc1cc3c577914', SOURCE),
        ('23b14a44b10504172e030bbd6625926bf049fb5c', '36fe7a0b938489d61d17d49c1c30a6fbbef699d5'),
        ('4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e', DIGEST),
        ('a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f', '57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'),
        ('3a53b979-fa01-47dd-92a6-7b26affcfb5c', '601297d0-a8ba-47da-852b-0ffeae409965'),
        ('2026-10-08T15:32:46.368375Z', '2026-10-08T21:33:23.332578Z'),
        ('970bbce1-6bba-4db0-ace1-680ee7dfde92', 'ad15ac4a-8d8e-4970-bcb3-2e000050ce77'),
        ('2026-10-08T15:57:38.735146Z', '2026-10-08T22:03:10.738020Z'),
        ('5a1acaa0c35e484c979401e3b6dfb36a', '095f6d1d7f8442b7b2b44ae59a4314f5'),
        ('87863', '111752'), ('86264628081', '107901545407'),
        ('87761979588', '109694780700'),
    )
    # Not every file contains every profile literal; required deltas checked per generator.
    for old, new in pairs:
        if old in raw:
            raw = raw.replace(old, new)
    return raw


def java():
    raw = bind((R/'Pg624CompletedDeployment.java').read_text())
    return replace(raw, ((
        '"PG600","36fe7a0b938489d61d17d49c1c30a6fbbef699d5",OLD',
        '"PG631","36fe7a0b938489d61d17d49c1c30a6fbbef699d5",OLD'),
        ('"PG621",source,NEXT', '"PG682",source,NEXT')))


def receipt():
    return bind((R/'pg609_parent_receipt.py').read_text())


def contract():
    raw = bind((R/'pg624_completed_contract.py').read_text())
    return replace(raw, (('caddyPre\'.split()', "caddyPre namespace currentBootstrapProofs'.split()"),))


def refs():
    raw = bind((R/'pg624_completed_refs.py').read_text())
    pairs = (
        ('pg611-native-stop-v1/after.private.json', 'pg684-completed-baseline-v2/before.private.json'),
        ('a7e90f2973f966def39d473f09274383bc866ad37d98b73c96658ece0a09c849', 'c039e70561fd7e5bab3ecf5ce204462d8415f4022d13793711c338a64d2f663d'),
        ("==492", "==514"), ("baseline['pid1']", "baseline['parentPid1']"),
        ('pg611-native-stop-v1', 'pg655-native-stop-v1'),
        ('pg611_parent_receipt.py', 'pg685_parent_receipt.py'),
        ('29ea92cd6befc7fd26e1ed23b8785bc7ce616d0cc36247cdb0b2f30c83564676', hashlib.sha256(receipt().encode()).hexdigest()),
        ("value['caddyPre']=show('caddy.service',{'ExecStartPre'})['ExecStartPre']",
         "value['caddyPre']=show('caddy.service',{'ExecStartPre'})['ExecStartPre']\n        namespace={**{n:pathlib.Path('/run/schubert-nk')/n for n in ('backup-request','cleanup-request','expiry-request')},'runtime-parent':pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')}\n        value['namespace']={n:{'metadata':metadata(p),'entries':sorted(c.name for c in p.iterdir()),'xattrs':os.listxattr(p)}for n,p in namespace.items()}\n        value['currentBootstrapProofs']={n:tree(BASE/n)for n in ('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1')}\n        require(set(value)==set(baseline)and len(value)==21)"),
    )
    return replace(raw, pairs)
