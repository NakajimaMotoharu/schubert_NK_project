"""Fresh829 source after typed-catch/bitmap correction, never replay failed PG5240."""
import pg5240_startup_view_selected as previous

selected=previous.selected
configure=previous.configure
extra_suites=previous.extra_suites


def main():
    configure()
    return selected.main(stem_override='pg5248-startup-view-owner',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=previous.previous.previous.aliases.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
