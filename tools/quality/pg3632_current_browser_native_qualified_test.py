"""Independent two-generation Inspector pairs; reject missing/duplicate/cross-session/reversed."""
import copy
import unittest
import pg3632_current_browser_native_qualified as p


def fixture():
    points=[{'unit':'ordinary','relative':str(i)}for i in range(20)]
    sessions=[{}for _ in range(20)]
    for start,generation in [(0,'generation-A'),(10,'generation-B')]:
        for i,suffix,dump in [(start,'.closing.exec',30),(start+1,'.terminal.exec',20)]:
            points[i]={'unit':'schubert-nk-inbox-inspector.service','relative':'ordinary-inspector196/'+generation+suffix}
            sessions[i]={'sessionIdSha256':generation,'startMs':10,'dumpMs':dump}
    return points,sessions


class Inspector(unittest.TestCase):
    def test_literal_two_pairs(self):
        self.assertEqual([(0,1),(10,11)],p.inspector_pairs(*fixture()))

    def test_negative_generations_and_times(self):
        a,b=fixture()
        variants=[]
        x=copy.deepcopy(a);x[11]['unit']='ordinary';variants.append((x,b))
        x=copy.deepcopy(a);x[11]=x[10];variants.append((x,b))
        for key,value in [('sessionIdSha256','foreign'),('startMs',9),('dumpMs',31)]:
            y=copy.deepcopy(b);y[1][key]=value;variants.append((a,y))
        y=copy.deepcopy(b);y[10]['sessionIdSha256']=y[11]['sessionIdSha256']='generation-A';variants.append((a,y))
        variants.extend([(a[:10],b[:10]),(a,b[:10]),(a[:19],b[:19]),(a+[a[19]],b+[b[19]]),(None,b)])
        for points,sessions in variants:
            with self.subTest(points=None if points is None else len(points),sessions=len(sessions)):
                with self.assertRaises(ValueError):p.inspector_pairs(points,sessions)

    def test_final_server_and_transport_roles(self):
        raw=p.server();self.assertIn("'currentNativeStreams':18",raw);self.assertIn("'validatedNativePoints':20",raw)
        self.assertIn('PG3632-native-input-v1.tar',raw)
        self.assertNotIn('PG3532-native-v3',raw)
        source=p.source();self.assertIn('old_input[\'selected\']+catalog[\'selected\']',source)
        self.assertIn('pg3632-current-browser-native-qualified-v1',source)


if __name__=='__main__':unittest.main()
