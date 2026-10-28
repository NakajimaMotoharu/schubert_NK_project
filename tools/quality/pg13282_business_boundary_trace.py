"""Preserve995 owner/cost/runtime rows; change only eight existing Test source hashes."""
import sys
import pg13270_business_boundary_literal_config as cfg
import f03_literal_batch_trace as core
SOURCE = 'df9dff4c9aa08047a15703e52db9620963211eec'
NORMAL = '1904c7cf76b0a3d7348b12c46715f08f972bb05d065857cfdc980d7d05727a52'
PROOF = '6bcdd66da3f336c70ee82e27c648ec3846ce4e4c82098218f174598e3eb21f45'
def state_after():return core.state_after(cfg)
if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:print(core.emit(cfg,SOURCE,NORMAL,PROOF),end='')
    else:assert not sys.argv[1:];core.main(cfg,SOURCE,NORMAL,PROOF)
