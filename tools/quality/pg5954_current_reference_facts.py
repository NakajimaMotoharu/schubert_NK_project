"""Current851 Main-only reference identity facts; no PT or runtime state access."""
import types
import pg5766_reference_identity_facts as engine
from pg5952_current_catch_facts import SOURCE, inputs


def main():
    scope = {**vars(engine), 'SOURCE': SOURCE, 'SLOT': 'pg5954-current-reference-facts-v1', 'inputs': inputs}
    return types.FunctionType(engine.main.__code__, scope, 'current851_reference_facts')()


if __name__ == '__main__':
    main()
