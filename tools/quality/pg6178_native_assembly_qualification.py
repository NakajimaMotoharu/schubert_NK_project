"""Original49/all Main/Jars/static only; does not execute native process assembly."""
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6174_native_assembly_static import MAIN
from pg6176_native_assembly_selected import inventory

SOURCE='99e7049fbf04fb23aa6c4143a123ca08285a7312'


def main():
    cases,_=inventory()
    return qualify(SOURCE,W/'pg6176-native-assembly-selected-v1',cases,(49,18),MAIN,
        BASE/'PG6172-native-retention-qualification-v3/manifest.json',
        '191c575a681701f34b19aa2c87bcbd1dacf81369987929997c8b45bcc1795fcd',
        W/'pg6172-native-retention-qualification-v3/manifest.safe.json',
        W/'pg6172-native-retention-qualification-v3/findings.safe.json',
        'pg6178-native-assembly-qualification-v1','PG6178-native-assembly-qualification-v1')


if __name__=='__main__':main()
