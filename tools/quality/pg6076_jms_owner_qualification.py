"""Independent1933 original artifacts plus static Main analysis,no extra build/PT or runtime."""
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6074_jms_owner_selected import inventory, MAIN

SOURCE = 'fa8580ce15a0292624cac2a12228abf1bcc79d1c'


def main():
    definitions, _ = inventory()
    return qualify(SOURCE, W/'pg6074-jms-owner-selected-v1', definitions, (1933, 317), MAIN,
        BASE/'PG6054-expiry-read-qualification-v1/manifest.json',
        '9f1269de6b66c0be2467aab5de164e82553f03d33dc79f5212e410ff4f1daee9',
        W/'pg6054-expiry-read-qualification-v1/manifest.safe.json',
        W/'pg6054-expiry-read-qualification-v1/findings.safe.json',
        'pg6076-jms-owner-qualification-v1', 'PG6076-jms-owner-qualification-v1')


if __name__ == '__main__':
    main()
