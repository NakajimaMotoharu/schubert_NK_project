"""Current-source688 cases including four independent Morning ownership-transfer tests."""
import pg5192_durable_worker_selected as previous

selected=previous.selected
configure=previous.configure
extra_suites=previous.extra_suites


def main():
    configure()
    return selected.main(stem_override='pg5200-morning-owner',version_override='v1',extra_suites=extra_suites())


if __name__=='__main__':raise SystemExit(main())
