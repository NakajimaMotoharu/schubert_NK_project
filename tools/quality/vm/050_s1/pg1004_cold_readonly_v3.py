"""New-only observer with continuous tenRef scope after BUG1005."""
import ast
from pathlib import Path
from pg1003_cold_readonly_v2 import source as previous
from pg1002_cold_readonly import capture

def source():
    raw=previous().replace('pg1003-cold-readonly-v2','pg1004-cold-readonly-v3').replace('PG1003-cold-readonly-v2','PG1004-cold-readonly-v3')
    helper=Path(__file__).with_name('pg1004_cold_refs.py').read_text()
    start='first=snapshot();second=snapshot();require(first==second)'
    assert raw.count(start)==1
    raw=raw.replace(start,helper+'''
import dbus
metadata_bus=dbus.SystemBus(private=True)
metadata_manager=dbus.Interface(metadata_bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
def observe_pair():
 a=snapshot();b=snapshot();require(a==b);return a
first=with_references(metadata_manager,metadata_bus,list(old['units']),observe_pair)
''')
    assert "'run':'PG1004-cold-readonly-v3'"in raw
    ast.parse(raw);return raw

if __name__=='__main__':capture('pg1004-cold-readonly-v3',source())
