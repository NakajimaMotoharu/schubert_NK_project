"""Read original combined1955 XML/sixJars/all8511667 and unfiltered static, no PT/build."""
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6150_api_factory_close_selected import inventory, MAIN

SOURCE = '8f0ba4cb06467e5e1c9b25f8360bbc1db4d963ea'


def main():
    cases, _ = inventory()
    return qualify(SOURCE, W/'pg6154-api-factory-close-selected-v2', cases, (1955, 321), MAIN,
        BASE/'PG6132-api-management-stop-qualification-v1/manifest.json',
        'a3f833f1b349e7d701e1f4e4abd790ce166794e5479a2c88eb39830dcb38488d',
        W/'pg6132-api-management-stop-qualification-v1/manifest.safe.json',
        W/'pg6132-api-management-stop-qualification-v1/findings.safe.json',
        'pg6156-api-factory-close-qualification-v2', 'PG6156-api-factory-close-qualification-v2')


if __name__ == '__main__':
    main()
