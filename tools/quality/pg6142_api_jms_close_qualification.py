"""Independent original1950 XML/sixJars/all8511667 and unfiltered static; no PT/build."""
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6140_api_jms_close_selected import inventory, MAIN

SOURCE = 'ad249a5f5a03cb7c4daf963ebafbedf04fb82ef6'


def main():
    cases, _ = inventory()
    return qualify(SOURCE, W/'pg6140-api-jms-close-selected-v1', cases, (1950, 320), MAIN,
        BASE/'PG6132-api-management-stop-qualification-v1/manifest.json',
        'a3f833f1b349e7d701e1f4e4abd790ce166794e5479a2c88eb39830dcb38488d',
        W/'pg6132-api-management-stop-qualification-v1/manifest.safe.json',
        W/'pg6132-api-management-stop-qualification-v1/findings.safe.json',
        'pg6142-api-jms-close-qualification-v1', 'PG6142-api-jms-close-qualification-v1')


if __name__ == '__main__':
    main()
