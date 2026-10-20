"""Original23 XML/sixJars/all8511667 and unfiltered static; no additional PT/build."""
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6130_api_management_stop_green import inventory, MAIN

SOURCE = 'ca0383ac0729065fe03d4cd4b1303c9afa7e4b21'


def main():
    definitions, _ = inventory()
    return qualify(SOURCE, W/'pg6130-api-management-stop-green-v1', definitions, (23, 9), {MAIN},
        BASE/'PG6114-http-owner-qualification-v1/manifest.json',
        '504e9754e0c815e97a70870d576988c9a7bde3aeabec6427a71bd15657ae1103',
        W/'pg6114-http-owner-qualification-v1/manifest.safe.json',
        W/'pg6114-http-owner-qualification-v1/findings.safe.json',
        'pg6132-api-management-stop-qualification-v1', 'PG6132-api-management-stop-qualification-v1')


if __name__ == '__main__':
    main()
