"""Preparation cannot be accepted before actual immutable original3939 artifacts exist."""
import unittest
from unittest.mock import patch
import pg5792_current_static_whole_join as p


class NoPrematureWhole(unittest.TestCase):
    def test_unknown_hashes_block_before_any_artifact_read(self):
        with patch.object(p,'QUALIFIED_PUBLIC_SHA',None),patch.object(p,'CURRENT_CASES_SHA',None),patch.object(p,'sha',side_effect=AssertionError('no premature read')):
            with self.assertRaisesRegex(ValueError,'await actual original3939'):p.qualified_whole()


if __name__=='__main__':unittest.main()
