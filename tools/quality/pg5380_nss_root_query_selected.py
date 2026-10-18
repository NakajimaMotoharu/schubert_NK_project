"""Nine canonical acquire scopes across NSS bootstrap and Root native process/file reader."""
import pg5372_ffm_progress_selected as previous

selected=previous.selected
aliases=previous.aliases
repetitions=previous.repetitions
REQUIRED={'bootstrap:dev/codex/schubert/nk/bootstrap/FixedServiceIdentity$NativeQuery.class',
    'batch:dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo.class'}
OPTIONAL={'bootstrap:dev/codex/schubert/nk/bootstrap/FixedServiceIdentity.class',
    'bootstrap:dev/codex/schubert/nk/bootstrap/FixedServiceIdentity$Value.class',
    'bootstrap:dev/codex/schubert/nk/bootstrap/FixedServiceIdentity$Query.class',
    'bootstrap:dev/codex/schubert/nk/bootstrap/FixedServiceIdentity$Start.class',
    'batch:dev/codex/schubert/nk/batch/platform/RootStartupContext.class',
    'batch:dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo$LinkRead.class',
    'batch:dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo$UnitQuery.class'}
RELATED={'dev.codex.schubert.nk.batch.platform.RootStartupContextTest':'batch'}
FILES={'FixedServiceIdentity','RootStartupContext'}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|=REQUIRED
    selected.EXTRA_DEBUG|=OPTIONAL


def extra_suites():
    return {**previous.extra_suites(),**RELATED}


if __name__=='__main__':
    configure()
    raise SystemExit(selected.main(stem_override='pg5380-nss-root-query',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases(),case_repetitions=repetitions()))
