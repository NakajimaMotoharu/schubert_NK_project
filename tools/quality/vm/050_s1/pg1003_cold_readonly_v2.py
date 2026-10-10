"""Separate fresh readonly attempt after BUG1004; no boot/start/recovery replay."""
import ast
from pg1002_cold_readonly import payload,capture

def source():
    old=payload();assert old.count('pg1002-cold-readonly-v1')==1 and old.count('PG1002-cold-readonly-v1')==1
    new=old.replace('pg1002-cold-readonly-v1','pg1003-cold-readonly-v2').replace('PG1002-cold-readonly-v1','PG1003-cold-readonly-v2')
    assert 'pg1002-cold-readonly-v1'not in new
    assert "v=complete_configuration(raw,name)"in new
    assert 'CONFIG_FIELDS=frozenset' in new and 'FIELDS=set(' in new
    ast.parse(new);return new

if __name__=='__main__':capture('pg1003-cold-readonly-v2',source())
