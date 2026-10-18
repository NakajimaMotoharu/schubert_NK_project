"""Thirteen environment scopes plus prior related642 actual cases; no real credential/VM action."""
import pg5176_backup_selected as backup

selected=backup.selected
PREFIX='batch:dev/codex/schubert/nk/batch/file/'
OUTERS={'InspectorEnvironmentFiles','InspectorEnvironmentReader','InspectorEnvironmentPublisher'}
DEBUG={'InspectorEnvironmentFiles$Roots','InspectorEnvironmentReader$NioIo',
       'InspectorEnvironmentPublisher$NioIo','InspectorEnvironmentPublisher$NioWriter'}
ENVIRONMENT={
 'dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest':'batch',
 'dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest':'batch',
 'dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest':'batch',
}


def configure():
    backup.configure()
    selected.EXTRA_CHANGED|={PREFIX+name+'.class' for name in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+name+'.class' for name in DEBUG}


def extra_suites():
    return {**backup.extra_suites(),**ENVIRONMENT}


def main():
    configure()
    return selected.main(stem_override='pg5184-environment-scopes',version_override='v1',
                         extra_suites=extra_suites())


if __name__=='__main__':raise SystemExit(main())
