import ast
import unittest
from pg1183_canonical_resume_observer import source


class CanonicalObserverTest(unittest.TestCase):
    def test_current_pins_independent_admission_and_original_budget(self):
        s = source();ast.parse(s)
        for part in ['pg1182-canonical-runtime-post-v1.safe.json', 'pg1183-parent-watch-v1.private.jsonl', 'cbca8738-3b24-4090-b77c-bf029677cdd6', 'd5b00104280028d9ea81b44c1d1c805f3c2861ed', '0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d']:
            self.assertTrue(part in s, part)
        ns = {'__file__': __file__, '__name__': 'data'};exec(s, ns)
        watch = ns['watch']();ast.parse(watch)
        self.assertTrue("deadline=int(m['ExecMainStartTimestampMonotonic'])/1e6+1860" in watch)
        self.assertTrue('same(roots[role],aa)' in watch)
        for forbidden in ["'start'", "'stop'", 'daemon-reload']:
            self.assertFalse(forbidden in watch, forbidden)


if __name__ == '__main__':unittest.main()
