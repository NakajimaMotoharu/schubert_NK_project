"""New-only actual saved XML topology, keep v1 no-run partial."""
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
 raw=(R/'pg853_before_fix_reference.py').read_text().replace('pg853-beforefix-reference-v1','pg853-beforefix-reference-v2')
 marker="(old/'batch').glob('TEST-*.MaintenanceRunFilesTest.xml')"
 assert raw.count(marker)==1
 return raw.replace(marker,"(old/'batch/surefire-reports').glob('TEST-*.MaintenanceRunFilesTest.xml')")
if __name__=='__main__':exec(compile(source(),'<853 exact frozen830 XML newv2>', 'exec'),{'__file__':str(R/'pg853_before_fix_reference_v2.py'),'__name__':'__main__'})
