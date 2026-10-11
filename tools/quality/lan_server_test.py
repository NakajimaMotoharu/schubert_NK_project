"""Independent negative fixtures for the LAN authentication boundary (not PG PT)."""
import base64
import subprocess
import unittest
from unittest.mock import patch

import lan_server as server


class ServerBoundaryTest(unittest.TestCase):
    def test_only_mini_selected_without_root_auth(self):
        fixture = 'addr: 192.168.1.131\nuser: mini\npass: fixture-mini\nuser: root\npass: fixture-root\n'
        with patch.object(server.Path, 'read_text', return_value=fixture):
            self.assertEqual('fixture-mini', server.credentials())

    def test_wrong_address_and_missing_mini_refused(self):
        for fixture in ['addr: 192.168.1.132\nuser: mini\npass: fixture\n',
                        'addr: 192.168.1.131\nuser: root\npass: fixture\n']:
            with self.subTest(fixture=fixture), patch.object(server.Path,'read_text',return_value=fixture):
                with self.assertRaises(RuntimeError):
                    server.credentials()

    def test_unpinned_key_refused_before_credentials(self):
        scan = subprocess.CompletedProcess([],0,'192.168.1.131 ssh-ed25519 '+base64.b64encode(b'wrong-key').decode()+'\n','')
        with patch.object(server.subprocess,'run',return_value=scan), patch.object(server,'credentials') as secret:
            with self.assertRaises(RuntimeError):
                server.run('true')
            secret.assert_not_called()

    def test_empty_key_refused_before_credentials(self):
        with patch.object(server.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'','')), patch.object(server,'credentials') as secret:
            with self.assertRaises(RuntimeError):
                server.run('true')
            secret.assert_not_called()

    def test_destination_boundary_before_auth(self):
        for target in ['/home/mini/other/', '/root/', '/home/mini/schubert-nk-pgpt-evil/',
                       '/home/mini/schubert-nk-pgpt/../outside/', '/home/mini/schubert-nk-pgpt/./tools/',
                       '/home/mini/schubert-nk-pgpt//tools/', '/home/mini/schubert-nk-pgpt/tools/\n',
                       '/home/mini/schubert-nk-pgpt/x;uname',None]:
            with patch.object(server,'pinned_key') as key:
                with self.assertRaises(ValueError):
                    server.copy('/fixture',target)
                key.assert_not_called()

    def test_canonical_destination_transfers_without_root(self):
        with patch.object(server,'pinned_key',return_value='fixture public'),patch.object(server,'authenticated',return_value=(0,'')) as transfer:
            self.assertEqual((0,''),server.copy('/fixture','/home/mini/schubert-nk-pgpt/tools/'))
            argv=transfer.call_args.args[0]
            self.assertEqual('mini@192.168.1.131:/home/mini/schubert-nk-pgpt/tools/',argv[-1])

    def test_timeout_closes_only_owned_local_child(self):
        with patch.object(server.pexpect,'spawn') as spawn:
            spawn.return_value.expect.side_effect=server.pexpect.TIMEOUT('fixture deadline')
            with self.assertRaises(server.pexpect.TIMEOUT):
                server.authenticated(['ssh','fixture'],None,1)
            spawn.return_value.close.assert_called_once_with(force=True)

    def test_normal_exit_closes_and_preserves_status(self):
        with patch.object(server.pexpect,'spawn') as spawn,patch.object(server,'credentials',return_value='fixture'):
            spawn.return_value.before='public result'
            spawn.return_value.exitstatus=0
            self.assertEqual((0,'public result'),server.authenticated(['ssh','fixture'],None,1))
            spawn.return_value.close.assert_called_once_with(force=True)


if __name__ == '__main__':
    unittest.main()
