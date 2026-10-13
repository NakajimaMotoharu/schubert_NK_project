"""Mandatory Backup metadata/retention selected PT for grouped changed source, no VM action."""
import inspect
import pg2112_caddy_metadata_selected as transport
from pg2116_caddy_metadata_selected_v3 import server as previous

def server():
    raw=previous().replace('PG2116','PG2122')
    raw=raw.replace('-Dtest=CaddyPublicMetadataTest,CaddyPublicConfigurationTest,CaddyPublicCaMetadataTest,CaddyAddressBoundaryTest','-Dtest=MorningBackupMetadataTest,BackupRetentionBoundaryTest,BackupArtifactVerifierTest,MorningBackupRetentionTest')
    raw=raw.replace("['CaddyPublicMetadataTest','CaddyPublicConfigurationTest','CaddyPublicCaMetadataTest','CaddyAddressBoundaryTest']","['MorningBackupMetadataTest','BackupRetentionBoundaryTest','BackupArtifactVerifierTest','MorningBackupRetentionTest']")
    raw=raw.replace("counts['dev.codex.schubert.nk.batch.file.CaddyPublicMetadataTest']","counts['dev.codex.schubert.nk.batch.file.MorningBackupMetadataTest']")
    raw=raw.replace("=='dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration'","=='dev/codex/schubert/nk/batch/file/MorningBackupArtifacts'")
    compile(raw,'<mandatory grouped Backup metadata selection>','exec');return raw

def main():
    raw=inspect.getsource(transport.main).replace('PG2112','PG2122').replace('pg2112','pg2122')
    ns={**transport.__dict__,'SERVER':server()}
    exec(compile(raw,'<new-only grouped Backup metadata entry>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
