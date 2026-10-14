"""Pure independent Backup oracle binding; no Backup/DB/guest execution."""
import ast
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import pg1257_fresh_independent_terminal_post as schema
from pg1446_current_cold_stage import W
import pg2716_operation_owned_post as stopped
import pg2724_operation_backup_content as backup
from pg2674_operation_publication_sources import production


class NewBackupOracle(unittest.TestCase):
    def test_literal_oracle_uses_new_actual_run_cutoff_and_configuration(self):
        live=json.loads((W/'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
        seal=json.loads((W/'pg2548-strict-current-full-seal-v1/manifest.safe.json').read_bytes())
        fixture={**live,'productionSource':production(),'binding':{**live['binding'],'run':'00000000-0000-0000-0000-000000000009','cutoff':'2026-10-14T01:00:00Z'}}
        seals={n:'a'*64 for n in schema.previous.SEALS}
        ctx=('b'*64,seal['observedOwned'],seal['genuineCompletion'],seal['doneEndUtc'])
        base=stopped.emit(seals,ctx,fixture,'a'*64);original=Path.read_bytes
        def read(path):
            if path==W/'pg2686-operation-current-live-binding-v1/manifest.safe.json':return json.dumps(fixture).encode()
            return original(path)
        with patch.object(Path,'read_bytes',read),patch.object(backup.current,'payload',return_value=base):raw=backup.payload(seals)
        ast.parse(raw)
        for value in [fixture['binding']['run'],fixture['binding']['cutoff'],'0.1.0-PG2654/config/templates/api.yml',backup.SLOT,'qualify_backup','ordinaryPgRestoreListExit=0','restorePruneAccepted=False']:self.assertIn(value,raw)


if __name__=='__main__':unittest.main()
