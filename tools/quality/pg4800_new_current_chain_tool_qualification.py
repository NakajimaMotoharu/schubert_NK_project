"""Unique independent new-campaign tool tests, no business/VM mutations or Production PT."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import unittest
from pyflakes.api import checkPath
from pg1446_current_cold_stage import W
from pg4736_new_normal_root_once import SOURCE

SLOT='pg4800-new-current-chain-tool-qualified-v1'


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    names=['pg4742_same_day_query_oracle_test.Queries','pg2078_current_same_day_rows_oracle_test.SameDay',
           'pg4752_new_current_admission_test.NewAdmission','pg4756_new_current_acceptance_test.Acceptance',
           'pg4762_new_current_browser_test.Browser','pg4768_new_current_composite_test.Composite',
           'pg4772_new_current_owned_test.NormalOwned','pg4780_new_current_native_test.Native']
    paths=[p for p in Path('tools/quality').glob('pg47*.py')if p.name.startswith(('pg4733','pg4742','pg4744','pg4746','pg4748','pg4752','pg4754','pg4756','pg4760','pg4762','pg4764','pg4766','pg4768','pg4770','pg4772','pg4774','pg4776','pg4778','pg4780','pg4782'))]
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    suite=unittest.defaultTestLoader.loadTestsFromNames(names)
    with(out/'tests.private.log').open('x')as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    findings=sum(checkPath(str(p))for p in paths)
    unchanged=hashes=={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
    success=result.wasSuccessful()and not result.skipped and not findings and unchanged
    value={'actualExit':0 if success else 1,'productionSource':SOURCE,'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'hostStaticFindings':findings,'hostSourceHashes':hashes,'logSha256':hashlib.sha256((out/'tests.private.log').read_bytes()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'productionPtAdded':0,'formalAccepted':False,'guestOperationIssued':False}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='hostSourceHashes'}));return value['actualExit']


if __name__=='__main__':raise SystemExit(main())
