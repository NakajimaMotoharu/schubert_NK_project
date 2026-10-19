"""Ordinary finite audit sink PT; existing six-module compile gates and explicit local fixtures."""
import types
import pg5732_enum48_selected as previous

SLOT='pg5738-local-audit-selected-v1'


def main():
    cases={**previous.CASES,'web':{'web.logging.WebAuditSinkContractTest'}}
    return types.FunctionType(previous.main.__code__,{**vars(previous),'SLOT':SLOT,'CASES':cases})()


if __name__=='__main__':raise SystemExit(main())
