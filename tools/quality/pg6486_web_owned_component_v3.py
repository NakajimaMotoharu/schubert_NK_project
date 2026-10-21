"""Compile every Test before the first selected PT; no warning waiver or original-run replay."""
import pg6470_web_owned_component_selected as prior


def main():
    prior.SLOT = 'pg6486-web-owned-component-v3'
    prior.COMPILE_BEFORE_PT = True
    return prior.main()


if __name__ == '__main__':
    raise SystemExit(main())
