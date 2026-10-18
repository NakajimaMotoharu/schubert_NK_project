import copy
import unittest
from pathlib import Path
from pyflakes.api import checkPath
import pg5520_guest_clock_contract as entry
from pg3136_browser_rows_oracle_test import fixture


def context():
    # Deliberate independent host/guest offset; no production data or clock query.
    before={'clockSource':entry.SOURCE,'instant':'2026-10-15T02:00:00Z','hostStartNanos':1,'hostEndNanos':1_000_000_001,
        'hostBeforeUtc':'2026-10-15T02:00:05Z','hostAfterUtc':'2026-10-15T02:00:06Z'}
    after={'clockSource':entry.SOURCE,'instant':'2026-10-15T02:02:00Z','hostStartNanos':120_000_000_001,'hostEndNanos':121_000_000_001,
        'hostBeforeUtc':'2026-10-15T02:02:05Z','hostAfterUtc':'2026-10-15T02:02:06Z'}
    return{'owner':1,'lower':before['instant'],'upper':after['instant'],'clockDomain':entry.DOMAIN,'lowerClock':before,'upperClock':after}


class GuestClock(unittest.TestCase):
    def test_actual_guest_domain_not_host_offset_correction(self):
        c=context();self.assertTrue(entry.verify_context(c)['guestClockWindowQualified'])
        old,new=fixture();self.assertTrue(entry.qualify(old,new,1,c['lower'],c['upper'])['all24Qualified'])
        # No event-based extension: the unchanged oracle still rejects out-of-window data.
        new['schubert_web_session.web_log_outbox'][0]['created_at']='2026-10-15T01:59:59.999Z'
        with self.assertRaises(ValueError):entry.qualify(old,new,1,c['lower'],c['upper'])

    def test_host_only_or_changed_bound_missing_wrong_domain_never_pass(self):
        original=context()
        cases=[{k:original[k]for k in('owner','lower','upper')},{**original,'owner':True},{**original,'clockDomain':'host'},
            {**original,'lower':'2026-10-15T01:59:59Z'},{**original,'lowerClock':None}]
        for value in cases:
            with self.assertRaises(ValueError):entry.verify_context(value)
        for label,key,value in(('lower','clockSource','row-minimum'),('lower','hostStartNanos',True),
            ('lower','hostEndNanos',40_000_000_001),('upper','hostStartNanos',0),
            ('upper','hostEndNanos',700_000_000_000),('upper','hostBeforeUtc','2026-10-15T01:00:00Z')):
            bad=copy.deepcopy(original);bad[label+'Clock'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):entry.verify_context(bad)

    def test_guest_reversal_timezone_and_missing_witness_refused(self):
        for value in('2026-10-15T01:59:00Z','2026-10-15T02:30:00Z','2026-10-15T02:02:00'):
            bad=context();bad['upper']=value;bad['upperClock']['instant']=value
            with self.assertRaises(ValueError):entry.verify_context(bad)
        bad=context();bad['lowerClock'].pop('clockSource')
        with self.assertRaises(ValueError):entry.verify_context(bad)

    def test_capture_order_is_before_source_and_after_snapshot_not_row_derived(self):
        root=Path(__file__).resolve().parents[2]
        raw=(root/'tools/quality/vm/050_s1/NativeNkBrowserBusinessCohort.java').read_text()
        run=raw[raw.index('  static void run(String[] args)'):]
        self.assertLess(run.index('lowerClock = guestClock()'),run.index('stage = "SOURCE"; source()'))
        self.assertLess(run.index('privateValue("after-rows.private.json", allRows())'),run.index('upperClock = guestClock()'))
        self.assertIn('query("select to_json(clock_timestamp())")',raw)
        self.assertNotIn('String lower = java.time.Instant.now()',run)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
