"""Meaningful Backup retention rejection matrix against current host candidate, no real Backup operation."""
import inspect
import pg2112_caddy_metadata_selected as transport
from pg2116_caddy_metadata_selected_v3 import server as previous

def server():
    raw=previous().replace('PG2116','PG2120')
    raw=raw.replace('-Dtest=CaddyPublicMetadataTest,CaddyPublicConfigurationTest,CaddyPublicCaMetadataTest,CaddyAddressBoundaryTest','-Dtest=BackupRetentionBoundaryTest,BackupArtifactVerifierTest,MorningBackupRetentionTest')
    raw=raw.replace("['CaddyPublicMetadataTest','CaddyPublicConfigurationTest','CaddyPublicCaMetadataTest','CaddyAddressBoundaryTest']","['BackupRetentionBoundaryTest','BackupArtifactVerifierTest','MorningBackupRetentionTest']")
    raw=raw.replace("counts['dev.codex.schubert.nk.batch.file.CaddyPublicMetadataTest']","counts['dev.codex.schubert.nk.batch.file.BackupRetentionBoundaryTest']")
    raw=raw.replace("=='dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration'","=='dev/codex/schubert/nk/batch/file/BackupArtifactVerifier'")
    compile(raw,'<current Backup retention mandatory scope>','exec');return raw

def main():
    raw=inspect.getsource(transport.main).replace('PG2112','PG2120').replace('pg2112','pg2120')
    ns={**transport.__dict__,'SERVER':server()}
    exec(compile(raw,'<new-only independent Backup host fixture entry>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
