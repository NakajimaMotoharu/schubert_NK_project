"""Numeric usage integrity and forward-only collection, no real private logs."""
import json
from pathlib import Path
import tempfile
import unittest
from pmo_usage_increment import normalize, scan


def row(response='r1', cached=80):
    return {'timestamp': '2026-10-08T00:00:00+09:00', 'type': 'event_msg',
            'payload': {'type': 'token_usage_record', 'response_id': response,
                        'usage': {'input_tokens': 100, 'cached_input_tokens': cached,
                                  'output_tokens': 20, 'reasoning_output_tokens': 10}}}


class UsageIntegrityTest(unittest.TestCase):
    def test_subsets_not_double_counted_and_id_redacted(self):
        data = normalize(row())
        self.assertEqual((data['N'], data['T']), (40, 120))
        self.assertEqual(len(data['responseKey']), 64)
        self.assertNotIn('response_id', data)

    def test_unknown_schema_and_invalid_subset_do_not_make_zero(self):
        bad = row(); del bad['payload']['usage']['input_tokens']
        with self.assertRaises(ValueError): normalize(bad)
        with self.assertRaises(ValueError): normalize(row(cached=101))

    def test_repeated_response_and_compaction_response_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'stream.jsonl'
            items = [row(), row(), row('compaction-response')]
            path.write_text(''.join(json.dumps(item)+'\n' for item in items))
            _, rows, issues, backlog = scan(path, 0, {})
            self.assertEqual(sum(r['N'] for r in rows), 80)
            self.assertEqual(len(rows), 2)
            self.assertFalse(issues or backlog)

    def test_old_text_ignored_incomplete_tail_waits_then_deduplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'stream.jsonl'; old = b'private old text\n'
            complete = json.dumps(row()).encode()
            path.write_bytes(old+complete)
            seen = {}; end, rows, _, pending = scan(path, len(old), seen)
            self.assertEqual(end, len(old)); self.assertEqual(rows, []); self.assertTrue(pending)
            with path.open('ab') as handle: handle.write(b'\n')
            end, rows, _, _ = scan(path, end, seen)
            self.assertEqual(len(rows), 1)
            with path.open('ab') as handle: handle.write(complete+b'\n')
            _, rows, _, _ = scan(path, end, seen)
            self.assertEqual(rows, [])

    def test_conflicting_same_response_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'stream.jsonl'
            path.write_text(json.dumps(row())+'\n'+json.dumps(row(cached=70))+'\n')
            _, rows, issues, _ = scan(path, 0, {})
            self.assertEqual(len(rows), 1)
            self.assertEqual(issues, ['CONFLICTING_RESPONSE_USAGE'])

    def test_cumulative_token_count_and_text_not_exported(self):
        data = {'payload': {'type': 'token_count', 'info': {'total_token_usage': {'input_tokens': 999}}}}
        self.assertIsNone(normalize(data))
        self.assertIsNone(normalize({'payload': {'type': 'agent_message', 'text': 'private'}}))


if __name__ == '__main__': unittest.main()
