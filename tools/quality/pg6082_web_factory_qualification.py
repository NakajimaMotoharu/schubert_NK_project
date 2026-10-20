"""Original SSC311 Web925 XML/Jars and unfiltered Main static analysis; no build/PT replay."""
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6080_web_factory_selected import inventory, MAIN

SOURCE = '870010d6681d74519237be7a7ca6381a190f471a'


def main():
    definitions, _ = inventory()
    return qualify(SOURCE, W/'pg6086-web-factory-selected-v2', definitions, (925, 150), {MAIN},
        BASE/'PG6076-jms-owner-qualification-v1/manifest.json',
        '4524bb06ba03d4dae2e9f3c5d280bf7fa648967277f7bb07de38142f9f2748c9',
        W/'pg6076-jms-owner-qualification-v1/manifest.safe.json',
        W/'pg6076-jms-owner-qualification-v1/findings.safe.json',
        'pg6082-web-factory-qualification-v1', 'PG6082-web-factory-qualification-v1')


if __name__ == '__main__':
    main()
