"""SSC261 changed Production candidate, selected29; installed D5 stays unchanged."""
import pg1276_private_export_selected as previous
import pg1272_stop_hold_selected as base


def source():
    s=previous.source()
    s=s.replace("'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/NativeCoverageExportTest.java'}", "'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/NativeCoverageExportTest.java','src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.java'}")
    s=s.replace('pg1276-private-export-selected-v1','pg1278-held-channel-selected-v1').replace("'tests':26","'tests':29")
    s=s.replace("'productionSource':SOURCE", "'productionSource':head,'productionBaseline':SOURCE,'installedVmSource':SOURCE,'candidateNotDeployed':True")
    compile(s,'<new-source held channel selected29>', 'exec');return s


def main():
    env=dict(base.__dict__);exec(source(),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
