import copy
import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5418_readonly_ownership_bytecode as entry


class ReadonlyBytecode(unittest.TestCase):
    def test_all_fourteen_twr_acquisitions_are_explicit_and_complete(self):
        self.assertEqual(sum(sum(row.values()) for row in entry.TWR.values()),14)
        self.assertEqual(len(entry.TWR),3);self.assertEqual(len(entry.CLASSES),6)
        method={'header':'fixture','ops':[(0,'invokestatic','Owner.open:'),(1,'astore_2',''),
            (2,'aload_2',''),(3,'invokevirtual','Owner.action:'),(4,'aload_2',''),(5,'invokevirtual','Owner.close:'),
            (6,'goto','10'),(7,'astore_3',''),(8,'aload_2',''),(9,'invokevirtual','Owner.close:'),(10,'return','')],
            'handlers':[(2,4,7,'Class java/lang/Throwable')]}
        row=entry.twr_site(method,0)
        self.assertEqual(row['registeredLocal'],2);self.assertEqual(row['sameResourceClosePcs'],[5,9])
        self.assertEqual(len(entry.twr_class([method],{'Owner.open:':1})),1)
        for invalid in (dict(method,handlers=[]),dict(method,handlers=[(3,4,7,'Class java/lang/Throwable')]),
            dict(method,ops=method['ops'][:1]+[(1,'invokedynamic','late callback')]+method['ops'][2:]),
            dict(method,ops=[row if row[0]!=8 else (8,'aload_1','') for row in method['ops']])):
            with self.assertRaises(ValueError):entry.twr_site(invalid,0)
        with self.assertRaises(ValueError):entry.twr_class([method],{'Owner.open:':2})

    def test_web_returns_go_directly_into_preexisting_owner_under_four_prebuilt_ports(self):
        pairs=[('WebBrokerContexts.create:','broker'),('WebNativeCodecs.create:','codecs'),
            ('OwnedTransferDirectory.open:','transfer'),('OwnedTransferDirectory.open:','assets'),
            ('ArtemisReplyConsumers.bind:','replies'),('WebLogReplayWorker.start:','replay'),
            ('RevocationRetryWorker.start:','retry'),('WebManagementServer.bind:','management')]
        ops=[]
        for needle,field in pairs:ops.extend([(len(ops),'invokestatic',needle),(len(ops)+1,'putfield','Field '+field+':')])
        runtime=[{'header':'void start();','ops':ops,'handlers':[]},
            {'header':'void httpOwner();','ops':[(0,'aload_0',''),(1,'aload_1',''),(2,'putfield','Field http:'),(3,'return','')],'handlers':[]}]
        call=[{'header':'void caller();','ops':[(0,'invokespecial','WebNativeRuntime."<init>":')]+
            [(index+1,'invokedynamic',kind) for index,kind in enumerate(('WebRuntimeExecution$Start;','WebRuntimeExecution$Io;','java/lang/Runnable;','WebRuntimeExecution$Io;'))]+
            [(5,'invokestatic','WebRuntimeExecution.execute:')],'handlers':[]}]
        execute=[{'header':'void execute();','ops':[(0,'invokeinterface','WebRuntimeExecution$Start.run:'),
            (1,'invokestatic','holdUnknownInterval:'),(2,'goto','1'),(3,'return','')],'handlers':[(0,1,1,'any')]}]
        result=entry.web_proof(runtime,call,execute)
        self.assertEqual(len(result['directResourceFieldStores']),8)
        bad=copy.deepcopy(runtime);bad[0]['ops'][1]=(1,'invokedynamic','late owner')
        with self.assertRaises(ValueError):entry.web_proof(bad,call,execute)
        bad=copy.deepcopy(call);del bad[0]['ops'][2]
        with self.assertRaises(ValueError):entry.web_proof(runtime,bad,execute)
        bad=copy.deepcopy(execute);bad[0]['handlers']=[]
        with self.assertRaises(ValueError):entry.web_proof(runtime,call,bad)

    def test_collector_is_readonly_complete_and_standalone_static(self):
        raw='CLASSES='+repr(entry.CLASSES)+'\n'+inspect.getsource(entry.collector)+'\ncollector()\n'
        self.assertEqual(check(raw,'<readonly six actual classes>'),0)
        self.assertNotIn('write_',raw);self.assertNotIn('.open(',raw)
        for path in (entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
