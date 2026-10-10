"""New-only three-suite real held-inode negative PT; frozen test-only source."""
import inspect
import pg1272_stop_hold_selected as previous


def source():
    s=inspect.getsource(previous.main)
    s=s.replace("changes==[TEST]","set(changes)=={TEST,'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageRemovalDuringShutdownProbe.java','src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/NativeCoverageExportTest.java'}")
    s=s.replace('pg1272-stop-hold-selected-v1','pg1276-private-export-selected-v1')
    s=s.replace('-Dtest=FixedNativeCoverageStopHoldTest','-Dtest=FixedNativeCoverageStopHoldTest,NativeCoverageExportTest,NativeCoveragePrivateFileTest')
    begin=s.index("    xml=target/'surefire-reports/TEST-dev.codex.schubert.nk.bootstrap.FixedNativeCoverageStopHoldTest.xml'")
    end=s.index('    static=None;',begin)
    block="""    counts={k:0 for k in ['tests','failures','errors','skipped']};xml_hashes={}
    for suite in ['FixedNativeCoverageStopHoldTest','NativeCoverageExportTest','NativeCoveragePrivateFileTest']:
        xml=target/('surefire-reports/TEST-dev.codex.schubert.nk.bootstrap.'+suite+'.xml')
        if xml.exists():
            if result.returncode==0:require(xml.stat().st_mtime>=start.timestamp())
            root=ET.parse(xml).getroot()
            for k in counts:counts[k]+=int(root.attrib[k])
            xml_hashes[suite]=sha(xml)
            shutil.copy2(xml,run/(suite+'.xml'))
    if not xml_hashes:counts=None
"""
    s=s[:begin]+block+s[end:]
    s=s.replace("'tests':6","'tests':26").replace("'changedTestOnly':[TEST]","'changedTestOnly':changes").replace("'testSha256':sha(T/TEST)","'testOnlySourceHashes':{p:sha(T/p)for p in changes}").replace("'xmlSha256':sha(xml)if xml.exists()else None","'xmlHashes':xml_hashes")
    compile(s,'<actual three-suite frozen private export selected>', 'exec');return s


def main():
    env=dict(previous.__dict__);exec(source(),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
