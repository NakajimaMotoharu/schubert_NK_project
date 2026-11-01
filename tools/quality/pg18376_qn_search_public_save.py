"""Save complete pure question and notification search form proofs."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18376-qn-search-public-save-v1'
save.BEFORE='da439852759cdd576fbee30acc24bb77ac796b6f'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1836','tools/quality/pg1837','tools/quality/architecture/QuestionSearchInputContractTest.java','tools/quality/architecture/NotificationSearchInputContractTest.java','tools/quality/architecture/QuestionNotificationSearch26CurrentJunitLauncher.java')
if __name__=='__main__':save.main()
