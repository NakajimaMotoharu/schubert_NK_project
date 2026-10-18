"""Six new independent handoff cases in the existing25 storage suites;1011/124 expected."""
import pg5288_morning_launch_selected as previous

selected=previous.selected
aliases=previous.aliases


def configure():
    previous.configure()


def extra_suites():
    return previous.extra_suites()


def main():
    configure()
    return selected.main(stem_override='pg5296-handoff',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
