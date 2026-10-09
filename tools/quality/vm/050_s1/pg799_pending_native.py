"""Direct exact799 immutable stage/one publication, no generic activation/revoke/start."""
from pathlib import Path
from pg799_pending_sources import SOURCE,DIGEST
R=Path(__file__).resolve().parent

def source():
 raw=(R/'pg778_native.py').read_text().replace('Pg778FailedRecovery','Pg799PendingDeployment').replace('pg778','pg799').replace('PG778','PG799').replace('pg799-failed758-tools-v1','pg799-pending-tools-v1')
 raw=raw.replace("sys.argv[1]in ('stage','verify','recover')","sys.argv[1]in ('stage','activate')")
 raw=raw.replace("        if action=='recover':assert (W/'pg799-verify-v1.exit').read_text()=='0\\n'\n", "        assert (W/'pg799-candidate-place-v1.exit').read_text()=='0\\n'\n")
 raw=raw.replace("'Pg799PendingDeployment '+action",repr('Pg799PendingDeployment '+SOURCE+' '+DIGEST))
 return raw

if __name__=='__main__':
 import sys
 assert sys.argv[1:]in (['stage'],['activate'])
 exec(compile(source(),'<799 fixed pending immutable native>', 'exec'),{'__file__':str(R/'pg799_pending_native.py'),'__name__':'__main__'})
