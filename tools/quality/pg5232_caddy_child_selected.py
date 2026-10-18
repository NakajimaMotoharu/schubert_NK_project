"""Caddy3/Child NativeIo1 factories, all bootstrap cases plus3 Caddy cases;812/96 expected."""
import pg5224_current_permit_selected as previous

selected=previous.selected
KEYS={'batch:dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration.class',
      'bootstrap:dev/codex/schubert/nk/bootstrap/ChildStartupContext$NativeIo.class'}
CADDY={'dev.codex.schubert.nk.batch.file.CaddyPublicConfigurationTest':'batch'}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|=KEYS


def extra_suites():
    return {**previous.extra_suites(),**CADDY}


def main():
    configure()
    return selected.main(stem_override='pg5232-caddy-child',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=previous.aliases.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
