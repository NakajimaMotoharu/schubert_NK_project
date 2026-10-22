import unittest

import pg6984_chr_adapter_acceptance as p


class CommonAcceptanceContractTest(unittest.TestCase):
    def test_actual_utf8_canonical_documents_not_display_quoted_alias(self):
        self.assertEqual(2,len(p.DOCS))
        for path in p.DOCS:
            self.assertNotIn('"',path)
            self.assertNotIn('\\',path)
            self.assertEqual(p.old.initial.git('origin/main',path),(p.host.ROOT/path).read_bytes())

    def test_source_formal_and_unrequested_scope_refused_before_evidence(self):
        valid=dict(source=p.SOURCE,reviewState='COMPLETE',acceptedBy='reviewer',formalUpdated=False,wholeEffortCompletionRate=None,
                   parentAccepted=False,newOriginal190Item=0)
        for changed in ({**valid,'source':'old'},{**valid,'formalUpdated':True},
                        {**valid,'reviewState':'PENDING'},{**valid,'wholeEffortCompletionRate':100}):
            with self.assertRaises(ValueError):p.verify(changed)


if __name__=='__main__':unittest.main()
