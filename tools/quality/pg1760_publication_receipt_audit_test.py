"""YKT922: literal emitted Java completion properties, never replay publication."""
import json
import re
import unittest
from pg1691_completed_ordinary_publication_sources import sources
from pg1696_completed_publication_independent_post import payload

EXPECTED={'genuineParentDone':'true','finiteOrdinaryPublication':'true','allNewScopesReturnedNormally':'true','originalBackupStartupRowsPreserved':'true','startsStopsReloadsSqlWrites0':'true','canonicalEpochApprovalCurrentChanged':'true','oldUnknownNormalized':'false'}

def admit(text):
    rows=text.splitlines()
    if any(v.count('=')!=1 for v in rows):raise ValueError('fixed property lines required')
    parsed=dict(v.split('=',1)for v in rows)
    if parsed!=EXPECTED or len(rows)!=len(parsed):raise ValueError('publication effects and exact unique keys required')
    return parsed

class Receipt(unittest.TestCase):
    def test_actual_emitted_completion_literal_and_independent_counterexamples(self):
        java=sources()['Pg1691OrdinaryPublication.java']
        values=[json.loads(v) for v in re.findall(r'"(?:[^"\\]|\\.)*"',java)if 'genuineParentDone=true' in v and 'canonicalEpochApprovalCurrentChanged=true'in v]
        self.assertEqual(1,len(values));text=values[0];self.assertEqual(EXPECTED,admit(text))
        for bad in (text.replace('canonicalEpochApprovalCurrentChanged=true','canonicalEpochApprovalCurrentChanged=false'),text.replace('startsStopsReloadsSqlWrites0=true','startsStopsReloadsEpochWrites0=true'),text.replace('oldUnknownNormalized=false','oldUnknownNormalized=true'),text+'canonicalEpochApprovalCurrentChanged=true\n',text.replace('\n','\\n'),text+'unknown=true\n'):
            with self.assertRaises(ValueError):admit(bad)
        old=payload()
        self.assertIn('startsStopsReloadsEpochWrites0=true',old)
        for key in ("oracle['canonical_epoch'](expected_epoch)","oracle['verify'](public_first,public_last,'release'","oracle['NEW_APPROVAL']","oracle['OLD_LINK']",'oldReceiptBug1154PreservedNotInferred'):
            self.assertIn(key,old)

if __name__=='__main__':unittest.main()
