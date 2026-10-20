"""Original1939 XML/all851/all1667/sixJars and unfiltered static; no new tests/build."""
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6112_http_owner_selected import inventory, PATHS

SOURCE = 'acb5fe9c375ede57f5d15fc5fc392f2197c910d4'


def main():
    definitions, _ = inventory()
    return qualify(SOURCE, W/'pg6112-http-owner-selected-v1', definitions, (1939, 318),
        {p for p in PATHS if '/src/main/java/' in p},
        BASE/'PG6108-locked-flag-qualification-v1/manifest.json',
        '8adb610d4bcbcdf3a345cff889e09f988c79607734d524c46f0cb344dfaab218',
        W/'pg6108-locked-flag-qualification-v1/manifest.safe.json',
        W/'pg6108-locked-flag-qualification-v1/findings.safe.json',
        'pg6114-http-owner-qualification-v1', 'PG6114-http-owner-qualification-v1')


if __name__ == '__main__':
    main()
