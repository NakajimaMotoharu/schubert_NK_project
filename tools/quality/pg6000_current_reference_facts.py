"""Fresh current b471 reference symbols, no reflection/Production/operational invocation."""
import types
import pg5766_reference_identity_facts as engine
from pg5998_current_catch_facts import SOURCE, inputs


def main():
    scope={**vars(engine),'SOURCE':SOURCE,'SLOT':'pg6000-current-reference-facts-v1','inputs':inputs}
    return types.FunctionType(engine.main.__code__,scope,'current851_reference_facts')()


if __name__=='__main__':
    raise SystemExit(main())
