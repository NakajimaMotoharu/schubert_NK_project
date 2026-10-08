"""Literal SSC230 before/after delta, never Production-generated expected."""
import copy
import hashlib
import unittest
from pg647_retirement_contract import changed_only

MORNING = 'schubert-nk-morning-controller.service'
NATIVE = '/etc/systemd/system/'+MORNING+'.d/pg477-native-coverage.conf'
TARGET = '/run/systemd/system/'+MORNING+'.d/pg635-once-resume.conf'
RUN = 'e49243d5-de84-4714-8612-6912ddc17e9e'
UNITS = ('artemis.service', 'caddy.service', 'schubert-nk-api.service', 'schubert-nk-backup.service',
         'schubert-nk-cleanup.service', 'schubert-nk-expiry-cleanup.service', 'schubert-nk-web.service',
         'schubert-nk-inbox-inspector.service', 'schubert-nk-bootstrap-admin.service', MORNING)


def record(argv, old=False):
    tail = 'start_time=[old] ; stop_time=[old] ; pid=42 ; code=exited ; status=143/0' if old else 'start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0'
    return '{ path=/usr/bin/java ; argv[]='+argv+' ; ignore_errors=no ; '+tail+' }'


def fixture():
    argv = '/usr/bin/java fixed MorningProcessMain --resume '+RUN
    dropin = ('[Service]\nExecStart=\nExecStart='+argv+'\n').encode()
    runtime = {'metadata': [0, 1], 'sha256': hashlib.sha256(dropin).hexdigest()}
    before = {'runtime': runtime, 'unitFiles': {'base': {'sha256': 'fixed'}, TARGET: runtime},
              'configuration': {u: {'ExecStart': record('/usr/bin/java '+u, True), 'User': 'same',
                                    'DropInPaths': 'same', 'ReadWritePaths': 'same'} for u in UNITS},
              'caddyPre': record('/usr/bin/java caddyPre', True), 'units': {'all10': 'major18'},
              'rows': {'all24': 'allcolumns'}, 'originals': {'anchorDone': 'same'}, 'native': {'all28': 'same'}}
    before['configuration'][MORNING].update(ExecStart=record(argv, True), DropInPaths=NATIVE+' '+TARGET)
    after = copy.deepcopy(before); after['runtime'] = None; after['unitFiles'].pop(TARGET)
    after['configuration'][MORNING].update(ExecStart=record(argv.removesuffix(' --resume '+RUN)), DropInPaths=NATIVE)
    return before, after, dropin


class Contract(unittest.TestCase):
    def test_normal_and_seven_paired_reset(self):
        a, b, d = fixture(); self.assertTrue(changed_only(a, b, d))
        for u in UNITS[:7]: b['configuration'][u]['ExecStart'] = record('/usr/bin/java '+u)
        b['caddyPre'] = record('/usr/bin/java caddyPre')
        self.assertTrue(changed_only(a, b, d))

    def test_every_field_or_missing_extra_unit(self):
        a, b, d = fixture()
        for key in a:
            if key in ('configuration', 'unitFiles', 'runtime', 'caddyPre'): continue
            c = copy.deepcopy(b); c[key] = 'foreign'
            with self.subTest(key=key), self.assertRaises(ValueError): changed_only(a, c, d)
        for u in UNITS:
            for key in a['configuration'][u]:
                for value in (None, 'foreign'):
                    c = copy.deepcopy(b); c['configuration'][u][key] = value
                    with self.subTest(unit=u, key=key, value=value), self.assertRaises(ValueError): changed_only(a, c, d)
        c = copy.deepcopy(b); c['configuration']['foreign'] = {}
        with self.assertRaises(ValueError): changed_only(a, c, d)

    def test_inbox_bootstrap_and_caddy_half_reset_denied(self):
        for unit in UNITS[7:9]:
            a, b, d = fixture(); b['configuration'][unit]['ExecStart'] = record('/usr/bin/java '+unit)
            with self.subTest(unit=unit), self.assertRaises(ValueError): changed_only(a, b, d)
        a, b, d = fixture(); b['caddyPre'] = record('/usr/bin/java caddyPre')
        with self.assertRaises(ValueError): changed_only(a, b, d)

    def test_runtime_wrong_hash_inode_or_extra_source(self):
        for which in ('hash', 'runtime', 'extra', 'base'):
            a, b, d = fixture()
            if which == 'hash': d += b'foreign'
            if which == 'runtime': b['runtime'] = a['runtime']
            if which == 'extra': b['unitFiles']['unknown'] = {}
            if which == 'base': b['unitFiles']['base']['sha256'] = 'changed'
            with self.subTest(which=which), self.assertRaises(ValueError): changed_only(a, b, d)


if __name__ == '__main__': unittest.main()
