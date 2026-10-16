"""Actual operational entry consumes only successful4806, never a fabricated4776 receipt."""
import unittest
from pathlib import Path
from unittest.mock import patch
from pyflakes.api import checkPath
import pg4778_new_current_owned_post as post


class PostLink(unittest.TestCase):
    def test_actual_entry_exact_stop_selector_and_unchanged_stage_source(self):
        main=post.namespace()['entry']()
        strings={c for c in main.__code__.co_consts if isinstance(c,str)}
        self.assertIn('pg4806-stop-v1.safe.json',strings);self.assertNotIn('pg4776-stop-v1.safe.json',strings)
        self.assertIn('pg4774-frozen-v1.safe.json',strings);self.assertIn('pg4772_parent_receipt.py',strings)
        self.assertEqual('825e463334c43a5bc96f50db964df22e11758d1b',main.__globals__['SOURCE'])
        self.assertEqual('pg4778-new-current-owned-post-v1',main.__globals__['SLOT'])
        self.assertNotIn('run_action',main.__code__.co_names)
        self.assertEqual(0,checkPath(post.__file__));self.assertEqual(0,checkPath(__file__))

    def test_failed_actual_stop_receipt_cannot_start_guest_read(self):
        main=post.namespace()['entry']()
        with patch.object(main.__globals__['subprocess'],'check_output',return_value=b''),patch.object(Path,'read_bytes',return_value=b'{"actualExit":1,"sourceQualified":false,"productionSource":"825e463334c43a5bc96f50db964df22e11758d1b"}'),patch.object(main.__globals__['subprocess'],'run')as execute:
            with self.assertRaises(ValueError):main()
            execute.assert_not_called()


if __name__=='__main__':unittest.main()
