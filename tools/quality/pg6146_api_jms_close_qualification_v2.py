"""Independent original v2 1950 XML/sixJars/all8511667; no test/build reexecution."""
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6140_api_jms_close_selected import inventory, MAIN

SOURCE = '19c81fcab4e58d3d24f64780c2f7dd5c4dda3912'


def main():
    cases, _ = inventory()
    return qualify(SOURCE, W/'pg6144-api-jms-close-selected-v2', cases, (1950, 320), MAIN,
        BASE/'PG6132-api-management-stop-qualification-v1/manifest.json',
        'a3f833f1b349e7d701e1f4e4abd790ce166794e5479a2c88eb39830dcb38488d',
        W/'pg6132-api-management-stop-qualification-v1/manifest.safe.json',
        W/'pg6132-api-management-stop-qualification-v1/findings.safe.json',
        'pg6146-api-jms-close-qualification-v2', 'PG6146-api-jms-close-qualification-v2')


if __name__ == '__main__':
    main()
