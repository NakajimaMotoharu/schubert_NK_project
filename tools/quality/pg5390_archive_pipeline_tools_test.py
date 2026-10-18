import re
import unittest
import pg5390_archive_pipeline_selected as entry

NAMES=('archiveown001All64StopStatesMatchIndependentLiteralPrecedenceAndOrder',
    'archiveown002All27HoldStatesKeepFirstUnknownAndConfirmEveryRemainingChild',
    'archiveown003UnknownCollectionNeverUnwindsAsConfirmedTerminal',
    'archiveown004NullableGettersAndIdleChildrenPreserveAdmissionAndInterrupt',
    'archiveown005ExistingAndRepeatedUnknownKeepIdentityAndSanitizeOnlyLaterFailures',
    'archiveown006ParallelPlansNeverStopOrConfirmEachOthersProcesses')


class ArchiveScope(unittest.TestCase):
    def test_fixed_stop_and_hold_goldens_match_independent_priority_rules(self):
        path=entry.selected.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/BackupArchiveProcessTest.java'
        raw=path.read_text()
        tables={}
        for name in ('STOP_TYPES','STOP_SUPPRESSED','STOP_WINNER'):
            declaration=re.search(name+r'\s*=\s*(.*?);',raw,re.S).group(1)
            tables[name]=''.join(re.findall(r'"([NIRE0-9x]+)"',declaration))
            self.assertEqual(len(tables[name]),64)
        for number in range(64):
            inputs=['NIRE'[(number>>shift)&3] for shift in (4,2,0)]
            unknown=[i for i,value in enumerate(inputs) if value in 'RE']
            expected=inputs[unknown[0]] if unknown else 'I' if 'I' in inputs else 'N'
            self.assertEqual(tables['STOP_TYPES'][number],expected)
            self.assertEqual(tables['STOP_WINNER'][number],str(unknown[0]) if unknown else 'x')
            self.assertEqual(int(tables['STOP_SUPPRESSED'][number]),
                sum(value!='N' for value in inputs[unknown[0]+1:]) if unknown else 0)
        hold={}
        for name in ('types','suppressed','winners'):
            declaration=re.search(r'String '+name+r'\s*=\s*(.*?);',raw,re.S).group(1)
            hold[name]=''.join(re.findall(r'"([NRE0-9x]+)"',declaration))
            self.assertEqual(len(hold[name]),27)
        for number in range(27):
            inputs=['NRE'[number//divisor%3] for divisor in (9,3,1)]
            unknown=[i for i,value in enumerate(inputs) if value in 'RE']
            self.assertEqual(hold['types'][number],inputs[unknown[0]] if unknown else 'N')
            self.assertEqual(hold['winners'][number],str(unknown[0]) if unknown else 'x')
            self.assertEqual(int(hold['suppressed'][number]),len(unknown)-1 if unknown else 0)

    def test_six_new_and_original_ten_with_explicit_main_growth(self):
        path=entry.selected.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/BackupArchiveProcessTest.java'
        raw=path.read_text();names=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
        self.assertEqual(len(names),16);self.assertEqual(raw.count('@Test'),16)
        self.assertEqual(tuple(n for n in names if n.startswith('archiveown')),NAMES)
        entry.configure()
        self.assertEqual((len(entry.selected.EXTRA_CHANGED),len(entry.selected.EXTRA_DEBUG),len(entry.extra_suites())),(62,190,103))
        self.assertEqual(entry.selected.EXTRA_ADDED,entry.ADDED)
        self.assertEqual(entry.selected.EXTRA_REMOVED,entry.REMOVED)
        self.assertEqual(764+len(entry.ADDED)-len(entry.REMOVED),entry.EXPECTED_MAIN)
        self.assertEqual(entry.repetitions(),entry.previous.repetitions())

    def test_missing_or_undeclared_added_removed_classes_are_never_coverage_exclusions(self):
        validate=entry.selected.validate_physical_delta
        validate({'changed'},{'newA','newB'},{'oldA'},{'changed'},set(),{'newA','newB'},{'oldA'})
        validate({'changed'},set(),set(),{'changed'},set(),set(),set())
        for changed,added,removed in ((set(),{'newA','newB'},{'oldA'}),({'changed'},{'newA'},{'oldA'}),
            ({'changed'},{'newA','newB'},set()),({'changed','foreign'},{'newA','newB'},{'oldA'})):
            with self.assertRaises(ValueError):validate(changed,added,removed,{'changed'},set(),{'newA','newB'},{'oldA'})


if __name__=='__main__':unittest.main()
