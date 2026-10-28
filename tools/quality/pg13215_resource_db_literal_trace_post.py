"""Independent eight-negative owner/cost/source/runtime and 485/486 preservation check."""
from pg13214_resource_db_literal_trace import cfg,core,SOURCE,NORMAL,PROOF,static_guard

if __name__ == '__main__':
    static_guard();core.post(cfg,SOURCE,NORMAL,PROOF)
