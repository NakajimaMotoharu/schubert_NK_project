"""SSC280/285 independent TCP-family normalization, not owner relaxation."""
import ipaddress
import unittest


def endpoint(value):
    address, port = value.split(':')
    raw = bytes.fromhex(address)
    if len(raw) not in (4, 16):
        raise ValueError('kernel IPv4 or IPv6 address required')
    parsed = ipaddress.ip_address(b''.join(raw[i:i + 4][::-1] for i in range(0, len(raw), 4)))
    if isinstance(parsed, ipaddress.IPv6Address) and parsed.ipv4_mapped is not None:
        parsed = parsed.ipv4_mapped
    return str(parsed), int(port, 16)


def tcp_pair(records, port, client_inodes, server_inodes):
    client = ('127.0.0.1', port)
    database = ('127.0.0.1', 5432)
    outbound = [r for r in records if len(r) >= 10 and r[3] == '01'
                and r[9] in client_inodes and endpoint(r[1]) == client and endpoint(r[2]) == database]
    inbound = [r for r in records if len(r) >= 10 and r[3] == '01'
               and r[9] in server_inodes and endpoint(r[1]) == database and endpoint(r[2]) == client]
    if len(outbound) != 1 or len(inbound) != 1:
        raise ValueError('exact owned established TCP endpoint pair required')
    return outbound[0][9], inbound[0][9]


class TcpPairTest(unittest.TestCase):
    def records(self):
        # Fixed Linux proc vectors, independently chosen port 40000 (0x9c40).
        return [['0:', '0000000000000000FFFF00000100007F:9C40',
                 '0000000000000000FFFF00000100007F:1538', '01', '0', '0', '0', '0', '0', '123'],
                ['1:', '0100007F:1538', '0100007F:9C40', '01', '0', '0', '0', '0', '0', '456']]

    def test_dual_stack_exact(self):
        self.assertEqual(('123', '456'), tcp_pair(self.records(), 40000, {'123'}, {'456'}))

    def test_independent_endpoints(self):
        self.assertEqual(('127.0.0.1', 5432), endpoint('0100007F:1538'))
        self.assertEqual(('127.0.0.1', 40000), endpoint('0000000000000000FFFF00000100007F:9C40'))
        self.assertEqual(('::1', 5432), endpoint('00000000000000000000000001000000:1538'))
        with self.assertRaises(ValueError):
            endpoint('0000:1538')

    def test_owner_port_state_and_duplicate_rejected(self):
        for port, client, server in [(40001, {'123'}, {'456'}), (40000, {'999'}, {'456'}),
                                     (40000, {'123'}, {'999'})]:
            with self.subTest(port=port, client=client, server=server), self.assertRaises(ValueError):
                tcp_pair(self.records(), port, client, server)
        for index in (0, 1):
            rows = self.records()
            rows[index][3] = '0A'
            with self.subTest(state=index), self.assertRaises(ValueError):
                tcp_pair(rows, 40000, {'123'}, {'456'})
            rows = self.records()
            rows.append(rows[index][:])
            with self.subTest(duplicate=index), self.assertRaises(ValueError):
                tcp_pair(rows, 40000, {'123'}, {'456'})


if __name__ == '__main__':
    unittest.main()
