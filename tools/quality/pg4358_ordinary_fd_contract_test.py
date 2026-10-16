"""Independent complete socket pairs and full descriptor transition negative fixtures."""
import copy
import stat
import unittest
import pg4358_ordinary_fd_contract as subject


class OrdinaryDescriptors(unittest.TestCase):
    def fixture(self, api=2, web=1):
        value = {'actors': {}, 'detailedActors': {}, 'database': {'peers': []}}
        table = []; servers = {}; number = 100
        for unit, user, application, count, uid, gid in [
            ('schubert-nk-api.service', 'schubert_app', 'schubert-nk-api', api, 999, 981),
            ('schubert-nk-web.service', 'schubert_web_session', 'schubert-nk-web', web, 997, 980)]:
            actor = {'pid': uid + 1000, 'ticks': 10000, 'argvSha256': 'a' * 64}
            value['actors'][unit] = actor
            detail = {'identity': actor, 'authority': {'Uid': str(uid)}, 'nss': {'uid': uid, 'gid': gid},
                      'children': [], 'fds': {'3': {'target': '/fixed.jar', 'metadata': [1, 10, 0, 0, stat.S_IFREG | 0o640, 1, 42, 20, 21], 'flags': '0100000', 'mountId': '1'}}}
            for index in range(count):
                number += 1; port = 5000 + number; client = str(number); server = str(number + 1000)
                fd = str(90 + index)
                detail['fds'][fd] = {'target': 'socket:[' + client + ']',
                                     'metadata': [9, number, uid, gid, stat.S_IFSOCK | 0o777, 1, 0, 0, 0],
                                     'flags': '04002', 'mountId': '12'}
                value['database']['peers'].append({'pid': number + 5000, 'user': user, 'application': application,
                                                   'address': '127.0.0.1', 'port': port})
                table.extend([['n', '127.0.0.1:' + str(port), '127.0.0.1:5432', '01', '', '', '', '', '', client],
                              ['n', '127.0.0.1:5432', '127.0.0.1:' + str(port), '01', '', '', '', '', '', server]])
                servers[number + 5000] = {server}
            value['detailedActors'][unit] = detail
        return value, table, servers

    def endpoint(self, text):
        address, port = text.rsplit(':', 1)
        return address, int(port)

    def pair(self, table, port, clients, servers):
        left = [r for r in table if self.endpoint(r[1]) == ('127.0.0.1', port)
                and self.endpoint(r[2]) == ('127.0.0.1', 5432) and r[3] == '01' and r[9] in clients]
        right = [r for r in table if self.endpoint(r[1]) == ('127.0.0.1', 5432)
                 and self.endpoint(r[2]) == ('127.0.0.1', port) and r[3] == '01' and r[9] in servers]
        if len(left) != 1 or len(right) != 1:
            raise ValueError('independent two-ended fixture rejected')

    def bind(self, value, table, servers):
        return subject.bind(value, table, servers, self.pair, self.endpoint)

    def test_positive_complete_current_and_nonpool_continuity(self):
        value, table, servers = self.fixture()
        pool = self.bind(value, table, servers)
        self.assertEqual({'90', '91'}, set(pool['schubert-nk-api.service']))
        self.assertEqual({'90'}, set(pool['schubert-nk-web.service']))
        self.assertTrue(subject.same_details(value['detailedActors'], copy.deepcopy(value['detailedActors']), pool, pool))

    def test_all_pool_boundaries_and_fixed_actor_changes(self):
        for api, web, accepted in [(2, 1, True), (8, 2, True), (1, 1, False), (9, 1, False), (2, 0, False), (2, 3, False)]:
            value, table, servers = self.fixture(api, web)
            if accepted:
                self.bind(value, table, servers)
            else:
                with self.subTest(api=api, web=web), self.assertRaises(ValueError):
                    self.bind(value, table, servers)
        value, table, servers = self.fixture(); pool = self.bind(value, table, servers)
        for key, wrong in [('pid', 1), ('ticks', 1), ('argvSha256', 'foreign')]:
            after = copy.deepcopy(value['detailedActors'])
            after['schubert-nk-api.service']['identity'][key] = wrong
            with self.subTest(key=key), self.assertRaises(ValueError):
                subject.same_details(value['detailedActors'], after, pool, pool)

    def test_actual_pool_replacement_allowed_but_nonpool_any_field_rejected(self):
        before, table, servers = self.fixture(); old_pool = self.bind(before, table, servers)
        after = copy.deepcopy(before); new_table = copy.deepcopy(table)
        after['detailedActors']['schubert-nk-api.service']['fds']['90']['target'] = 'socket:[900]'
        after['detailedActors']['schubert-nk-api.service']['fds']['90']['metadata'][1] = 900
        new_table[0][9] = '900'
        new_pool = self.bind(after, new_table, servers)
        self.assertTrue(subject.same_details(before['detailedActors'], after['detailedActors'], old_pool, new_pool))
        for field, wrong in [('target', '/foreign'), ('metadata', [1]), ('flags', '0'), ('mountId', 'foreign')]:
            bad = copy.deepcopy(after); bad['detailedActors']['schubert-nk-api.service']['fds']['3'][field] = wrong
            with self.subTest(field=field), self.assertRaises(ValueError):
                subject.same_details(before['detailedActors'], bad['detailedActors'], old_pool, new_pool)
        for key in ['identity', 'authority', 'nss', 'children']:
            bad = copy.deepcopy(after); bad['detailedActors']['schubert-nk-api.service'][key] = 'foreign'
            with self.subTest(key=key), self.assertRaises(ValueError):
                subject.same_details(before['detailedActors'], bad['detailedActors'], old_pool, new_pool)

    def test_wrong_peer_role_app_endpoint_backend_and_duplicates_rejected(self):
        for key, bad in [('user', 'foreign'), ('application', 'foreign'), ('address', '10.0.0.1'), ('port', 1), ('pid', 1)]:
            value, table, servers = self.fixture(); value['database']['peers'][0][key] = bad
            with self.subTest(key=key), self.assertRaises((ValueError, KeyError)):
                self.bind(value, table, servers)
        for operation in ['duplicatePeer', 'duplicateClient', 'missingServer', 'foreignSocket', 'extraAlias', 'wrongCapturedInode', 'wrongUid', 'wrongFlags', 'missingPeer', 'extraUnknownFd']:
            value, table, servers = self.fixture()
            fd = value['detailedActors']['schubert-nk-api.service']['fds']['90']
            if operation == 'duplicatePeer': value['database']['peers'].append(copy.deepcopy(value['database']['peers'][0]))
            elif operation == 'duplicateClient': table.append(copy.deepcopy(table[0]))
            elif operation == 'missingServer': del table[1]
            elif operation == 'foreignSocket': fd['target'] = 'socket:[999]'; fd['metadata'][1] = 999
            elif operation == 'extraAlias': value['detailedActors']['schubert-nk-api.service']['fds']['99'] = copy.deepcopy(fd)
            elif operation == 'wrongCapturedInode': fd['metadata'][1] += 1
            elif operation == 'wrongUid': fd['metadata'][2] = 0
            elif operation == 'wrongFlags': fd['flags'] = '0'
            elif operation == 'missingPeer': del value['database']['peers'][0]
            elif operation == 'extraUnknownFd':
                fixed, _, _ = self.fixture(); pool = self.bind(fixed, table, servers)
                value['detailedActors']['schubert-nk-api.service']['fds']['99'] = copy.deepcopy(fd)
                with self.assertRaises(ValueError): subject.same_details(fixed['detailedActors'], value['detailedActors'], pool, pool)
                continue
            with self.subTest(operation=operation), self.assertRaises((ValueError, KeyError)):
                self.bind(value, table, servers)


if __name__ == '__main__':
    unittest.main()
