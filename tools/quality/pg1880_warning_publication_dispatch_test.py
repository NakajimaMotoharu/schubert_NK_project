"""Actual direct entry rejects before filesystem/SSH and reload never auto-retries."""
import os
import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import pg1880_warning_publication_dispatch as driver
from pg1877_unit_exchange_contract import UnitExchange
from pg1882_warning_publication_post import payload
from pyflakes.api import check


class Direct(unittest.TestCase):
    def test_closed_actual_arguments_before_read_and_ssh(self):
        with patch.object(driver.subprocess,'check_output')as git,patch.object(driver,'management_gate')as gate:
            for args in [[],['prepare-ro'],['activate','again'],['stage','extra']]:
                with patch.object(driver.sys,'argv',['driver',*args]):
                    with self.assertRaises(ValueError):driver.main()
            git.assert_not_called();gate.assert_not_called()

    def test_dirty_actual_source_rejected_before_ownership(self):
        with patch.object(driver.sys,'argv',['driver','activate']),patch.object(driver.subprocess,'check_output',return_value=b' M file\n')as git,patch.object(driver,'management_gate')as gate:
            with self.assertRaises(ValueError):driver.main()
            self.assertEqual(1,git.call_count);gate.assert_not_called()

    def test_one_reload_reservation_before_command_and_repeat_refused(self):
        with tempfile.TemporaryDirectory()as d:
            obj=UnitExchange.__new__(UnitExchange);obj.exchanged=True;obj.reloaded=False
            obj.private=os.open(d,os.O_RDONLY|os.O_DIRECTORY)
            try:
                with patch.object(obj,'verify')as verify,patch('pg1877_unit_exchange_contract.subprocess.run',return_value=subprocess.CompletedProcess([],0,b'',b''))as run:
                    obj.reload()
                    self.assertEqual(b'one normal daemon-reload; no retry\n',(Path(d)/'daemon-reload-reserved.private').read_bytes())
                    self.assertEqual(0o600,(Path(d)/'daemon-reload-reserved.private').stat().st_mode&0o777)
                    self.assertTrue(obj.reloaded);self.assertEqual(2,verify.call_count)
                    run.assert_called_once_with(['/usr/bin/systemctl','daemon-reload'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
                    with self.assertRaises(ValueError):obj.reload()
                    self.assertEqual(1,run.call_count)
            finally:os.close(obj.private)

    def test_timeout_retains_reserved_unknown_and_no_second_command(self):
        with tempfile.TemporaryDirectory()as d:
            obj=UnitExchange.__new__(UnitExchange);obj.exchanged=True;obj.reloaded=False;obj.private=os.open(d,os.O_RDONLY|os.O_DIRECTORY)
            try:
                with patch.object(obj,'verify'),patch('pg1877_unit_exchange_contract.subprocess.run',side_effect=subprocess.TimeoutExpired('daemon-reload',20))as run:
                    with self.assertRaises(subprocess.TimeoutExpired):obj.reload()
                    self.assertFalse(obj.reloaded)
                    self.assertEqual(b'one normal daemon-reload; no retry\n',(Path(d)/'daemon-reload-reserved.private').read_bytes())
                    with self.assertRaises(FileExistsError):obj.reload()
                    self.assertEqual(1,run.call_count)
            finally:os.close(obj.private)

    def test_actual_whole_post_globals_and_unique_sole_unit_oracle(self):
        raw=payload();self.assertEqual(0,check(raw,'<actual independent full post>'))
        self.assertIn("for stamp,phase,observed in phases:oracle['verify']",raw)
        self.assertIn("if k not in {'startup','unitFilesActual'}",raw)
        self.assertIn("if k!=unit_path",raw)
        self.assertIn("SuccessExitStatus=10",raw)
        self.assertIn("len(old_unit)==len(new_unit)==10",raw)
        self.assertIn("old_unit[9]=='28e6e23ddcfeacac7dc1daf326a1a2b1bc91895bbd34b313fe89a1b04f499bd6'",raw)
        self.assertNotIn('reset-failed',raw)


if __name__=='__main__':unittest.main()
