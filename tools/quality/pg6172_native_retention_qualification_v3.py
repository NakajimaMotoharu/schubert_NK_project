"""Qualify the original25 only after genuine terminal0; no native Root claim."""
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6162_native_ports_static import MAIN
from pg6164_native_retention_selected import inventory

SOURCE='7b6296d5c'


def main():
    from subprocess import check_output
    from pg6164_native_retention_selected import ROOT
    source=check_output(['git','rev-parse',SOURCE],cwd=ROOT,text=True).strip()
    cases,_=inventory()
    return qualify(source,W/'pg6170-native-retention-selected-v3',cases,(25,13),MAIN,
        BASE/'PG6132-api-management-stop-qualification-v1/manifest.json',
        'a3f833f1b349e7d701e1f4e4abd790ce166794e5479a2c88eb39830dcb38488d',
        W/'pg6132-api-management-stop-qualification-v1/manifest.safe.json',
        W/'pg6132-api-management-stop-qualification-v1/findings.safe.json',
        'pg6172-native-retention-qualification-v3','PG6172-native-retention-qualification-v3')


if __name__=='__main__':main()
