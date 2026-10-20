"""Fresh resolved identity operands, not dynamic PT/native or a rule exemption."""
import types
import pg5766_reference_identity_facts as engine
from pg6094_jms_current_catch_facts import SOURCE, inputs


def main():
    scope = {**vars(engine), 'SOURCE': SOURCE, 'SLOT': 'pg6096-jms-reference-facts-v1', 'inputs': inputs}
    return types.FunctionType(engine.main.__code__, scope, 'current870_reference_facts')()


if __name__ == '__main__':
    raise SystemExit(main())
