"""New-only exact SSC304 selection after test-only nested nullable syntax correction."""
import subprocess
import pg4956_expiry_success_selected as role

WORK=role.ROOT.parent/'pgpt-runs/PG379/pg4964-expiry-success-selected-v1'


def main():
    role.validate_selection()
    if subprocess.check_output(['git','status','--porcelain'],cwd=role.ROOT):raise ValueError('clean frozen corrected source first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=role.ROOT,text=True).strip()
    ns={**vars(role.previous.base),'SOURCE':head,'WORK':WORK,'TESTS':list(role.MODULES),'MODULES':role.MODULES,
        'MAIN_SOURCE':head,'METHODS':role.METHODS,'verify_main_bytes':role.verify_main_bytes}
    exec(compile(role.source(),'<SSC304 exact nullability syntax and static ownership>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
