import ast
import copy
import unittest
from pg4058_original_read_profile_test import GuardTest, guards
import pg4060_original_profile_dual_stack as profile


class DualStackTest(unittest.TestCase):
    def test_actual_emitted_guard_all_pairs_and_negative(self):
        raw = profile.payload('run')
        for owned in [False, True]:
            value, ns, sockets = GuardTest().fixture(owned)
            # Independent kernel IPv6-mapped client vectors, IPv4 server vectors.
            v4 = ['header']; v6 = ['header']
            for i, row in enumerate(value['database']['peers']):
                port = row['port']; client, server = str(100 + 2 * i), str(101 + 2 * i)
                v6.append(f'0: 0000000000000000FFFF00000100007F:{port:04X} 0000000000000000FFFF00000100007F:1538 01 0 0 0 0 0 {client}')
                v4.append(f'0: 0100007F:1538 0100007F:{port:04X} 01 0 0 0 0 0 {server}')
            table = {'/proc/net/tcp': '\n'.join(v4), '/proc/net/tcp6': '\n'.join(v6)}
            current = guards(table, sockets, raw); owner = (140, 240) if owned else None
            current['peers'](value, owner)
            duplicate = {**table, '/proc/net/tcp6': table['/proc/net/tcp6'] + '\n' + v6[1]}
            with self.assertRaises(ValueError): guards(duplicate, sockets, raw)['peers'](value, owner)
            sockets[220].clear()
            with self.assertRaises(ValueError): current['peers'](value, owner)
            changed = copy.deepcopy(value); changed['database']['peers'][0]['port'] += 100
            with self.assertRaises(ValueError): current['peers'](changed, owner)

    def test_new_slot_full_hash_and_original_inputs(self):
        raw = profile.payload('run'); tree = ast.parse(raw)
        self.assertTrue("compiled['classHashes']" in raw, 'all compiled bytecode hashes required')
        self.assertTrue(profile.SLOT in raw and 'pg4058-original-read-profile-v1' not in raw,
                        'failed slot must remain immutable')
        self.assertEqual(1, sum(isinstance(n, ast.FunctionDef) and n.name == 'tcp_pair' for n in tree.body))
        with self.assertRaises(ValueError): profile.once('one one', 'one', 'replacement')


if __name__ == '__main__': unittest.main()
