import copy
import stat
import unittest
import pg3504_signed_current_profile_contract as p


def fixture():
    fds = {}
    for n in p.FDS:
        i = int(n)
        mode = stat.S_IFREG | 0o640
        target = p.ROOT + '/operations/lib/f' + n + '.jar'
        flag = 0o100000
        if n in {'0', '1', '2'}:
            mode = stat.S_IFIFO | 0o600; target = 'pipe:[' + str(i) + ']'; flag = 0 if n == '0' else 1
        elif n == '3':
            target = '/opt/jdk-25.0.4/lib/modules'
        elif n == '4':
            target = p.ROOT + '/operations/batch.jar'
        elif n in {'28', '31', '29', '32'}:
            mode = stat.S_IFDIR | 0o755; target = '/run' if n in {'29', '32'} else '/run/schubert-nk'; flag = 0o2700000
        elif n in {'30', '33', '34', '43', '128'}:
            mode = stat.S_IFREG | 0o600; target = '/run/schubert-nk/' + ('startup-admission.lock' if n in {'43', '128'} else 'maintenance.lock'); flag = 0o12400000 if n in {'30', '33'} else 0o2100000
        elif n in {'35', '36'}:
            mode = stat.S_IFCHR | 0o666; target = '/dev/random' if n == '35' else '/dev/urandom'
        fds[n] = {'target': target, 'metadata': [1, i + 1, 0, 0, mode, 1, 0 if n in {'30', '33', '34', '43', '128'} else 1, 10, 10], 'fdinfo': 'pos:\t0\nflags:\t' + oct(flag)[2:] + '\n'}
    fds['32'] = copy.deepcopy(fds['29'])
    fields = {k: '0' for k in p.AUTHORITY}; fields['Uid'] = fields['Gid'] = '0 0 0 0'
    return {'pid':410196, 'ppid':410194, 'ticks':8469964, 'argvSha256':'7da390fc72f2f1fa5ceaa6fdb5c797e1dea89f20409f10dfa2f3b831f92036e3', 'argv':['java','Pg3490NativeStop','stop'], 'exe':'/opt/jdk-25.0.4/bin/java', 'status':'\n'.join(k+':\t'+v for k,v in fields.items()), 'root':'/', 'cgroup':'actual', 'fds':fds, 'children':[]}


class CompleteSignedCurrent39(unittest.TestCase):
    def test_exact_and_only_two_shared_chrono(self):
        a = fixture(); self.assertTrue(p.fresh39(a, copy.deepcopy(a), 12))
        b = copy.deepcopy(a)
        for n in ['29','32']: b['fds'][n]['metadata'][7:] = [11,12]
        self.assertTrue(p.fresh39(a,b,12))
        for value in [None, False, -1, 11]:
            with self.assertRaises(ValueError):p.fresh39(a,b,value)

    def test_each_descriptor_missing_target_metadata_flag_and_fdinfo_refused(self):
        a = fixture()
        for n in p.FDS:
            for mutation in ['missing','target','metadata','flags','fdinfo']:
                b=copy.deepcopy(a)
                if mutation=='missing':del b['fds'][n]
                elif mutation=='target':b['fds'][n]['target']+='foreign'
                elif mutation=='metadata':b['fds'][n]['metadata'][1]+=1
                elif mutation=='flags':b['fds'][n]['fdinfo']='flags:\t02\n'
                else:b['fds'][n]['fdinfo']+='unknown: 1\n'
                with self.subTest(fd=n,mutation=mutation),self.assertRaises(ValueError):p.fresh39(a,b,12)

    def test_identity_child_authority_unknown_and_backward_time_refused(self):
        a=fixture()
        for key,value in [('pid',410197),('ticks',1),('root','/other'),('children',[1]),('status','Uid: 0 0 0 0')]:
            b=copy.deepcopy(a);b[key]=value
            with self.assertRaises(ValueError):p.fresh39(a,b,12)
        for n in ['29','32']:
            b=copy.deepcopy(a);b['fds'][n]['metadata'][7]=9
            with self.assertRaises(ValueError):p.fresh39(a,b,12)
        b=copy.deepcopy(a);b['fds']['99']=copy.deepcopy(b['fds']['0'])
        with self.assertRaises(ValueError):p.fresh39(a,b,12)


if __name__ == '__main__':unittest.main()
