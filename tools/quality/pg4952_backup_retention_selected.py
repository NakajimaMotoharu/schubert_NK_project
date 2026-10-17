"""BUG1395 fixture fix in a new frozen snapshot; old4950/partial14 retained."""
import subprocess
import pg4950_backup_retention_selected as previous

WORK=previous.ROOT.parent/'pgpt-runs/PG379/pg4952-backup-retention-selected-v1'


def main():
    previous.validate_selection()
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed corrected fixture first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(previous.base),'SOURCE':head,'WORK':WORK,'TESTS':list(previous.MODULES),
        'MODULES':previous.MODULES,'MAIN_SOURCE':previous.MAIN_SOURCE,'METHODS':previous.METHODS,'verify_main_bytes':previous.verify_main_bytes}
    exec(compile(previous.source(),'<new-only109 sameMain actual Guard ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
