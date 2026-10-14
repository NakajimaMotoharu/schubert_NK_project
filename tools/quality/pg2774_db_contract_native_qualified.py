"""Retained current-source CRC/session streams joined to new full, all member bytes including META."""
import inspect
import pg2746_backup_admission_native_qualification as previous
from pg2770_db_contract_group_full_six import validate


def server():
    raw=previous.server().replace('PG2746','PG2774').replace('PG2744','PG2770').replace('3669','3673').replace(
        'PG2774-native-v2','PG2774-native-v1').replace('qualified2744Tests','qualified2770Tests')
    compile(raw,'<strict current native DB integration>','exec');return raw


def main():
    raw=inspect.getsource(previous.main).replace('pg2745-backup-admission-full-qualified-v1','pg2772-db-contract-full-qualified-v1').replace(
        'pg2746-backup-admission-native-qualified-v2','pg2774-db-contract-native-qualified-v1').replace('3669','3673')
    ns={**previous.__dict__,'validate':validate,'server':server}
    exec(compile(raw,'<retained native new DB group>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
