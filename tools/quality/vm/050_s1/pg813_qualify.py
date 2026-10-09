"""Independent qualification of actual v2 compile/oracle0; no recompilation or VM."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
import pg813_sources as p
from pg813_compile import refs_source
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
if __name__=='__main__':
 os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain'])
 target=W/'pg813-failed949-tools-v2';manifest=W/'pg813-frozen-v2.safe.json';assert not manifest.exists()
 for phase in('compile','oracle'):assert(W/('pg813-'+phase+'-v2.exit')).read_text()=='0\n'
 assert(W/'pg813-oracle-v2.private.log').read_text()=='PG813_JAVA_ORACLE assertions=77 independent=true nativeMutation0=true productionPT0=true\n'
 for name,source in{'Pg813FailedRecovery.java':p.java(),'Pg813FailedRecoveryTest.java':p.java_test(),'pg813_owned.py':p.helper(),'pg813_refs.py':refs_source()}.items():assert(target/name).read_text()==source
 for name in('Pg797OwnedDatabase.java','Pg797OwnedDatabaseTest.java','Pg798DatabaseScope.java','Pg798DatabaseScopeTest.java'):assert(target/name).read_bytes()==(R/name).read_bytes()
 oracle=(W/'pg813-database-oracle-v2.private.log').read_text();assert 'assertions=307'in oracle and 'assertions=20'in oracle
 hashes=json.loads((target/'payload-sha256.json').read_text());assert set(hashes)=={f.name for f in target.iterdir()}-{'payload-sha256.json'}
 for name,digest in hashes.items():assert hashlib.sha256((target/name).read_bytes()).hexdigest()==digest
 value={'actualExit':0,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':p.SOURCE,'manifestSha256':p.DIGEST,'snapshotSha256':p.SNAPSHOT,'fileHashes':hashes,'qualifiedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualWerrorCompileExit':0,'actualJavaOracleExit':0,'pythonIndependentTests':4,'databaseFaultOracle':True,'productionPTAdded':0,'oldV1Accepted':False,'metadataJoinFailurePreserved':True,'guestMutation0':True,'formalAccepted':False}
 with manifest.open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps({'actualExit':0,'Werror0':True,'javaOracle':77,'databaseFaultOracles':True,'noRecompile':True,'guestActions0':True,'qualifiedSha256':hashlib.sha256(manifest.read_bytes()).hexdigest()}))
