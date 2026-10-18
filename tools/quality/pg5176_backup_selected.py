"""Nineteen Backup file-adapter scopes, null=old UNAVAILABLE IO, exact related611 cases."""
import pg5168_release_selected as release

selected=release.selected
PREFIX='batch:dev/codex/schubert/nk/batch/file/'
OUTERS={'BackupArtifactVerifier','BackupManifestPublisher','BackupManifestReader'}
DEBUG={'BackupArtifactVerifier$FileClaim','BackupArtifactVerifier$NioIo','BackupManifestReader$NioIo'}
BACKUP={
 'dev.codex.schubert.nk.batch.file.BackupArtifactVerifierTest':'batch',
 'dev.codex.schubert.nk.batch.file.BackupManifestPublisherTest':'batch',
 'dev.codex.schubert.nk.batch.file.BackupManifestReaderTest':'batch',
 'dev.codex.schubert.nk.batch.file.BackupManifestCodecTest':'batch',
 'dev.codex.schubert.nk.batch.backup.BackupManifestValuesTest':'batch',
}


def configure():
    release.configure()
    selected.EXTRA_CHANGED|={PREFIX+name+'.class' for name in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+name+'.class' for name in DEBUG}


def extra_suites():
    return {**release.bootstrap.bootstrap_suites(),**BACKUP}


def main():
    configure()
    return selected.main(stem_override='pg5176-backup-scopes',version_override='v1',
                         extra_suites=extra_suites())


if __name__=='__main__':raise SystemExit(main())
