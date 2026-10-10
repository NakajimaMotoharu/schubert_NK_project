import copy
import json
import unittest
from pg1204_jvm_gc_append_oracle import qualify


def fixture():
    unit='schubert-nk-web.service';prior=[{'__CURSOR':'old-fixed','__MONOTONIC_TIMESTAMP':'100','MESSAGE':'old full record'}]
    messages=['[2026-10-10T18:31:01.071+0000][3399.919s][info][gc,start       ] GC(9) Pause Young (Allocation Failure)',
              '[2026-10-10T18:31:01.081+0000][3399.928s][info][gc,heap        ] GC(9) DefNew: 110281K(118080K)->5722K(118080K) Eden: 105024K(105024K)->0K(105024K) From: 5257K(13056K)->5722K(13056K)',
              '[2026-10-10T18:31:01.081+0000][3399.928s][info][gc,heap        ] GC(9) Tenured: 15923K(262144K)->15923K(262144K)',
              '[2026-10-10T18:31:01.081+0000][3399.928s][info][gc,metaspace   ] GC(9) Metaspace: 53765K(54528K)->53765K(54528K) NonClass: 47971K(48384K)->47971K(48384K) Class: 5794K(6144K)->5794K(6144K)',
              '[2026-10-10T18:31:01.081+0000][3399.928s][info][gc             ] GC(9) Pause Young (Allocation Failure) 123M->21M(371M) 9.744ms',
              '[2026-10-10T18:31:01.081+0000][3399.929s][info][gc,cpu         ] GC(9) User=0.01s Sys=0.00s Real=0.01s']
    rows=[dict(_BOOT_ID='cbca87383b244090b77cbf029677cdd6',_SYSTEMD_UNIT=unit,_SYSTEMD_INVOCATION_ID='898429f0e6a64d4fa7a6c07e4473fe8a',_PID='526861',_UID='997',PRIORITY='6',MESSAGE=m,__CURSOR='new-'+str(i),__MONOTONIC_TIMESTAMP=str(101+i))for i,m in enumerate(messages)]
    encode=lambda x:json.dumps(x,sort_keys=True).encode().hex()
    return unit,prior,rows,encode


class GcTest(unittest.TestCase):
    def test_all_prefix_full_gc_and_complete_negative_matrix(self):
        unit,prior,rows,encode=fixture();old={unit:encode(prior)};new={unit:encode(prior+rows)}
        self.assertEqual(qualify(old,new)['qualifiedInfoGcAppended'],6)
        self.assertEqual(qualify(old,old)['qualifiedInfoGcAppended'],0)
        for k in rows[0]:
            bad=copy.deepcopy(rows);bad[0][k]=''if k=='__CURSOR'else'foreign'
            with self.assertRaises((ValueError,TypeError)):qualify(old,{unit:encode(prior+bad)})
        for bad in [rows[:-1],rows[1:]+rows[:1],rows+rows,rows[:1]*6]:
            with self.assertRaises(ValueError):qualify(old,{unit:encode(prior+bad)})
        bad=copy.deepcopy(prior);bad[0]['MESSAGE']='changed'
        with self.assertRaises(ValueError):qualify(old,{unit:encode(bad+rows)})
        for before,after in [('GC(9)','GC(8)'),('[info]','[warn]'),('9.744ms','-9ms'),('3399.928s','0.928s')]:
            bad=copy.deepcopy(rows);bad[4]['MESSAGE']=bad[4]['MESSAGE'].replace(before,after)
            with self.assertRaises(ValueError):qualify(old,{unit:encode(prior+bad)})


if __name__=='__main__':unittest.main()
