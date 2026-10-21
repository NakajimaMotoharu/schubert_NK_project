"""Test-only strict flat Web-source endpoint correction; same compile-first27, fresh source/run."""
import pg6470_web_owned_component_selected as prior


def main():
    prior.SLOT = 'pg6494-web-owned-component-v4'
    prior.COMPILE_BEFORE_PT = True
    return prior.main()


if __name__ == '__main__':
    raise SystemExit(main())
