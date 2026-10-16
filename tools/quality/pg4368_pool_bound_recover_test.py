import ast
import hashlib
import unittest
import pg4368_pool_bound_recover as subject
import pg4360_pool_bound_partial_sources as sources


class CurrentBoundEntry(unittest.TestCase):
    def test_same_frozen_bootstrap_and_exact_three_current_phases(self):
        hashes = {name: hashlib.sha256(raw.encode()).hexdigest() for name, raw in sources.files().items()}
        for name, mode in [('keeper.py', 'recover'), ('partial.py', 'inspect'), ('partial.py', 'recover'), ('post.py', None)]:
            args = subject.remote_args(name, hashes, mode)
            self.assertIn('pg4366-pool-bound-tools-v3', args[-1])
            self.assertNotIn('pg4182', args[-1])
            for digest in hashes.values(): self.assertIn(digest, args[-1])
        with self.assertRaises(ValueError): subject.remote_args('keeper.py', hashes, 'inspect')

    def test_current_entry_retains_qualified_post_and_actual_transport(self):
        raw = subject.main_source(); ast.parse(raw)
        self.assertIn('SSC293_PAIR_READY', raw)
        self.assertNotIn('SSC292_', raw)
        self.assertIn("receipt['actualExit']", raw)
        self.assertIn("job('post.py',None", raw)
        self.assertIn("newMARDDBTenRefNormalClose", raw)
        self.assertIn('acquired.wait(30)', raw)


if __name__ == '__main__':
    unittest.main()
