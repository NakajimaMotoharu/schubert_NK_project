"""New-only complete schema-corrected SSC305 witness; failed5094 kept immutable."""
import types
import pg5094_failed_phase_full_proof as previous
import pg5092_retained_pair_full_proof as proof

SLOT = 'pg5098-failed-phase-full-proof-v1'


def payload():
    return proof.payload().replace('SLOT=' + repr(proof.SLOT), 'SLOT=' + repr(SLOT), 1)


def main():
    return types.FunctionType(previous.main.__code__, {**vars(previous), 'SLOT': SLOT, 'payload': payload})()


if __name__ == '__main__':
    raise SystemExit(main())
