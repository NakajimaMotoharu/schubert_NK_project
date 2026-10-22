import subprocess
import unittest
import pg6860_web_deadline_structure as p


class WebDeadlineStructureTest(unittest.TestCase):
    def values(self):
        return subprocess.check_output(['git','show',p.OLD+':'+p.MAIN],cwd=p.ROOT,text=True),(p.ROOT/p.MAIN).read_text()

    def test_actual_exact_legacy_expansion(self):
        before,after=self.values();x=p.expand(before,after)
        self.assertTrue(x['legacyBodyAndOutsideMethodEqual']);self.assertFalse(x['vendorPreemptionAdded'])

    def test_original_budget_early_irq_loss_or_unknown_success_are_rejected(self):
        before,after=self.values()
        mutants=[
          p.replace_once(p.tokens(after),p.AFTER_AWAIT,p.BEFORE_AWAIT),
          p.replace_once(p.tokens(after),'if (entryInterrupted) Thread.currentThread().interrupt(); try { if (closed.get())','try { if (closed.get())'),
          p.replace_once(p.tokens(after),'if (!started) return Optional.of(new IOException(STOP_UNCONFIRMED));','if (!started) return Optional.empty();')]
        for words in mutants:
            with self.assertRaises(ValueError):p.expand(before,' '.join(words))


if __name__=='__main__':unittest.main()
