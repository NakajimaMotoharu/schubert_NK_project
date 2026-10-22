"""Actual legacy Receipt interface counters and independent case, no global/native success import."""
from pathlib import Path
import pg6910_legacy_receipt_selected as profile
from pg5940_private_lock_compile import BASE
from unchanged_selected_evidence import qualify

QSHA = 'b03ac4ea16c71beb4c42f96d3c1e7e5f4282ed64e2ca37f88b3ed9b648f2bd9c'


def main():
    return qualify(profile, 'PG6912-legacy-receipt-original-v1', QSHA, (25, 9),
      BASE / 'PG6890-current4213-cases/qualification.json', '80ad328f6e4f20d2f53f0e6ac4c314c1f698842a7b9b031b14d47592d19123ce',
      ['batch:dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Receipt.class'],
      {profile.TEST: {'retdata001LegacyZeroDoesNotManufactureTypedOrStoppedReceipt': 'PT-OPS-RETDATA-001'}},
      'PG6914-legacy-receipt-qualification-v1', Path(__file__))


if __name__ == '__main__':
    main()
