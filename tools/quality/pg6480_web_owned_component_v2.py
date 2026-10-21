"""New source/run after BUG1583 Test-only generic Boolean correction; preserve original6470."""
import pg6470_web_owned_component_selected as prior


def main():
    prior.SLOT = 'pg6480-web-owned-component-v2'
    return prior.main()


if __name__ == '__main__':
    raise SystemExit(main())
