#!/usr/bin/env python3
"""PT-QA-TRACE-002/003 independent inventory/run/failure canaries; no production secrets."""
import copy
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
import bootstrap_ownership
from pgpt_evidence_destination import CANDIDATE_ROOT_ENV, evidence_output_root


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


media = module("media_collector", "009_collect_media_evidence.py")
gate = module("set_collector", "018_collect_verified_evidence_set.py")
batch = module("batch_collector", "020_collect_batch_evidence.py")
inspection = module("inspection_collector", "016_collect_inbox_inspection_evidence.py")
database = module("inspector_database_collector", "021_collect_inspector_database_evidence.py")
launch = module("inspector_launch_collector", "022_collect_inspector_launch_evidence.py")
backup = module("backup_rerun_collector", "023_collect_backup_rerun_evidence.py")
references = module("run_reference_collector", "024_collect_run_reference_evidence.py")
parent_summary = module("parent_summary_collector", "025_collect_parent_summary_evidence.py")
atomic = module("atomic_collector", "026_collect_atomic_cleanup_evidence.py")
expiry = module("expiry_audit_collector", "037_collect_expiry_audit_database.py")
request_sender = module("request_sender_resource_collector", "038_collect_request_sender_resource.py")
jms_compounds = module("jms_resource_compound_collector", "039_collect_jms_resource_compounds.py")
log_vertical = module("log_replay_vertical_collector", "040_collect_log_replay_vertical.py")
scenario = module("scenario_collector", "006_collect_scenario_evidence.py")


class EvidenceSetTest(unittest.TestCase):
    def test_web_log_jdbc_resource_suite_canaries(self):
        expected = ("PT-IDEM-012-R02", "PT-IDEM-012-R03", "PT-IDEM-012-R04",
                    "PT-IDEM-012-R05")
        self.assertEqual(expected, tuple(log_vertical.RESOURCE_METHODS))
        suite = ET.Element("testsuite", name=log_vertical.RESOURCE_CLASS,
                           tests="9", failures="0", errors="0", skipped="0")
        for name in log_vertical.RESOURCE_METHODS.values():
            ET.SubElement(suite, "testcase", classname=log_vertical.RESOURCE_CLASS,
                          name=name)
        for index in range(5):
            ET.SubElement(suite, "testcase", classname=log_vertical.RESOURCE_CLASS,
                          name=f"existing{index}")
        self.assertEqual(expected, tuple(log_vertical.validate_resource_suite(suite)))
        for key, value in (("tests", "8"), ("failures", "1"), ("errors", "1"),
                           ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError):
                log_vertical.validate_resource_suite(wrong)
        for mutation in ("missing", "duplicate", "failed", "renamed"):
            wrong = copy.deepcopy(suite)
            if mutation == "missing":
                wrong.remove(wrong[0])
            elif mutation == "duplicate":
                wrong[-1].set("name", wrong[0].get("name"))
            elif mutation == "failed":
                ET.SubElement(wrong[0], "failure")
            else:
                wrong[0].set("name", "wrong-name")
            with self.assertRaises(ValueError):
                log_vertical.validate_resource_suite(wrong)

    def test_jms_resource_compound_inventory_and_coverage(self):
        self.assertEqual(("PT-JMS-021", "PT-IDEM-010-R01", "PT-IDEM-010-R02",
                          "PT-IDEM-010-R03", "PT-IDEM-010-R04", "PT-IDEM-010-R05",
                          "PT-IDEM-012-R01"),
                         tuple(subject[0] for subject in jms_compounds.SUBJECTS))
        for test_id, program, folder, module_name, class_name, method, count, subject in jms_compounds.SUBJECTS:
            self.assertTrue(test_id.startswith("PT-"))
            self.assertTrue(program in ("NK-MSG-001", "NK-MSG-002"))
            self.assertEqual("NK-MSG-001" if folder.startswith("005") else "NK-MSG-002", program)
            self.assertIn(module_name, ("api", "web"))
            suite = ET.Element("testsuite", name=class_name, tests=str(count),
                               failures="0", errors="0", skipped="0")
            ET.SubElement(suite, "testcase", classname=class_name, name=method)
            for index in range(count - 1):
                ET.SubElement(suite, "testcase", classname=class_name, name=f"existing{index}")
            self.assertEqual(class_name + "#" + method,
                             jms_compounds.validate_suite(suite, class_name, method, count))
            for key, bad in (("tests", str(count - 1)), ("failures", "1"),
                             ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, bad)
                with self.assertRaises(ValueError):
                    jms_compounds.validate_suite(wrong, class_name, method, count)
            wrong = copy.deepcopy(suite); wrong[0].set("name", "unlisted")
            with self.assertRaises(ValueError):
                jms_compounds.validate_suite(wrong, class_name, method, count)
            wrong = copy.deepcopy(suite)
            wrong[0].set("name", method.removesuffix("(Path)") if method.endswith("(Path)")
                         else method + "(Path)")
            with self.assertRaises(ValueError):
                jms_compounds.validate_suite(wrong, class_name, method, count)
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], "failure")
            with self.assertRaises(ValueError):
                jms_compounds.validate_suite(wrong, class_name, method, count)
            report = ET.Element("report")
            cls = ET.SubElement(report, "class", name=subject)
            for kind in ("INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH"):
                ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
            self.assertEqual(5, len(jms_compounds.validate_coverage(report, subject)))
            for counter in cls.findall("counter"):
                wrong = copy.deepcopy(report)
                next(c for c in wrong.iter("counter") if c.get("type") == counter.get("type")).set("missed", "1")
                with self.assertRaises(ValueError):
                    jms_compounds.validate_coverage(wrong, subject)

    def test_request_sender_resource_inventory_and_coverage(self):
        self.assertEqual(("PT-JMS-020-A", "PT-JMS-020-B", "PT-JMS-020-C", "PT-JMS-020-D"),
                         tuple(request_sender.METHODS))
        suite = ET.Element("testsuite", name=request_sender.CLASS, tests="7", failures="0",
                           errors="0", skipped="0")
        for name in (*request_sender.BASE_METHODS, *request_sender.METHODS.values()):
            ET.SubElement(suite, "testcase", classname=request_sender.CLASS, name=name)
        self.assertEqual(4, len(request_sender.validate_suite(suite)))
        for key, bad in (("tests", "6"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, bad)
            with self.assertRaises(ValueError): request_sender.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[0].set("name", "unlisted")
        with self.assertRaises(ValueError): request_sender.validate_suite(wrong)
        wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], "failure")
        with self.assertRaises(ValueError): request_sender.validate_suite(wrong)
        report = ET.Element("report")
        cls = ET.SubElement(report, "class", name=request_sender.SUBJECT)
        for kind in ("INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH"):
            ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        self.assertEqual(5, len(request_sender.validate_coverage(report)))
        for counter in cls.findall("counter"):
            wrong = copy.deepcopy(report)
            next(c for c in wrong.iter("counter") if c.get("type") == counter.get("type")).set("missed", "1")
            with self.assertRaises(ValueError): request_sender.validate_coverage(wrong)

    def test_expiry_audit_sql_method_inventory_and_oracle(self):
        self.assertEqual({"PT-DB-016", "PT-DB-017", "PT-DB-018"}, set(expiry.METHODS))
        self.assertEqual(3, len(expiry.ORACLE.splitlines()))
        suite = ET.Element("testsuite", name=expiry.CLASS, tests="18", failures="0",
                           errors="0", skipped="0")
        for name in (*expiry.METHODS.values(), *(f"other{i}" for i in range(15))):
            ET.SubElement(suite, "testcase", classname=expiry.CLASS, name=name)
        self.assertEqual({key: expiry.CLASS + "#" + name for key, name in expiry.METHODS.items()},
                         expiry.validate_suite(suite))
        for key, bad in (("tests", "17"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, bad)
            with self.assertRaises(ValueError): expiry.validate_suite(wrong)
        for name in (list(expiry.METHODS.values())[1], "other0"):
            wrong = copy.deepcopy(suite); wrong[0].set("name", name)
            with self.assertRaises(ValueError): expiry.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[0].set("classname", "unknown")
        with self.assertRaises(ValueError): expiry.validate_suite(wrong)
        wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], "failure")
        with self.assertRaises(ValueError): expiry.validate_suite(wrong)

    def test_api_dependency_readiness_inventory_and_branch_coverage(self):
        runtime = module("api_log_path_runtime_collector", "036_collect_api_log_path_runtime.py")
        names = (
            "realPostgresAndBothReceiveQueuesCloseAfterProbe",
            "nullAndInvalidDatabaseFailBeforeBroker",
            "jdbcInspectionAndCloseFailuresAreRedacted",
            "brokerNullModeAttachAndCloseFailuresAreRedacted",
            "stoppedBrokerCannotPassConnectivity",
            "apiReadinessFatalBrokerCloseCannotBeDowngradedToOrdinaryUnavailable",
            "apiReadinessOrdinaryInspectionAndCloseFailuresRemainRedacted",
            "apiReadinessFatalInspectionRetainsIdentityEvenWhenCloseAlsoFatal",
            "apiReadinessFatalDatabaseCloseCannotBeDowngradedToOrdinaryUnavailable",
            "apiReadinessOrdinaryDatabaseInspectionAndCloseFailuresRemainRedacted",
            "apiReadinessFatalDatabaseInspectionRetainsIdentityEvenWhenCloseAlsoFatal",
        )
        self.assertEqual(names, runtime.READY_METHODS)
        suite = ET.Element("testsuite", name=runtime.READY_CLASS, tests="11",
                           failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=runtime.READY_CLASS, name=name)
        self.assertEqual({"PT-JMS-019-A", "PT-JMS-019-B", "PT-JMS-019-C", "PT-JMS-019-D",
                          "PT-JMS-019-E", "PT-JMS-022-A", "PT-JMS-022-B", "PT-JMS-022-C",
                          "PT-JMS-023-A", "PT-JMS-023-B", "PT-JMS-023-C"},
                         set(runtime.validate_ready_suite(suite)))
        for key, value in (("tests", "10"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): runtime.validate_ready_suite(wrong)
        for replacement in (names[1], "unlisted"):
            wrong = copy.deepcopy(suite); wrong[0].set("name", replacement)
            with self.assertRaises(ValueError): runtime.validate_ready_suite(wrong)
        report = ET.Element("report")
        cls = ET.SubElement(report, "class", name=runtime.READY_SUBJECT)
        for kind in ("INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH"):
            ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        self.assertEqual(5, len(runtime.validate_ready_coverage(report)))
        for counter in cls.findall("counter"):
            wrong = copy.deepcopy(report)
            matching = next(c for c in wrong.iter("counter") if c.get("type") == counter.get("type"))
            matching.set("missed", "1")
            with self.assertRaises(ValueError): runtime.validate_ready_coverage(wrong)

    def test_api_log_path_runtime_inventory_and_coverage(self):
        runtime = module("api_log_path_runtime_collector", "036_collect_api_log_path_runtime.py")
        names = (
            "realDatabaseAndBrokerBindThreeRoutesAndTerminal(Path)",
            "allDependenciesFailBeforeOpeningConsumer",
            "failedConsumerStartupDoesNotReturnPartialRuntime",
        )
        self.assertEqual(names, runtime.METHODS)
        suite = ET.Element("testsuite", name=runtime.CLASS, tests="3",
                           failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=runtime.CLASS, name=name)
        self.assertEqual(3, len(runtime.validate_suite(suite)))
        for key, value in (("tests", "2"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): runtime.validate_suite(wrong)
        for replacement in (names[1], "unlisted"):
            wrong = copy.deepcopy(suite); wrong[0].set("name", replacement)
            with self.assertRaises(ValueError): runtime.validate_suite(wrong)
        report = ET.Element("report")
        cls = ET.SubElement(report, "class", name=runtime.SUBJECT)
        for kind in ("INSTRUCTION", "LINE", "METHOD", "CLASS"):
            ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        self.assertEqual(4, len(runtime.validate_coverage(report)))
        for counter in cls.findall("counter"):
            wrong = copy.deepcopy(report)
            matching = next(c for c in wrong.iter("counter") if c.get("type") == counter.get("type"))
            matching.set("missed", "1")
            with self.assertRaises(ValueError): runtime.validate_coverage(wrong)
        branch = ET.SubElement(cls, "counter", type="BRANCH", missed="0", covered="2")
        self.assertEqual(5, len(runtime.validate_coverage(report)))
        branch.set("missed", "1")
        with self.assertRaises(ValueError): runtime.validate_coverage(report)

    def test_log_path_router_inventory_and_coverage(self):
        router = module("log_path_router_collector", "035_collect_log_path_router.py")
        names = (
            "exactThreeLayoutsReachOnlyTheirRegisteredProcessor",
            "validButUnregisteredLayoutIsRetryableNotPermanentDlq",
            "nullInputsAndNullReplyAreRejectedAtTheirBoundary",
            "delegateFailureClassificationIsNotRewritten",
            "concurrentDispatchDoesNotShareMutableRoutingState",
        )
        self.assertEqual(names, router.METHODS)
        suite = ET.Element("testsuite", name=router.CLASS, tests="5",
                           failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=router.CLASS, name=name)
        self.assertEqual(5, len(router.validate_suite(suite)))
        for key, value in (("tests", "4"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): router.validate_suite(wrong)
        for replacement in (names[1], "unlisted"):
            wrong = copy.deepcopy(suite); wrong[0].set("name", replacement)
            with self.assertRaises(ValueError): router.validate_suite(wrong)
        report = ET.Element("report")
        cls = ET.SubElement(report, "class", name=router.SUBJECT)
        for kind in ("INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH"):
            ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        self.assertEqual(5, len(router.validate_coverage(report)))
        for counter in cls.findall("counter"):
            wrong = copy.deepcopy(report)
            matching = next(c for c in wrong.iter("counter") if c.get("type") == counter.get("type"))
            matching.set("missed", "1")
            with self.assertRaises(ValueError): router.validate_coverage(wrong)

    def test_web_log_runtime_inventory_and_negative_status(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = screen.WEB_LOG_RUNTIME_CLASS
        names = (
            "scr127RealReplyWorkerAndSecuredLogMvcStartAndClose",
            "scr128InvalidReplyDlqMakesWholeRuntimeNotReady",
            "scr129PartialStartupClosesReplyConsumer",
            "scr130LifecycleAggregatesCloseFailuresAndReadinessBoundaries",
            "scr131StartupNullContractsAndSuppressedCleanup",
            "scr133SameThrowableAcrossOwnedClosuresKeepsPrimary",
            "scr134RealHttpLoginUsesProductionApiBrokerAndSession",
            "scr135RealHttpAdminLogSearchUsesProductionApiBroker",
        )
        self.assertEqual(names, screen.WEB_LOG_RUNTIME_METHODS)
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-SCR-{i:03}": cls + "#" + name
                          for i, name in zip((127, 128, 129, 130, 131, 133, 134, 135), names)},
                         screen.validate_web_log_runtime_suite(suite))
        for key, value in (("tests", "5"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): screen.validate_web_log_runtime_suite(wrong)
        for replacement in (names[1], "scr127RealReplyWorkerAndSecuredLogMvcStartAndClose(Path)", "unlisted"):
            wrong = copy.deepcopy(suite); wrong[0].set("name", replacement)
            with self.assertRaises(ValueError): screen.validate_web_log_runtime_suite(wrong)

    def test_web_runtime_dependency_inventory_and_negative_status(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = screen.WEB_RUNTIME_DEPENDENCY_CLASS
        name = "scr132RuntimePostgresDriverAndScopeCanaries"
        self.assertEqual((name,), screen.WEB_RUNTIME_DEPENDENCY_METHODS)
        suite = ET.Element("testsuite", name=cls, tests="1", failures="0", errors="0", skipped="0")
        ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({"PT-SCR-132": cls + "#" + name},
                         screen.validate_web_runtime_dependency_suite(suite))
        for key, value in (("tests", "0"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): screen.validate_web_runtime_dependency_suite(wrong)
        for replacement in ("unlisted", name + "(Path)"):
            wrong = copy.deepcopy(suite); wrong[0].set("name", replacement)
            with self.assertRaises(ValueError): screen.validate_web_runtime_dependency_suite(wrong)

    def test_real_log_replay_vertical_inventory_and_negative_coverage(self):
        vertical = module("log_replay_vertical", "040_collect_log_replay_vertical.py")
        suite = ET.Element("testsuite", name=vertical.CLASS, tests="1",
                           failures="0", errors="0", skipped="0")
        ET.SubElement(suite, "testcase", classname=vertical.CLASS, name=vertical.METHOD)
        self.assertEqual({"PT-IDEM-016": vertical.CLASS + "#" + vertical.METHOD},
                         vertical.validate_suite(suite))
        for key, value in (("tests", "0"), ("failures", "1"), ("errors", "1"),
                           ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): vertical.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[0].set("name", "unlisted")
        with self.assertRaises(ValueError): vertical.validate_suite(wrong)
        report = ET.Element("report")
        candidate = ET.SubElement(report, "class", name=vertical.SUBJECTS[0][1])
        for counter in ("INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH"):
            ET.SubElement(candidate, "counter", type=counter, covered="1", missed="0")
        self.assertEqual(5, len(vertical.validate_coverage(report, vertical.SUBJECTS[0][1])))
        bad = copy.deepcopy(report); bad[0][4].set("missed", "1")
        with self.assertRaises(ValueError): vertical.validate_coverage(bad, vertical.SUBJECTS[0][1])
        branchless = copy.deepcopy(report); branchless[0].remove(branchless[0][4])
        self.assertEqual(4, len(vertical.validate_coverage(branchless, vertical.SUBJECTS[0][1])))

    def test_api_messaging_parent_inventory_and_coverage(self):
        parent = module("api_messaging_parent_collector", "034_collect_api_messaging_runtime.py")
        names = (
            "opensFiveConsumersAndSignalsOneTerminalAcrossGroups(Path)",
            "validatesAllPortsBeforeOpeningAnyContext",
            "fifthContextFailureClosesFourEarlierContexts",
            "failedSecondStartupPreservesFirstCloseFailure",
            "closeAttemptsBothGroupsAndPreservesBothFailures",
            "closeHandlesOnlySyncFailure",
        )
        self.assertEqual(names, parent.METHODS)
        suite = ET.Element("testsuite", name=parent.CLASS, tests="6",
                           failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=parent.CLASS, name=name)
        self.assertEqual(6, len(parent.validate_suite(suite)))
        for key, value in (("tests", "5"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): parent.validate_suite(wrong)
        for replacement in (names[1], "opensFiveConsumersAndSignalsOneTerminalAcrossGroups", "unlisted"):
            wrong = copy.deepcopy(suite); wrong[0].set("name", replacement)
            with self.assertRaises(ValueError): parent.validate_suite(wrong)
        report = ET.Element("report")
        cls = ET.SubElement(report, "class", name=parent.SUBJECT)
        for kind in ("INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH"):
            ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        self.assertEqual(5, len(parent.validate_coverage(report)))
        for counter in cls.findall("counter"):
            for field, value in (("missed", "1"), ("covered", "0")):
                wrong = copy.deepcopy(report)
                matching = next(c for c in wrong.iter("counter") if c.get("type") == counter.get("type"))
                matching.set(field, value)
                with self.assertRaises(ValueError): parent.validate_coverage(wrong)

    def test_api_web_log_consumer_inventory_and_coverage(self):
        log = module("api_web_log_consumer_collector", "033_collect_api_web_log_consumers.py")
        names = (
            "oneConsumerCommitsValidatedWebLog(Path)",
            "temporaryProcessorFailureRollsBackAndRedelivers(Path)",
            "permanentInvalidEventsCommitDlqAndSignalTerminalOnce(Path)",
            "startupRejectsNullAndWrongModeBeforeDelivery(Path)",
            "closeIsIdempotentAndStartupPreservesCloseFailure",
        )
        self.assertEqual(names, log.METHODS)
        suite = ET.Element("testsuite", name=log.CLASS, tests="5",
                           failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=log.CLASS, name=name)
        self.assertEqual(5, len(log.validate_suite(suite)))
        for key, value in (("tests", "4"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): log.validate_suite(wrong)
        for replacement in (names[1], "oneConsumerCommitsValidatedWebLog", "unlisted"):
            wrong = copy.deepcopy(suite); wrong[0].set("name", replacement)
            with self.assertRaises(ValueError): log.validate_suite(wrong)
        report = ET.Element("report")
        cls = ET.SubElement(report, "class", name=log.SUBJECT)
        for kind in ("INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH"):
            ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        self.assertEqual(5, len(log.validate_coverage(report)))
        for counter in cls.findall("counter"):
            for field, value in (("missed", "1"), ("covered", "0")):
                wrong = copy.deepcopy(report)
                matching = next(c for c in wrong.iter("counter") if c.get("type") == counter.get("type"))
                matching.set(field, value)
                with self.assertRaises(ValueError): log.validate_coverage(wrong)

    def test_web_log_worker_inventory_and_coverage(self):
        worker = module("web_log_worker_collector", "032_collect_web_log_worker.py")
        actual_surefire_names = (
            "realOutboxRetriesInBackgroundAndSendsOnce",
            "temporarySqlAndRuntimeFailuresRecoverWithoutLeakingDetails",
            "fatalVmFailureMakesWorkerNotReadyWithoutExposingCause",
            "closeIsIdempotentAndRejectsInvalidInputs",
            "boundedStopReportsUnresponsiveWorkerThenReleases",
            "interruptedStopRestoresCallerFlag",
        )
        self.assertEqual(actual_surefire_names, worker.METHODS)
        suite = ET.Element("testsuite", name=worker.CLASS, tests="6",
                           failures="0", errors="0", skipped="0")
        for method in actual_surefire_names:
            ET.SubElement(suite, "testcase", classname=worker.CLASS, name=method)
        self.assertEqual(6, len(worker.validate_suite(suite)))
        for key, value in (("tests", "5"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): worker.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): worker.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[0].set("name", "unlisted")
        with self.assertRaises(ValueError): worker.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[0].set("name", "realOutboxRetriesInBackgroundAndSendsOnce(Path)")
        with self.assertRaises(ValueError): worker.validate_suite(wrong)
        report = ET.Element("report")
        for subject in worker.SUBJECTS:
            cls = ET.SubElement(report, "class", name=subject)
            for kind in ("LINE", "METHOD", "CLASS", "BRANCH"):
                ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        self.assertEqual(2, len(worker.validate_coverage(report)))
        for subject in worker.SUBJECTS:
            for kind in ("LINE", "METHOD", "CLASS", "BRANCH"):
                for field, value in (("missed", "1"), ("covered", "0")):
                    wrong = copy.deepcopy(report)
                    matching = next(c for c in wrong.iter("class") if c.get("name") == subject)
                    next(c for c in matching.findall("counter") if c.get("type") == kind).set(field, value)
                    with self.assertRaises(ValueError): worker.validate_coverage(wrong)

    def test_web_reply_consumer_inventory_and_coverage(self):
        reply = module("web_reply_consumer_collector", "031_collect_web_reply_consumers.py")
        actual_surefire_names = (
            "oneConsumerDeliversActiveAndLateReplies(Path)",
            "invalidRepliesAreCommittedToDlqAndTerminalIsSignalledOnce(Path)",
            "startupRejectsNullAndWrongModeAndClosesPartialSession(Path)",
            "closeIsIdempotentAndPreservesStartupAndCloseFailures",
            "temporaryReadFailureRollsBackAndLeavesRuntimeReady",
        )
        self.assertEqual(actual_surefire_names, reply.METHODS)
        suite = ET.Element("testsuite", name=reply.CLASS, tests=str(len(reply.METHODS)),
                           failures="0", errors="0", skipped="0")
        for method in actual_surefire_names:
            ET.SubElement(suite, "testcase", classname=reply.CLASS, name=method)
        self.assertEqual(5, len(reply.validate_suite(suite)))
        for key, value in (("tests", "4"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): reply.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): reply.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[0].set("name", "unlisted")
        with self.assertRaises(ValueError): reply.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[0].set("name", "oneConsumerDeliversActiveAndLateReplies")
        with self.assertRaises(ValueError): reply.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[-1].set("name", "temporaryReadFailureRollsBackAndLeavesRuntimeReady(Path)")
        with self.assertRaises(ValueError): reply.validate_suite(wrong)
        report = ET.Element("report")
        cls = ET.SubElement(report, "class", name=reply.SUBJECT)
        for kind in ("LINE", "METHOD", "CLASS", "BRANCH"):
            ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        self.assertEqual(4, len(reply.validate_coverage(report)))
        for counter in cls.findall("counter"):
            for field, value in (("missed", "1"), ("covered", "0")):
                wrong = copy.deepcopy(report)
                matching = next(c for c in wrong.iter("counter") if c.get("type") == counter.get("type"))
                matching.set(field, value)
                with self.assertRaises(ValueError): reply.validate_coverage(wrong)

    def test_api_sync_consumer_inventory_and_coverage(self):
        sync = module("sync_consumer_collector", "030_collect_sync_consumers.py")
        actual_surefire_names = (
            "fourConsumersReceiveAndCommitOneReply(Path)",
            "invalidMessageCommitsToDlqAndSignalsTerminal(Path)",
            "partialStartupRejectsWrongSessionAndClosesAll(Path)",
            "temporaryBusinessFailureRollsBackAndRedelivers(Path)",
            "closeIsIdempotentAndAggregatesAllContextFailures",
            "failedStartupPreservesClosingFailureAsSuppressed",
        )
        self.assertEqual(actual_surefire_names, sync.METHODS)
        suite = ET.Element("testsuite", name=sync.CLASS, tests=str(len(sync.METHODS)),
                           failures="0", errors="0", skipped="0")
        for method in actual_surefire_names:
            ET.SubElement(suite, "testcase", classname=sync.CLASS, name=method)
        self.assertEqual(6, len(sync.validate_suite(suite)))
        for key, value in (("tests", "5"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): sync.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): sync.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[0].set("name", "unlisted")
        with self.assertRaises(ValueError): sync.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[0].set("name", "fourConsumersReceiveAndCommitOneReply")
        with self.assertRaises(ValueError): sync.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[-1].set("name", "failedStartupPreservesClosingFailureAsSuppressed(Path)")
        with self.assertRaises(ValueError): sync.validate_suite(wrong)
        report = ET.Element("report")
        cls = ET.SubElement(report, "class", name=sync.SUBJECT)
        for kind in ("LINE", "METHOD", "CLASS", "BRANCH"):
            ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        self.assertEqual(4, len(sync.validate_coverage(report)))
        for counter in cls.findall("counter"):
            for field, value in (("missed", "1"), ("covered", "0")):
                wrong = copy.deepcopy(report)
                matching = next(c for c in wrong.iter("counter") if c.get("type") == counter.get("type"))
                matching.set(field, value)
                with self.assertRaises(ValueError): sync.validate_coverage(wrong)

    def test_authentication_resource_method_inventory(self):
        auth = module("auth_collector", "003_collect_auth_evidence.py")
        methods = list(auth.RESOURCE_METHODS.values()) + list(auth.PRODUCTION_LOGIN_METHODS.values())
        auth.validate_resource_method(methods)
        for wrong in ([], ["Other#method"]):
            with self.assertRaises(ValueError): auth.validate_resource_method(wrong)
        for method in methods:
            with self.assertRaises(ValueError): auth.validate_resource_method([m for m in methods if m != method])
            with self.assertRaises(ValueError): auth.validate_resource_method(methods + [method])

    def test_web_session_resource_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        expected = {
            "PT-WEB-294": "dev.codex.schubert.nk.web.logging.JdbcWebSessionStoreTest#web294ProviderGetterFailureNeverBecomesInvalidRow",
            "PT-WEB-295": "dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest#web295ProviderGetterFailureRollsBackWithoutDeletingSession",
            "PT-WEB-296": "dev.codex.schubert.nk.web.logging.JdbcWebSessionStoreTest#web296MalformedRowWithResultCloseFailureIsInfrastructureNotInvalidation",
            "PT-WEB-297": "dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest#web297MalformedRowAndResultCloseFailureRollsBackWithoutDeletingSession",
            "PT-WEB-298": "dev.codex.schubert.nk.web.logging.JdbcWebSessionStoreTest#web298MalformedRowWithFatalResultClosePropagatesFatalWithoutInvalidation",
        }
        web.validate_session_resource_inventory(expected)
        for key in expected:
            wrong = dict(expected); del wrong[key]
            with self.assertRaises(ValueError): web.validate_session_resource_inventory(wrong)
            wrong = dict(expected); wrong[key] = "Other#unverified"
            with self.assertRaises(ValueError): web.validate_session_resource_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_session_resource_inventory(dict(expected, unknown="Other#unverified"))

    def test_log_http_and_browser_inventory(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        for cls, names, first, validate in (
                (screen.LOG_SCRIPT_CLASS, ("log092BrowserInputScript",), 92, screen.validate_log_script_suite),
                (screen.LOG_HTTP_CLASS, screen.LOG_HTTP_METHODS, 93, screen.validate_log_http_suite)):
            suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
            for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
            self.assertEqual({f"PT-SCR-{i:03}": cls + "#" + name for i, name in enumerate(names, first)}, validate(suite))
            for field, value in (("tests", "0"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(field, value)
                with self.assertRaises(ValueError): validate(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
                with self.assertRaises(ValueError): validate(wrong)
            wrong = copy.deepcopy(suite); wrong[0].set("name", "unknown")
            with self.assertRaises(ValueError): validate(wrong)
        source_hash = "a" * 64
        trace = {"testId": "PT-SCR-092", "nodeVersion": "v24.19.0", "subcases": 8,
                 "failed": 0, "skipped": 0, "todo": 0, "syntaxExit": 0, "testExit": 0,
                 "lineCoverage": 100, "functionCoverage": 100, "branchCoverage": 100,
                 "productionFiles": 1, "scriptSha256": source_hash,
                 "browserDom": "deterministic-event-double", "actualNkGate": False}
        screen.validate_script_trace(trace, source_hash, "PT-SCR-092")
        for key, value in (("testId", "PT-SCR-025"), ("branchCoverage", 99), ("skipped", 1),
                           ("actualNkGate", True), ("scriptSha256", "b" * 64), ("failed", False)):
            wrong = dict(trace); wrong[key] = value
            with self.assertRaises(ValueError): screen.validate_script_trace(wrong, source_hash, "PT-SCR-092")

    def test_log_template_inventory(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = "dev.codex.schubert.nk.web.view.LogSearchTemplateTest"
        names = ("log084LayoutAndFilters", "log085RowsAndOptional", "log086Pagination", "log087Escaping", "log088InvalidDisplay", "log089CsrfAndClosedSurface", "log090StylesAndResources", "log091ConcurrentRendering")
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-SCR-{i:03}": cls + "#" + name for i, name in enumerate(names, 84)}, screen.validate_log_template_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "7"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): screen.validate_log_template_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): screen.validate_log_template_suite(wrong)
        for field, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(field, value)
            with self.assertRaises(ValueError): screen.validate_log_template_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): screen.validate_log_template_suite(wrong)

    def test_animation_template_inventory(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = "dev.codex.schubert.nk.web.view.AnimationTemplateTest"
        names = ("animation046Menu", "animation047MainRows", "animation048OvaRows", "animation049EmptyAndMaximum",
                 "animation050MegabyteRounding", "animation051EscapingAndCsrf", "animation052CssAndViewBoundary",
                 "animation053ConcurrentRendering")
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-SCR-{i:03}": cls + "#" + name for i, name in enumerate(names, 46)}, screen.validate_animation_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "7"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): screen.validate_animation_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): screen.validate_animation_suite(wrong)
        for field, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(field, value)
            with self.assertRaises(ValueError): screen.validate_animation_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): screen.validate_animation_suite(wrong)

    def test_music_http_inventory(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = "dev.codex.schubert.nk.web.session.MusicControllerTest"
        names = ("music072SuccessAndWire", "music073ErrorMapping", "music074SessionInvalid",
                 "music075MalformedAndTransport", "music076ResponseBinding", "music077NullAndUnknown",
                 "music078MvcRoutesAndInput", "music079RealHttpSecurity", "music080EscapingAndIsolation",
                 "music081EmptyAndMaximum", "music082ConcurrentRequests", "music083CompatibilityTrace")
        suite = ET.Element("testsuite", name=cls, tests="12", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-SCR-{i:03}": cls + "#" + name for i, name in enumerate(names, 72)}, screen.validate_music_http_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "11"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): screen.validate_music_http_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): screen.validate_music_http_suite(wrong)
        for field, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(field, value)
            with self.assertRaises(ValueError): screen.validate_music_http_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): screen.validate_music_http_suite(wrong)

    def test_music_template_inventory(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = "dev.codex.schubert.nk.web.view.MusicHierarchyTemplateTest"
        names = ("music066CategoryMenu", "music067SectionMenu", "music068EmptyAndMaximum",
                 "music069EscapingAndCsrf", "music070CssAndViewBoundary", "music071ConcurrentRendering")
        suite = ET.Element("testsuite", name=cls, tests="6", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-SCR-{i:03}": cls + "#" + name for i, name in enumerate(names, 66)}, screen.validate_music_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "5"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): screen.validate_music_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): screen.validate_music_suite(wrong)
        for field, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(field, value)
            with self.assertRaises(ValueError): screen.validate_music_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): screen.validate_music_suite(wrong)

    def test_log_view_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web286SuccessfulSnapshot", "web287Pagination", "web288QueryEncoding", "web289ResponseBinding", "web290InvalidFields", "web291NullRoleOwnership", "web292ClosedBeanAndEscaping", "web293ConcurrentViews")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.LogSearchViewModelTest#" + name for i, name in enumerate(names, 286)}
        web.validate_log_view_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_log_view_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_log_view_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_log_view_inventory(dict(mapping, unknown="unknown"))

    def test_log_form_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web278DefaultsAndFilters", "web279TextAndBinding", "web280Characters", "web281PageAndEnums", "web282Dates", "web283DateRange", "web284NullOwnershipAndRedaction", "web285ConcurrentBinding")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.form.LogSearchFormTest#" + name for i, name in enumerate(names, 278)}
        web.validate_log_form_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_log_form_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_log_form_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_log_form_inventory(dict(mapping, unknown="unknown"))

    def test_log_results_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web262CompleteRow", "web263OptionalFields", "web264PageBounds", "web265OrderingAndIdentity", "web266NullRoleAndOwnership", "web267ClosedBeansAndRedaction", "web268SyntheticHtmlEscaping", "web269ConcurrentProjection")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest#" + name for i, name in enumerate(names, 262)}
        web.validate_log_results_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_log_results_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_log_results_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_log_results_inventory(dict(mapping, unknown="unknown"))

    def test_log_wire_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web270Requests", "web271SuccessProfiles", "web272ErrorProfiles", "web273MalformedReplies", "web274CapabilitiesAndNull", "web275TransportFailures", "web276ConcurrentRequests", "web277OwnershipAndDiagnostics")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.messaging.LogSearchWireClientTest#" + name for i, name in enumerate(names, 270)}
        web.validate_log_wire_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_log_wire_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_log_wire_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_log_wire_inventory(dict(mapping, unknown="unknown"))

    def test_music_wire_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web254Requests", "web255SuccessProfiles", "web256ErrorProfiles", "web257MalformedReplies",
                 "web258CapabilitiesAndNull", "web259TransportFailures", "web260ConcurrentRequests", "web261OwnershipAndDiagnostics")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.messaging.MusicWireClientTest#" + name
                   for i, name in enumerate(names, 254)}
        web.validate_music_wire_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_music_wire_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_music_wire_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_music_wire_inventory(dict(mapping, unknown="unknown"))

    def test_music_hierarchy_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web246CategorySnapshot", "web247SectionSnapshot", "web248SizeAndCountBounds", "web249DuplicateAndSegment",
                 "web250NullAndOwnership", "web251ClosedBeansAndRedaction", "web252SyntheticHtmlEscaping", "web253ConcurrentProjection")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.MusicHierarchyViewModelTest#" + name
                   for i, name in enumerate(names, 246)}
        web.validate_music_hierarchy_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_music_hierarchy_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_music_hierarchy_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_music_hierarchy_inventory(dict(mapping, unknown="unknown"))

    def test_animation_http_inventory(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = "dev.codex.schubert.nk.web.session.AnimationControllerTest"
        names = ("animation054SuccessAndWire", "animation055ErrorMapping", "animation056SessionInvalid",
                 "animation057MalformedAndTransport", "animation058ResponseBinding", "animation059NullAndUnknown",
                 "animation060MvcRoutes", "animation061RealHttpSecurity", "animation062EscapingAndIsolation",
                 "animation063EmptyAndGrouping", "animation064ConcurrentRequests", "animation065CompatibilityTrace")
        suite = ET.Element("testsuite", name=cls, tests="12", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-SCR-{i:03}": cls + "#" + name for i, name in enumerate(names, 54)}, screen.validate_animation_http_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "11"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): screen.validate_animation_http_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): screen.validate_animation_http_suite(wrong)
        for field, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(field, value)
            with self.assertRaises(ValueError): screen.validate_animation_http_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): screen.validate_animation_http_suite(wrong)

    def test_animation_wire_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web238AnimationRequests", "web239SuccessProfiles", "web240ErrorProfiles",
                 "web241MalformedReplies", "web242CapabilitiesAndNull", "web243TransportFailures",
                 "web244ConcurrentRequests", "web245OwnershipAndDiagnostics")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.messaging.AnimationWireClientTest#" + name
                   for i, name in enumerate(names, 238)}
        web.validate_animation_wire_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_animation_wire_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_animation_wire_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_animation_wire_inventory(dict(mapping, unknown="unknown"))

    def test_animation_view_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web230AnimationMenuCounts", "web231MainGrouping", "web232OvaAndBounds", "web233RejectInconsistentGroups",
                 "web234NullAndOwnership", "web235ClosedBeansAndRedaction", "web236SyntheticHtmlEscaping", "web237ConcurrentProjection")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.AnimationViewModelTest#" + name
                   for i, name in enumerate(names, 230)}
        web.validate_animation_view_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_animation_view_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_animation_view_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_animation_view_inventory(dict(mapping, unknown="unknown"))

    def test_search_http_inventory(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = "dev.codex.schubert.nk.web.session.ScenarioSearchControllerTest"
        names = ("search034SuccessAndWire", "search035InvalidNoMq", "search036ResultErrorsAtEveryStage",
                 "search037SessionInvalidAtEveryStage", "search038MalformedAndTransport", "search039ResponseBinding",
                 "search040NullAndFailurePropagation", "search041MvcGetHeadAndMethod", "search042RealHttpSecurity",
                 "search043EscapingAndIsolation", "search044ConcurrentRequests", "search045CompatibilityTrace")
        suite = ET.Element("testsuite", name=cls, tests="12", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-SCR-{i:03}": cls + "#" + name for i, name in enumerate(names, 34)}, screen.validate_search_http_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "11"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): screen.validate_search_http_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): screen.validate_search_http_suite(wrong)
        for field, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(field, value)
            with self.assertRaises(ValueError): screen.validate_search_http_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): screen.validate_search_http_suite(wrong)

    def test_search_template_inventory(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = "dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest"
        names = ("search026CommonLayoutAndInputs", "search027ResultsAndAudio", "search028PaginationAndEmpty",
                 "search029ValidationErrors", "search030EscapingAndCsp", "search031MaximumRowsAndCandidates",
                 "search032CssResourcesAndViewBoundary", "search033ConcurrentRendering")
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-SCR-{i:03}": cls + "#" + name for i, name in enumerate(names, 26)}, screen.validate_search_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "7"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): screen.validate_search_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): screen.validate_search_suite(wrong)
        for field, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(field, value)
            with self.assertRaises(ValueError): screen.validate_search_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): screen.validate_search_suite(wrong)

    def test_search_script_inventory_and_trace(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = "dev.codex.schubert.nk.web.view.ScenarioSearchScriptTest"
        suite = ET.Element("testsuite", name=cls, tests="1", failures="0", errors="0", skipped="0")
        ET.SubElement(suite, "testcase", classname=cls, name="search025BrowserInputScript")
        self.assertEqual({"PT-SCR-025": cls + "#search025BrowserInputScript"}, screen.validate_script_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "0"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): screen.validate_script_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): screen.validate_script_suite(wrong)
        for field in ("name", "classname"):
            wrong = copy.deepcopy(suite); wrong[0].set(field, "unknown")
            with self.assertRaises(ValueError): screen.validate_script_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): screen.validate_script_suite(wrong)
        trace = {"testId": "PT-SCR-025", "nodeVersion": "v24.19.0", "subcases": 8, "failed": 0,
                 "skipped": 0, "todo": 0, "syntaxExit": 0, "testExit": 0, "lineCoverage": 100,
                 "functionCoverage": 100, "branchCoverage": 100, "productionFiles": 1,
                 "scriptSha256": "a" * 64, "browserDom": "deterministic-event-double", "actualNkGate": False}
        screen.validate_script_trace(trace, "a" * 64)
        for key in trace:
            wrong = dict(trace); del wrong[key]
            with self.assertRaises(ValueError): screen.validate_script_trace(wrong, "a" * 64)
            wrong = dict(trace); wrong[key] = "unknown"
            with self.assertRaises(ValueError): screen.validate_script_trace(wrong, "a" * 64)
        for key in ("failed", "skipped", "todo", "syntaxExit", "testExit"):
            wrong = dict(trace); wrong[key] = False
            with self.assertRaises(ValueError): screen.validate_script_trace(wrong, "a" * 64)
        for key in ("lineCoverage", "functionCoverage", "branchCoverage"):
            wrong = dict(trace); wrong[key] = 99
            with self.assertRaises(ValueError): screen.validate_script_trace(wrong, "a" * 64)
        with self.assertRaises(ValueError): screen.validate_script_trace(dict(trace, unknown=1), "a" * 64)
        with self.assertRaises(ValueError): screen.validate_script_trace(trace, "b" * 64)

    def test_detail_template_inventory(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest"
        names = ("detail017HeaderAndCommonLayout", "detail018PreviousNext", "detail019EntriesAndVoices",
                 "detail020EmptyScenario", "detail021HtmlAndUrlSafety", "detail022MaximumRecordsAndVoices",
                 "detail023CssAndViewBoundary", "detail024ConcurrentRendering")
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-SCR-{i:03}": cls + "#" + name for i, name in enumerate(names, 17)}, screen.validate_suite(suite, True))
        for field, value in (("name", "unknown"), ("tests", "7"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): screen.validate_suite(wrong, True)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): screen.validate_suite(wrong, True)
        for attribute, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(attribute, value)
            with self.assertRaises(ValueError): screen.validate_suite(wrong, True)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): screen.validate_suite(wrong, True)
        with self.assertRaises(ValueError): screen.validate_suite(suite)

    def test_search_view_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web222SuccessfulSnapshot", "web223PaginationUrls", "web224QueryEncoding",
                 "web225ResponseBindingAndBounds", "web226InvalidFieldDisplay", "web227NullAndOwnership",
                 "web228ClosedBeansAndRedaction", "web229ConcurrentSnapshots")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest#" + name
                   for i, name in enumerate(names, 222)}
        web.validate_search_view_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_search_view_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_search_view_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_search_view_inventory(dict(mapping, unknown="unknown"))

    def test_search_form_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web214CanonicalRequest", "web215ByteBoundaries", "web216UnicodeAndEnums",
                 "web217BindingAllowlist", "web218PageBoundaries", "web219InvalidCannotRequest",
                 "web220NullOwnershipRedaction", "web221ConcurrentValidation")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.form.ScenarioSearchFormTest#" + name
                   for i, name in enumerate(names, 214)}
        web.validate_search_form_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_search_form_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_search_form_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_search_form_inventory(dict(mapping, unknown="unknown"))

    def test_search_results_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web206LiteralRowsAndAudio", "web207PageBounds", "web208PageRecordMismatch",
                 "web209AudioAndLineInvariants", "web210NullAndOwnership", "web211ClosedBeansAndRedaction",
                 "web212SyntheticEscaping", "web213ConcurrentProjection")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest#" + name
                   for i, name in enumerate(names, 206)}
        web.validate_search_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_search_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_search_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_search_inventory(dict(mapping, unknown="unknown"))

    def test_detail_web_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web194HeaderAndNavigation", "web195GroupingAndAudio", "web196EmptyAndBounds",
                 "web197NullContracts", "web198NavigationPairs", "web199SequenceRejection",
                 "web200EntryMetadataConsistency", "web201ImmutableSnapshot", "web202ClosedBeanContract",
                 "web203SyntheticHtmlEscaping", "web204ConcurrentProjection", "web205RedactedDiagnostics")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#" + name
                   for i, name in enumerate(names, 194)}
        web.validate_detail_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_detail_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_detail_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_detail_inventory(dict(mapping, unknown="unknown"))

    def test_screen_inventory_and_negative_status(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = "dev.codex.schubert.nk.web.session.ScenarioControllerTest"
        names = ("screens001GamesSuccess", "screens002RoutesSuccess", "screens003FilesSuccess",
                 "screens004EmptyHierarchy", "screens005AllResultCodes", "screens006InvalidSessionTerminal",
                 "screens007WireAndBindingFailure", "screens008NullAndForeignPrincipal",
                 "screens009ClosedRoutesAndRequests", "screens010RealTemplatesAndNavigation",
                 "screens011HtmlEscaping", "screens012CompatibilityObservations", "screens013ConcurrentQueries",
                 "screens014FailurePropagation", "screens015MvcConfiguration", "screens016RealHttpSecurityAndTerminal")
        suite = ET.Element("testsuite", name=cls, tests="16", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-SCR-{i:03}": cls + "#" + name for i, name in enumerate(names, 1)}, screen.validate_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "15"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): screen.validate_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): screen.validate_suite(wrong)
        for attribute, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(attribute, value)
            with self.assertRaises(ValueError): screen.validate_suite(wrong)
        wrong = copy.deepcopy(suite); wrong.remove(wrong[0])
        with self.assertRaises(ValueError): screen.validate_suite(wrong)

    def test_login_inventory_and_negative_status(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = "dev.codex.schubert.nk.web.controller.LoginControllerTest"
        names = ("scr105ApprovedBrandAndPostCsrf", "scr106InputsAndNoLeakedCredentials",
                 "scr107OnlyMatchingCurrentMessagesAppear", "scr108ClosedViewAndControllerBoundary")
        suite = ET.Element("testsuite", name=cls, tests="4", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        expected = {f"PT-SCR-{index:03}": cls + "#" + name for index, name in enumerate(names, 105)}
        self.assertEqual(expected, screen.validate_login_suite(suite))
        for position in range(4):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): screen.validate_login_suite(wrong)
        for kind in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError): screen.validate_login_suite(wrong)

    def test_web_http_inventory_and_negative_status(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = screen.WEB_HTTP_CLASS
        names = screen.WEB_HTTP_METHODS
        suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        expected = {f"PT-SCR-{index:03}": cls + "#" + name for index, name in zip(screen.WEB_HTTP_IDS, names)}
        self.assertEqual(expected, screen.validate_web_http_suite(suite))
        for position in range(len(names)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): screen.validate_web_http_suite(wrong)
        for kind in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError): screen.validate_web_http_suite(wrong)
        for replacement in (names[1], "scr999Unknown"):
            wrong = copy.deepcopy(suite); wrong[0].set("name", replacement)
            with self.assertRaises(ValueError): screen.validate_web_http_suite(wrong)
        with self.assertRaises(ValueError):
            screen.validate_named_suite(suite, cls, names, 109, (109,) * len(names))

    def test_web_application_inventory_and_negative_status(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = screen.WEB_APPLICATION_CLASS
        names = screen.WEB_APPLICATION_METHODS
        self.assertEqual(("scr117ActualIntegratedLoginAndDirectDenial",
                          "scr118DependencyFailurePreventsHttpBind",
                          "scr119NullAndInvalidInputStopsBeforeDependencyProbe",
                          "scr122InvalidMvcDependencyStopsBeforeDatabaseBorrow",
                          "scr124SessionFactoryWiresLogMvcUsingSecurityRepository",
                          "scr125NullSessionFactoryStopsBeforeBorrowingResources",
                          "scr126InvalidSessionDependenciesStopBeforeHttpBind"), names)
        self.assertEqual((117, 118, 119, 122, 124, 125, 126), screen.WEB_APPLICATION_IDS)
        suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        expected = {f"PT-SCR-{index:03}": cls + "#" + name for index, name in zip(screen.WEB_APPLICATION_IDS, names)}
        self.assertEqual(expected, screen.validate_web_application_suite(suite))
        for position in range(len(names)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): screen.validate_web_application_suite(wrong)
        for kind in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError): screen.validate_web_application_suite(wrong)
        wrong = copy.deepcopy(suite); wrong[0].set("name", "scr999Unknown")
        with self.assertRaises(ValueError): screen.validate_web_application_suite(wrong)

    def test_web_dependency_inventory_and_negative_status(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        cls = screen.WEB_DEPENDENCY_CLASS
        names = screen.WEB_DEPENDENCY_METHODS
        suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        expected = {f"PT-SCR-{index:03}": cls + "#" + name for index, name in zip(screen.WEB_DEPENDENCY_IDS, names)}
        self.assertEqual(expected, screen.validate_web_dependency_suite(suite))
        for position in range(len(names)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): screen.validate_web_dependency_suite(wrong)
        for kind in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError): screen.validate_web_dependency_suite(wrong)

    def test_screen_trace_and_coverage(self):
        screen = module("screen_collector", "029_collect_scenario_screen_evidence.py")
        expected = {"PT-SCR-012.txt": b"cases=CHR-S05|CHR-S06\nfixture=public-synthetic\ngames=2\nroutes=2\nfiles=2\norderAndText=PASS\nactualNkGate=false\n",
                    "PT-SCR-024.txt": b"template=scenario\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumEntries=10000\nmaximumVoices=999\nactualNkGate=false\n",
                    "PT-SCR-033.txt": b"template=search\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRows=100\nmaximumSpeakers=500\nactualNkGate=false\n",
                    "PT-SCR-045.txt": b"screen=SCR003\nfixture=public-synthetic\nrequestOrder=SRC|GAM|SPK\nresults=2\nrepresentativeAudio=1\nempty=PASS\nactualNkGate=false\n",
                    "PT-SCR-053.txt": b"templates=animation|animation-list\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRecords=50\nactualNkGate=false\n",
                    "PT-SCR-065.txt": b"screens=SCR008|SCR009\nfixture=public-synthetic\nroutes=3\nmenuCards=3\nlistRecords=2\nactualNkGate=false\n",
                    "PT-SCR-071.txt": b"templates=music|music-sections\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumCategories=20\nmaximumSections=100\nactualNkGate=false\n",
                    "PT-SCR-083.txt": b"screens=SCR011|SCR012\nfixture=public-synthetic\nroutes=2\ncategories=2\nsections=2\nactualNkGate=false\n"}
        screen.validate_traces(expected)
        for wrong in ({}, dict(expected, unknown=b""), {"PT-SCR-012.txt": b"PASS"}):
            with self.assertRaises(ValueError): screen.validate_traces(wrong)
        for key in expected:
            wrong = dict(expected); del wrong[key]
            with self.assertRaises(ValueError): screen.validate_traces(wrong)
            wrong = dict(expected); wrong[key] = b"PASS"
            with self.assertRaises(ValueError): screen.validate_traces(wrong)
        report = ET.Element("report")
        for name in ("controller/ScenarioController", "config/ScenarioMvcConfiguration", "config/WebMvcConfiguration",
                     "controller/AnimationController", "config/AnimationMvcConfiguration",
                     "controller/MusicController", "config/MusicMvcConfiguration",
                     "controller/LogController", "config/LogMvcConfiguration",
                     "controller/LoginController", "bootstrap/WebHttpServer",
                     "bootstrap/WebDependencyReadiness", "bootstrap/WebStartupException",
                     "bootstrap/WebApplication", "bootstrap/WebLogApplicationRuntime"):
            cls = ET.SubElement(report, "class", name="dev/codex/schubert/nk/web/" + name)
            for kind in ("LINE", "METHOD", "CLASS"):
                ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        ET.SubElement(report[0], "counter", type="BRANCH", missed="0", covered="1")
        ET.SubElement(report[3], "counter", type="BRANCH", missed="0", covered="1")
        ET.SubElement(report[5], "counter", type="BRANCH", missed="0", covered="1")
        ET.SubElement(report[7], "counter", type="BRANCH", missed="0", covered="1")
        ET.SubElement(report[10], "counter", type="BRANCH", missed="0", covered="1")
        ET.SubElement(report[11], "counter", type="BRANCH", missed="0", covered="1")
        ET.SubElement(report[14], "counter", type="BRANCH", missed="0", covered="1")
        self.assertEqual(15, len(screen.validate_coverage(report)))
        for cls_index in range(15):
            wrong = copy.deepcopy(report); wrong.remove(wrong[cls_index])
            with self.assertRaises(ValueError): screen.validate_coverage(wrong)
            for counter_index in range(len(report[cls_index])):
                for attribute, value in (("missed", "1"), ("covered", "0")):
                    wrong = copy.deepcopy(report); wrong[cls_index][counter_index].set(attribute, value)
                    with self.assertRaises(ValueError): screen.validate_coverage(wrong)
                wrong = copy.deepcopy(report); wrong[cls_index].remove(wrong[cls_index][counter_index])
                with self.assertRaises(ValueError): screen.validate_coverage(wrong)

    def test_postgres_source_test_ids(self):
        ids = ["PT-OPS-PGCFG-001", "PT-OPS-PGCFG-002", "PT-OPS-PGCFG-003", "PT-OPS-PGCFG-004",
               "PT-OPS-PGCFG-005", "PT-OPS-PGCFG-006", "PT-OPS-PGCFG-007", "PT-OPS-PGCFG-008"]
        source = "\n".join('@DisplayName("' + value + ' fixture")' for value in ids)
        launch.validate_postgres_ids(source)
        for wrong in ("", source.replace("PGCFG-", "PGCFG"), source + source,
                      source.replace("PGCFG-008", "PGCFG-009")):
            with self.assertRaises(ValueError): launch.validate_postgres_ids(wrong)

    def test_receipt_inventory_and_negative_status(self):
        receipt = module("receipt_collector", "027_collect_question_receipt_evidence.py")
        cls = "dev.codex.schubert.nk.api.application.question.QuestionReceiptIdTest"
        names = ("exactAlphabet", "lengthBoundaries", "characterBoundaries", "independentRandomVector",
                 "randomFailure", "nullAndFactory", "concurrentCalls", "equalityAndPublicEvidence")
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        expected = {f"PT-QST-RID{i:03}": cls + "#" + name for i, name in enumerate(names, 1)}
        self.assertEqual(expected, receipt.validate_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "7"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): receipt.validate_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): receipt.validate_suite(wrong)
        for attribute, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(attribute, value)
            with self.assertRaises(ValueError): receipt.validate_suite(wrong)

    def test_stub_inventory_and_negative_status(self):
        stub = module("stub_collector", "028_collect_stub_evidence.py")
        cls = "dev.codex.schubert.nk.api.application.question.StubAnswerProviderTest"
        names = ("emptyAnswerAndClock", "nullContracts", "clockFailures", "resultValueAndRedaction",
                 "concurrentCallsAndEvidence", "fixedBusinessFailureValue")
        suite = ET.Element("testsuite", name=cls, tests="6", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-ASY-STB{i:03}": cls + "#" + name for i, name in enumerate(names, 1)}, stub.validate_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "5"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): stub.validate_suite(wrong)
        missing_latest = copy.deepcopy(suite)
        missing_latest.remove(missing_latest[-1])
        missing_latest.set("tests", "5")
        with self.assertRaises(ValueError):
            stub.validate_suite(missing_latest)
        for tag in ("failure", "error", "skipped", "flakyFailure", "flakyError", "rerunFailure", "rerunError"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[-1], tag)
            with self.assertRaises(ValueError): stub.validate_suite(wrong)
        for attribute, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(attribute, value)
            with self.assertRaises(ValueError): stub.validate_suite(wrong)

    def test_scenario_web_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web166SixRequestsMatchIndependentWire", "web167SixSuccessResponsesDecodeWithoutRetainingSecrets",
                 "web168ApprovedErrorsNeverExposeSuccessPayload", "web169MalformedUncorrelatedAndForeignResponsesReject",
                 "web170InputAndConfigurationFaultsNeverSend", "web171TransportFailuresDoNotRetryOrLeakPending",
                 "web172ConcurrentQueriesKeepContextsAndRepliesSeparate", "web173ResponseBoundsAndCallerOwnershipRemainExact")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest#" + name
                   for i, name in enumerate(names, 166)}
        web.validate_scenario_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_scenario_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_scenario_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_scenario_inventory(dict(mapping, unknown="unknown"))

    def test_page_web_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web174EmptyAndSinglePage", "web175FirstMiddleAndLastPages",
                 "web176MaximumWireBounds", "web177InvalidProjectionCombinations",
                 "web178NullConfigurationAndRedaction", "web179IndependentParallelProjection",
                 "web180JavaBeanDisplayContract", "web181ThymeleafSyntheticDom")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.PageViewModelTest#" + name
                   for i, name in enumerate(names, 174)}
        web.validate_page_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_page_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_page_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_page_inventory(dict(mapping, unknown="unknown"))

    def test_hierarchy_web_inventory(self):
        web = module("web_collector", "015_collect_web_evidence.py")
        names = ("web182GameDisplay", "web183RouteDisplay", "web184FileDisplay", "web185NullBoundaries", "web186PrefixBoundaries", "web187SnapshotOwnership", "web188ClosedBeanContract", "web189SyntheticEscaping", "web190ConcurrentProjection", "web191ListSizeBoundaries", "web192PreserveSourceOrder", "web193RedactedDiagnostics")
        mapping = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.ScenarioHierarchyViewModelTest#" + name
                   for i, name in enumerate(names, 182)}
        web.validate_hierarchy_inventory(mapping)
        for key in mapping:
            wrong = dict(mapping); del wrong[key]
            with self.assertRaises(ValueError): web.validate_hierarchy_inventory(wrong)
            wrong = dict(mapping); wrong[key] = "Other#unknown"
            with self.assertRaises(ValueError): web.validate_hierarchy_inventory(wrong)
        with self.assertRaises(ValueError): web.validate_hierarchy_inventory(dict(mapping, unknown="unknown"))

    def test_stub_trace_and_coverage(self):
        stub = module("stub_collector", "028_collect_stub_evidence.py")
        expected = {"PT-ASY-STB005.txt": b"provider=STUB\nanswerLength=0\nclockReadsPerCall=1\nconcurrentCalls=64\nuniqueClockValues=64\nexternalCalls=0\nrawBodySaved=false\n"}
        self.assertEqual(expected, stub.TRACES)
        stub.validate_traces(expected)
        for wrong in ({}, dict(expected, unknown=b""), {"PT-ASY-STB005.txt": b"PASS"}):
            with self.assertRaises(ValueError): stub.validate_traces(wrong)
        report = ET.Element("report")
        for name in ("AnswerResult", "StubAnswerProvider", "AnswerBusinessException"):
            cls = ET.SubElement(report, "class", name="dev/codex/schubert/nk/api/application/question/" + name)
            for kind in ("LINE", "METHOD", "CLASS"):
                ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        result = stub.validate_coverage(report)
        self.assertEqual(3, len(result))
        self.assertTrue(all(counters["BRANCH"] == {"missed": 0, "covered": 0} for counters in result.values()))
        for cls_index in range(3):
            wrong = copy.deepcopy(report); ET.SubElement(wrong[cls_index], "counter", type="BRANCH", missed="1", covered="0")
            with self.assertRaises(ValueError): stub.validate_coverage(wrong)
            for counter_index in range(3):
                wrong = copy.deepcopy(report); wrong[cls_index][counter_index].set("missed", "1")
                with self.assertRaises(ValueError): stub.validate_coverage(wrong)
                wrong = copy.deepcopy(report); wrong[cls_index].remove(wrong[cls_index][counter_index])
                with self.assertRaises(ValueError): stub.validate_coverage(wrong)
            wrong = copy.deepcopy(report); wrong.remove(wrong[cls_index])
            with self.assertRaises(ValueError): stub.validate_coverage(wrong)

    def test_submit_inventory_and_negative_status(self):
        receipt = module("receipt_collector", "027_collect_question_receipt_evidence.py")
        cls = "dev.codex.schubert.nk.api.application.question.QuestionSubmitRequestTest"
        names = ("literalWireAndCanonical", "byteAndUnicodeBoundaries", "protocolRejection",
                 "fingerprintBinding", "ownershipAndClose", "nullContracts", "concurrentScopes",
                 "publicEvidenceAndRedaction")
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-QST-SUB{i:03}": cls + "#" + name for i, name in enumerate(names, 1)},
                         receipt.validate_suite(suite))
        for field, value in (("name", "unknown"), ("tests", "7"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(field, value)
            with self.assertRaises(ValueError): receipt.validate_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): receipt.validate_suite(wrong)
        for attribute, value in (("name", names[1]), ("name", "unknown"), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(attribute, value)
            with self.assertRaises(ValueError): receipt.validate_suite(wrong)

    def test_receipt_trace_and_coverage(self):
        receipt = module("receipt_collector", "027_collect_question_receipt_evidence.py")
        expected = {"PT-QST-RID008.txt": b"forward=0123456789ABCDEFGHJKMNPQRS\nreverse=ZYXWVTSRQPNMKJHGFEDCBA9876\nlength=26\nalphabetSize=32\nrandomDrawsPerId=26\nownerOrTimeInput=false\n"}
        expected["PT-QST-SUB008.txt"] = b"layout=QSBREQ01\ninteraction=A\ndataLength=4144\ncanonicalFieldCount=1\ncanonicalField=question/X1\ntarget=QUESTION:NEW\nmetadataExcluded=true\nrawBodySaved=false\n"
        self.assertEqual(expected, receipt.TRACES)
        receipt.validate_traces(expected)
        for wrong in ({}, dict(expected, unknown=b""), {"PT-QST-RID008.txt": b"PASS"}):
            with self.assertRaises(ValueError): receipt.validate_traces(wrong)
        report = ET.Element("report")
        for name in ("QuestionReceiptId", "QuestionReceiptIdGenerator", "QuestionSubmitRequest"):
            cls = ET.SubElement(report, "class", name="dev/codex/schubert/nk/api/application/question/" + name)
            for kind in ("LINE", "METHOD", "CLASS", "BRANCH"):
                ET.SubElement(cls, "counter", type=kind, missed="0", covered="1")
        self.assertEqual(3, len(receipt.validate_coverage(report)))
        for cls_index in (0, 1, 2):
            for counter_index in range(4):
                wrong = copy.deepcopy(report); wrong[cls_index][counter_index].set("missed", "1")
                with self.assertRaises(ValueError): receipt.validate_coverage(wrong)
            wrong = copy.deepcopy(report); wrong.remove(wrong[cls_index])
            with self.assertRaises(ValueError): receipt.validate_coverage(wrong)

    def test_postgres_configuration_trace(self):
        expected = {"PT-OPS-PGCFG-008.txt": b"isolated=true\nhostConfigurationChanged=false\nhbaReload=false\nrawDatabaseLogCopied=false\nconfigurationKeys=32\nhbaRules=16\n"}
        self.assertEqual(expected, launch.POSTGRES_TRACES)
        launch.validate_postgres_traces(expected)
        for wrong in ({}, dict(expected, unknown=b""), {"PT-OPS-PGCFG-008.txt": b"PASS"}):
            with self.assertRaises(ValueError): launch.validate_postgres_traces(wrong)

    def test_batch_reactor_gate(self):
        verified = {"runId": "PT-WEB-fixture", "exitCode": 0, "modules": {"batch": {"tests": 550}}}
        batch.validate_reactor(verified, "PT-WEB-fixture")
        for count in (0, 327, 343, 359, 366, 367, 369, 404, 419, 421, 500, 508, 516, 531):
            wrong = copy.deepcopy(verified); wrong["modules"]["batch"]["tests"] = count
            with self.assertRaises(ValueError): batch.validate_reactor(wrong, "PT-WEB-fixture")
        wrong = copy.deepcopy(verified); wrong["exitCode"] = 1
        with self.assertRaises(ValueError): batch.validate_reactor(wrong, "PT-WEB-fixture")
        with self.assertRaises(ValueError): batch.validate_reactor(verified, "PT-WEB-other")

    def test_batch_preflight_report_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            reports = target / "surefire-reports"
            reports.mkdir()
            report = reports / "TEST-batch.xml"
            suite = ET.Element("testsuite", name="LocalBatchFixture", tests="550",
                               failures="0", errors="0", skipped="0")
            for index in range(550):
                ET.SubElement(suite, "testcase", name=f"local{index}", classname="LocalBatchFixture")
            ET.ElementTree(suite).write(report, encoding="utf-8")
            self.assertEqual([550], [len(s.findall("testcase")) for s in batch.read_batch_reports(target)])
            for attribute in ("failures", "errors", "skipped", "tests"):
                with self.subTest(attribute=attribute):
                    bad = copy.deepcopy(suite)
                    bad.set(attribute, "1")
                    ET.ElementTree(bad).write(report, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "nonpassing or inconsistent"):
                        batch.read_batch_reports(target)
            later = copy.deepcopy(suite)
            later.set("tests", "1466")
            for index in range(550, 1466):
                ET.SubElement(later, "testcase", name=f"local{index}", classname="LocalBatchFixture")
            ET.ElementTree(later).write(report, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "total does not match"):
                batch.read_batch_reports(target)
            rerun = copy.deepcopy(suite)
            ET.SubElement(rerun[0], "rerunFailure")
            ET.ElementTree(rerun).write(report, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nonpassing or inconsistent"):
                batch.read_batch_reports(target)
            report.unlink()
            with self.assertRaisesRegex(ValueError, "total does not match"):
                batch.read_batch_reports(target)

    def test_batch_runtime_dependency_inventory_and_nonpassing_cases(self):
        cls = "dev.codex.schubert.nk.batch.bootstrap.BatchRuntimeDependencyTest"
        name = "bat283RuntimePostgresDriverAndScopeCanaries"
        self.assertEqual(cls, batch.BATCH_RUNTIME_DEPENDENCY_CLASS)
        self.assertEqual((name,), batch.BATCH_RUNTIME_DEPENDENCY_METHODS)
        suite = ET.Element("testsuite", name=cls, tests="1", failures="0", errors="0", skipped="0")
        ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({"PT-BAT-283": cls + "#" + name}, batch.validate_batch_runtime_dependency_suite(suite))
        for key, value in (("tests", "0"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): batch.validate_batch_runtime_dependency_suite(wrong)
        for replacement in ("unlisted", name + "(Path)"):
            wrong = copy.deepcopy(suite); wrong[0].set("name", replacement)
            with self.assertRaises(ValueError): batch.validate_batch_runtime_dependency_suite(wrong)

    @staticmethod
    def completion_fixture():
        cls = "dev.codex.schubert.nk.batch.file.BackupBundleCompletionTest"
        names = ("verifiedCommitAndReplay", "invalidFilesAndHandleBinding", "allReadAndDatabaseFailures",
                 "sharedDeadlineAndInterrupt", "completionClockAndCommitUncertainty", "nullOwnershipAndFactory",
                 "unknownFailuresAndResourceOwnership", "concurrentAndIndependentTrace")
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite,"testcase",classname=cls,name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i,name in enumerate(names,274)}

    def test_completion_inventory(self):
        suite, expected = self.completion_fixture()
        self.assertEqual(expected, batch.validate_completion_suite(suite))
        for position in range(8):
            wrong=copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_completion_suite(wrong)
            for tag in ("failure","error","skipped","flakyFailure","rerunFailure","unknown"):
                wrong=copy.deepcopy(suite); ET.SubElement(wrong[position],tag)
                with self.assertRaises(ValueError): batch.validate_completion_suite(wrong)
            for key,value in (("name","unknown"),("name",suite[(position+1)%8].get("name")),("classname","unknown")):
                wrong=copy.deepcopy(suite); wrong[position].set(key,value)
                with self.assertRaises(ValueError): batch.validate_completion_suite(wrong)
        for key,value in (("tests","1"),("name","unknown"),("failures","1"),("errors","1"),("skipped","1")):
            wrong=copy.deepcopy(suite); wrong.set(key,value)
            with self.assertRaises(ValueError): batch.validate_completion_suite(wrong)

    def test_completion_literal_trace(self):
        expected={"PT-BAT-281-completion.txt":b"manifestSha256=bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370\nfiles=4\nDB=1/1/0/26\nCONFIG=2/2/0/67\nend=2026-09-12T15:00:04.987654Z\nowner=SUCCESS\nnonowner=REJECTED\n"}
        batch.validate_completion_traces(expected)
        for wrong in ({},{**expected,"unknown":b""}):
            with self.assertRaises(ValueError): batch.validate_completion_traces(wrong)
        name,value=next(iter(expected.items()))
        for position in range(len(value)):
            with self.assertRaises(ValueError):
                batch.validate_completion_traces({name:value[:position]+bytes([value[position]^1])+value[position+1:]})

    @staticmethod
    def publication_fixture():
        cls = "dev.codex.schubert.nk.batch.file.BackupManifestPublisherTest"
        names = ("independentGoldenPublication", "privateCreationOwnership", "rootAndChildAdmission",
                 "metadataNullTypes", "filePermissionsAndLinks", "writeProgressBoundaries",
                 "readbackAndIdentity", "namespaceReplacement", "collisionAndPartRetention",
                 "everyIoFailure", "deadlineAndInterrupt", "compoundAndBufferWipe",
                 "nullAndClosedContracts", "concurrentNoReplace", "nativeIoAndFactory", "independentPublicationTrace")
        suite = ET.Element("testsuite", name=cls, tests="16", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names,242)}

    @staticmethod
    def bundle_fixture():
        cls = "dev.codex.schubert.nk.batch.file.BackupBundlePublisherTest"
        names = ("verifiedDurablePublication", "forceOrderAndRetainedInodes", "pendingContentAndMetadata",
                 "finalManifestAndArtifactChecks", "forceSizeAndNullBoundaries", "everyIoFailure",
                 "unknownAndCompoundFailures", "deadlineAcrossPhases", "interruptionAcrossPhases",
                 "existingFinalAndMissingPending", "namespaceReplacement", "nullAndOwnerContracts",
                 "concurrentPublication", "nativePortsAndFactory", "readonlyCompatibility", "independentBundleTrace")
        suite = ET.Element("testsuite", name=cls, tests="16", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite,"testcase",classname=cls,name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i,name in enumerate(names,258)}

    def test_bundle_inventory(self):
        suite, expected = self.bundle_fixture()
        self.assertEqual(expected,batch.validate_bundle_suite(suite))
        for position in range(16):
            wrong=copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_bundle_suite(wrong)
            for tag in ("failure","error","skipped","flakyFailure","rerunFailure","unknown"):
                wrong=copy.deepcopy(suite); ET.SubElement(wrong[position],tag)
                with self.assertRaises(ValueError): batch.validate_bundle_suite(wrong)
            for key,value in (("name","unknown"),("name",suite[(position+1)%16].get("name")),("classname","unknown")):
                wrong=copy.deepcopy(suite); wrong[position].set(key,value)
                with self.assertRaises(ValueError): batch.validate_bundle_suite(wrong)
        for key,value in (("tests","1"),("name","unknown"),("failures","1"),("errors","1"),("skipped","1")):
            wrong=copy.deepcopy(suite); wrong.set(key,value)
            with self.assertRaises(ValueError): batch.validate_bundle_suite(wrong)

    def test_bundle_literal_trace(self):
        expected={"PT-BAT-273-bundle.txt":b"964|bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370\nforce=4|publish=1|sync=2\nio=301|clock=514\n"}
        batch.validate_bundle_traces(expected)
        for wrong in ({},{**expected,"unknown":b""}):
            with self.assertRaises(ValueError): batch.validate_bundle_traces(wrong)
        name,value=next(iter(expected.items()))
        for position in range(len(value)):
            with self.assertRaises(ValueError):
                batch.validate_bundle_traces({name:value[:position]+bytes([value[position]^1])+value[position+1:]})

    def test_root_publication_inventory(self):
        suite, expected = self.publication_fixture()
        self.assertEqual(expected, batch.validate_publication_suite(suite))
        for position in range(16):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_publication_suite(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[position], tag)
                with self.assertRaises(ValueError): batch.validate_publication_suite(wrong)
            for key, value in (("name", "unknown"), ("name", suite[(position+1)%16].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[position].set(key,value)
                with self.assertRaises(ValueError): batch.validate_publication_suite(wrong)
        for key, value in (("tests", "1"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key,value)
            with self.assertRaises(ValueError): batch.validate_publication_suite(wrong)

    def test_root_publication_literal_trace(self):
        expected = {"PT-BAT-257-publication.txt": b"964|bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370\ncreate=1|publish=1|sync=1\nio=79|clock=109\n"}
        batch.validate_publication_traces(expected)
        for wrong in ({}, {**expected, "unknown": b""}):
            with self.assertRaises(ValueError): batch.validate_publication_traces(wrong)
        name, value = next(iter(expected.items()))
        for position in range(len(value)):
            with self.assertRaises(ValueError):
                batch.validate_publication_traces({name: value[:position] + bytes([value[position]^1]) + value[position+1:]})

    @staticmethod
    def reader_fixture():
        cls = "dev.codex.schubert.nk.batch.file.BackupManifestReaderTest"
        names = ("canonicalRootManifest", "nameAndFullHandleBinding", "directoryAndOwnerContracts",
                 "manifestMetadataAndAcl", "rootAndChildRebinding", "manifestReplacementAndMutation",
                 "sizeAndReadBoundaries", "canonicalByteRejection", "everyIoFailure", "closeFailurePrecedence",
                 "timeAndInterrupt", "nullAndUnknownProviders", "borrowedRootAndClosed",
                 "concurrentSerializedReaders", "readOnlyNativeAdapters", "independentTraceAndDownstream")
        suite = ET.Element("testsuite", name=cls, tests="16", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 226)}

    def test_root_reader_inventory(self):
        suite, expected = self.reader_fixture()
        self.assertEqual(expected, batch.validate_reader_suite(suite))
        for position in range(16):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_reader_suite(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[position], tag)
                with self.assertRaises(ValueError): batch.validate_reader_suite(wrong)
            for key, value in (("name", "unknown"), ("name", suite[(position + 1) % 16].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[position].set(key, value)
                with self.assertRaises(ValueError): batch.validate_reader_suite(wrong)
        for key, value in (("tests", "1"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): batch.validate_reader_suite(wrong)

    def test_root_reader_literal_trace(self):
        expected = {"PT-BAT-241-reader.txt": b"20260913-000002-12345678-9abc-def0-8123-456789abcdef\n90000|90001\n26|67\n964|bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370\n"}
        batch.validate_reader_traces(expected)
        for wrong in ({}, {**expected, "unknown": b""}):
            with self.assertRaises(ValueError): batch.validate_reader_traces(wrong)
        name, value = next(iter(expected.items()))
        for position in range(len(value)):
            wrong = {name: value[:position] + bytes([value[position] ^ 1]) + value[position + 1:]}
            with self.assertRaises(ValueError): batch.validate_reader_traces(wrong)

    def test_resource_scope_inventory(self):
        cls = "dev.codex.schubert.nk.storage.ResourceScopeTest"
        self.assertEqual((cls, 1, ("successfulOwnership", "knownIoFailures", "unknownBodyFailures",
                         "knownBodyUnknownCleanup", "unknownCompoundFailures", "nullAndNullableContracts",
                         "nestedScopes", "concurrentScopes")),
                         next(group for group in launch.DEPLOYMENT_GROUPS if group[0] == cls))
        self.assertFalse(scenario.scenario_storage_suite(cls))
        self.assertEqual("dev/codex/schubert/nk/storage/ResourceScope", launch.SCOPE_SUBJECT)

    @staticmethod
    def pair_fixture(service=False):
        cls, names, start = (
            ("dev.codex.schubert.nk.batch.backup.BackupCommitServiceTest",
             ("commitAndExistingReceipt", "rollbackBothSteps", "uncertainCommitReplay", "connectionContract", "everyBoundaryFailure", "interruptionAfterCommit", "unknownPrimaryAndCleanup", "independentConnections"), 218) if service else
            ("dev.codex.schubert.nk.batch.repository.BackupStepRepositoryTest",
             ("runningAndCommittedPair", "fullHandleAndMissingRows", "statusCounterAndTimeMatrix", "atomicPairAndReplay", "databaseGuardsAndLocks", "everyJdbcFault", "nullAndUnknownFailures", "concurrentBindings"), 210))
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_backup_pair_inventory(self):
        for service, validate in ((False, batch.validate_pair_suite), (True, batch.validate_commit_suite)):
            suite, expected = self.pair_fixture(service)
            self.assertEqual(expected, validate(suite))
            for position in range(8):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
                for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                    wrong = copy.deepcopy(suite); ET.SubElement(wrong[position], tag)
                    with self.assertRaises(ValueError): validate(wrong)
                for key, value in (("name", "unknown"), ("name", suite[(position + 1) % 8].get("name")), ("classname", "unknown")):
                    wrong = copy.deepcopy(suite); wrong[position].set(key, value)
                    with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "1"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)

    def test_backup_pair_literal_traces(self):
        rows = b"BACKUP_CONFIG|SUCCESS|2|2|0|67|2026-09-13 02:00:03.000000+00|true|true\nBACKUP_DB|SUCCESS|1|1|0|26|2026-09-13 02:00:03.000000+00|true|true\n"
        expected = {
            "PT-BAT-213-pair.txt": rows,
            "PT-BAT-215-jdbc.txt": b"read=70\nnew=240\nreplay=70\ninjected=380\n",
            "PT-BAT-218-commit.txt": b"fresh_jdbc=246\nreplay_jdbc=76\n" + rows,
            "PT-BAT-220-uncertain-false.txt": b"committed_before_failure=false\nretry_updates=2\n" + rows,
            "PT-BAT-220-uncertain-true.txt": b"committed_before_failure=true\nretry_updates=0\n" + rows,
        }
        batch.validate_pair_traces(expected)
        for wrong in ({}, {**expected, "unknown": b""}):
            with self.assertRaises(ValueError): batch.validate_pair_traces(wrong)
        for name, value in expected.items():
            wrong = dict(expected); del wrong[name]
            with self.assertRaises(ValueError): batch.validate_pair_traces(wrong)
            for position in range(len(value)):
                wrong = dict(expected); wrong[name] = value[:position] + bytes([value[position] ^ 1]) + value[position+1:]
                with self.assertRaises(ValueError): batch.validate_pair_traces(wrong)

    @staticmethod
    def artifact_fixture():
        cls = "dev.codex.schubert.nk.batch.file.BackupArtifactVerifierTest"
        names = ("trustedBundleAndManifestDigest", "completeFileSetAndCanonicalName", "directoryAndOwnerContracts", "perFileMetadataAndAcl", "rootAndChildRebinding", "eachFileReplacementAndMutation", "sizesShortLongAndZeroRead", "independentHashAndGoldenMismatch", "streamingBoundaryAndLargeFile", "everyIoFailure", "resourceClosureAndSuppression", "timeAndInterrupt", "providerNullRuntimeAndRedaction", "borrowedRootOwnershipAndClosed", "concurrentSerializedAccess", "readOnlyNoMutationInventory",)
        suite = ET.Element("testsuite", name=cls, tests="16", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 194)}

    def test_backup_artifact_inventory(self):
        suite, expected = self.artifact_fixture()
        self.assertEqual(expected, batch.validate_artifact_suite(suite))
        for position in range(16):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_artifact_suite(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[position], tag)
                with self.assertRaises(ValueError): batch.validate_artifact_suite(wrong)
            for key, value in (("name", "unknown"), ("name", suite[(position + 1) % 16].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[position].set(key, value)
                with self.assertRaises(ValueError): batch.validate_artifact_suite(wrong)
        for key, value in (("tests", "1"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): batch.validate_artifact_suite(wrong)

    def test_backup_artifact_independent_digest_trace(self):
        name = "PT-BAT-194-digest.txt"
        expected = b"964|bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370\n"
        batch.validate_artifact_traces({name: expected})
        for wrong in ({}, {name: expected, "unknown": b""}, {name: expected + b"\n"}):
            with self.assertRaises(ValueError): batch.validate_artifact_traces(wrong)
        for position in range(len(expected)):
            wrong = expected[:position] + bytes([expected[position] ^ 1]) + expected[position+1:]
            with self.assertRaises(ValueError): batch.validate_artifact_traces({name: wrong})
        self.assertEqual(964, len(batch.ARTIFACT_GOLDEN))
        self.assertEqual("bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370",
                         hashlib.sha256(batch.ARTIFACT_GOLDEN).hexdigest())

    @staticmethod
    def backup_fixture(codec=False):
        cls, names, start = (
            ("dev.codex.schubert.nk.batch.file.BackupManifestCodecTest",
             ("independentCanonicalGolden", "allFieldsAndMaximumLengths", "structuralByteMutation", "noncanonicalScalarsAndDates", "missingUnknownDuplicateAndOrder", "sizeAndNullBoundaries", "inputOutputOwnership", "concurrentCanonicalRoundTrips",), 186) if codec else
            ("dev.codex.schubert.nk.batch.backup.BackupManifestValuesTest",
             ("completeIdentityAndDirectoryName", "fileDigestBoundsAndOverflow", "versionTokenBoundaries", "stepAndRunBinding", "timeAndPrecisionBoundaries", "nullAndRedaction", "immutableAccessors", "concurrentValueUse",), 178))
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_backup_manifest_inventories(self):
        for codec, validate in ((False, batch.validate_backup_value_suite), (True, batch.validate_backup_codec_suite)):
            suite, expected = self.backup_fixture(codec)
            self.assertEqual(expected, validate(suite))
            for position in range(8):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
                for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                    wrong = copy.deepcopy(suite); ET.SubElement(wrong[position], tag)
                    with self.assertRaises(ValueError): validate(wrong)
                for key, value in (("name", "unknown"), ("name", suite[(position + 1) % 8].get("name")), ("classname", "unknown")):
                    wrong = copy.deepcopy(suite); wrong[position].set(key, value)
                    with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "1"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)

    def test_backup_manifest_literal_trace(self):
        expected = "{\"format\":\"NKBACKUP1\",\"database\":\"schubert_nk\",\"runId\":\"12345678-9abc-def0-8123-456789abcdef\",\"cutoff\":\"2026-09-12T15:00:00.000000Z\",\"startedAt\":\"2026-09-12T15:00:02.123456Z\",\"contentFinishedAt\":\"2026-09-12T15:00:03.654321Z\",\"databaseStep\":{\"id\":90000,\"attempt\":1,\"startedAt\":\"2026-09-12T15:00:00.000000Z\"},\"configurationStep\":{\"id\":90001,\"attempt\":1,\"startedAt\":\"2026-09-12T15:00:01.000000Z\"},\"versions\":{\"host\":\"nk-pt\",\"app\":\"0.1.0-SNAPSHOT\",\"schema\":\"020\",\"os\":\"Ubuntu-26.04.1\",\"jdk\":\"25.0.4\",\"postgresql\":\"18.6\",\"artemis\":\"2.56.0\",\"age\":\"1.2.1\"},\"recipientSha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"files\":{\"schubert_nk.dump\":{\"size\":1,\"sha256\":\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"},\"config.tar\":{\"size\":512,\"sha256\":\"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\"},\"credentials.tar.age\":{\"size\":200,\"sha256\":\"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc\"}}}\n".encode("ascii")
        self.assertEqual(965, len(expected))
        self.assertEqual("733939f4daa4dcb642e6b9a4433c92daf3d42e8ac73a15b0aee914b58571289e",
                         hashlib.sha256(expected).hexdigest())
        self.assertEqual(expected, batch.BACKUP_GOLDEN)
        name = "PT-BAT-186-manifest.json"
        batch.validate_backup_traces({name: expected})
        for wrong in ({}, {name: expected, "unknown": b""}, {name: expected + b"\n"}):
            with self.assertRaises(ValueError): batch.validate_backup_traces(wrong)
        for i in range(len(expected)):
            changed = expected[:i] + bytes([expected[i] ^ 1]) + expected[i+1:]
            with self.assertRaises(ValueError): batch.validate_backup_traces({name: changed})

    @staticmethod
    def atomic_fixture(group):
        cls, names, prefix, start = [
            ("dev.codex.schubert.nk.batch.repository.CleanupStepValuesTest", ("kindStepMapping", "successfulChunkContracts", "rejectionAndDeferredContracts", "summaryCountsAndCompletion", "counterOverflowAndBounds", "nullAndRedaction", "immutableValues", "concurrentValues",), "BAT", 154),
            ("dev.codex.schubert.nk.batch.repository.CleanupStepRepositoryTest", ("actualSevenKindsAndStepTotals", "borrowedStateAndMapping", "nullAndProjection", "allJdbcFailures", "rejectionReasonsAndUnknownTotals", "utcFullHandle", "interruptRuntimeAndResourceOwnership", "concurrentTransactionsAndRollback",), "BAT", 162),
            ("dev.codex.schubert.nk.batch.cleanup.StepCleanupServiceTest", ("allKindsCompleteAndPersistedCounts", "multiChunkResumeAndSharedStep", "lockBackupAndForeignKeyDeferral", "transactionFaultsAndUnknownCommit", "timeoutInterruptAndClockWrap", "counterContinuityAndOverflow", "connectionStateRestorationAndNulls", "concurrencyAndIndependentTrace",), "BAT", 170),
            ("dev.codex.schubert.nk.api.maintenance.StepCleanupBoundaryTest", ("sevenKindAtomicCounts", "handleArgumentsAndIdentity", "backupLockAndRoleBoundary", "zeroChunkLockedRemainder", "retentionAndProtectedRows", "rollbackOverflowAndForeignKey", "typedProjectionAndNoBypass", "appendOnlyMigrationInventory",), "DB-INBOX", 259),
        ][group]
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-{prefix}-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_atomic_cleanup_inventories(self):
        for group, validate in enumerate((batch.validate_atomic_value_suite, batch.validate_atomic_repository_suite,
                                           batch.validate_atomic_service_suite, atomic.validate_suite)):
            suite, expected = self.atomic_fixture(group)
            self.assertEqual(expected, validate(suite))
            for position in range(8):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "1"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[0].set(key, value)
                with self.assertRaises(ValueError): validate(wrong)

    def test_atomic_cleanup_literal_traces(self):
        batch_expected = {
            "PT-BAT-162-seven-kinds.txt": b"NOTIFICATIONS=1|1|END\nQUESTIONS=1|1|END\nSESSIONS=3|3|END\nOUTBOX=2|2|END\nBATCH_RUNS=1|1|END\nINBOX_PROGRESS=2|1|END\nLOG_PROGRESS=3|1|END\n",
            "PT-BAT-165-jdbc.txt": b"repository=53\nfault_positions=53\ndouble_close_pairs=3\n",
            "PT-BAT-171-chunks.txt": b"sessions=1001\nchunks=1000|1|0\nservice_jdbc=171\nresume_delta=0\n",
            "PT-BAT-173-jdbc.txt": b"positive_end=115\nfault_positions=115\ncommit_response_unknown=stored1|resume_delta0\n",
            "PT-BAT-177-service.txt": b"NOTIFICATIONS=RUNNING|1|1|0|0|true\nQUESTIONS=RUNNING|1|1|0|0|true\nSESSIONS=RUNNING|3|3|0|0|true\nOUTBOX=RUNNING|2|2|0|0|true\nBATCH_RUNS=RUNNING|1|1|0|0|true\nINBOX_PROGRESS=RUNNING|2|2|0|0|true\nLOG_PROGRESS=RUNNING|3|3|0|0|true\n",
        }
        sql_expected = {"PT-DB-INBOX-259-seven-kinds.txt": b"NOTIFICATIONS=1|1|0|1|1|false|OK\nQUESTIONS=1|1|0|1|1|false|OK\nSESSIONS=3|3|0|3|3|false|OK\nOUTBOX=2|2|0|2|2|false|OK\nBATCH_RUNS=1|1|0|1|1|false|OK\nINBOX_PROGRESS=1|1|0|2|2|false|OK\nLOG_PROGRESS=1|1|0|3|3|false|OK\n"}
        for expected, constants, validate in ((batch_expected, batch.ATOMIC_TRACES, batch.validate_atomic_traces),
                                               (sql_expected, atomic.TRACES, atomic.validate_traces)):
            self.assertEqual(expected, constants); self.assertIsNone(validate(expected))
            for name in expected:
                missing = dict(expected); del missing[name]
                wrong = dict(expected); wrong[name] += b"X"
                for bad in (missing, wrong, {**expected, "unknown": b""}):
                    with self.assertRaises(ValueError): validate(bad)

    @staticmethod
    def step_fixture(repository=False):
        cls, names, start = (
            ("dev.codex.schubert.nk.batch.repository.BatchRunRepositoryTest",
             ("firstAttemptAndTerminalStates", "ordinarySuccessSkipsByBusinessDate", "backupAlwaysRunsAndAttemptLimit", "explicitAbandonedRecovery", "foreignRunningAndRootIdentity", "exactFinishReplay", "handleIdentityAndMissingRows", "rollbackAndUnknownCommit", "historicalUtcAndFixedRunDay", "clockRegressionPreservesRows", "parentTransactionAndLock", "historyProjectionAndNulls", "jdbcFailurePositions", "interruptionAndRuntime", "concurrentOwnersAndRowLocks", "independentSqlInventoryAndGrants",), 138) if repository else
            ("dev.codex.schubert.nk.batch.repository.BatchStepValuesTest",
             ("closedStepsAndBackupPolicy", "attemptIdentityAndBounds", "terminalStatesAndReasonMatrix", "counterAndStatusBoundaries", "temporalContractAndBusinessDay", "nullContractsAndRedaction", "immutableValueSemantics", "independentConcurrentValues",), 130))
        suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_parent_step_inventories(self):
        for repository, validate in ((False, batch.validate_step_value_suite), (True, batch.validate_step_repository_suite)):
            suite, expected = self.step_fixture(repository)
            self.assertEqual(expected, validate(suite))
            for position in range(len(suite)):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "1"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[0].set(key, value)
                with self.assertRaises(ValueError): validate(wrong)

    def test_parent_step_literal_traces(self):
        expected = {
            "PT-BAT-138-terminals.txt": b"BACKUP_DB=SUCCESS|5|3|0|9|NULL|NULL\nBACKUP_CONFIG=WARNING|5|2|0|8|PROTECTED_RECORDS|protected records retained\nCLEAN_NOTIFICATION=FAILED|6|2|4|0|DATABASE_FAILURE|batch database operation failed\nCLEAN_QUESTION=SKIPPED|0|0|0|0|BACKUP_UNAVAILABLE|verified backup unavailable\nCLEAN_SESSION=SUCCESS|5|3|0|9|NULL|NULL\nCLEAN_INBOX_OUTBOX=WARNING|5|2|0|8|PROTECTED_RECORDS|protected records retained\nCLEAN_LOG=FAILED|6|2|4|0|DATABASE_FAILURE|batch database operation failed\nCLEAN_BATCH_RUN=SKIPPED|0|0|0|0|BACKUP_UNAVAILABLE|verified backup unavailable\nCLEAN_TRANSFER=SUCCESS|5|3|0|9|NULL|NULL\nCLEAN_EXPIRY=WARNING|5|2|0|8|PROTECTED_RECORDS|protected records retained\n",
            "PT-BAT-150-jdbc.txt": b"empty=57/57/2\nhistory=70/70/2\nskip=70/70/2\nrecover=80/80/2\nfinish=50/50/2\nreplay=72/72/2\n",
        }
        self.assertEqual(expected, batch.STEP_TRACES)
        self.assertIsNone(batch.validate_step_traces(expected))
        for name in expected:
            missing = dict(expected); del missing[name]
            wrong = dict(expected); wrong[name] += b"X"
            for bad in (missing, wrong):
                with self.assertRaises(ValueError): batch.validate_step_traces(bad)
        with self.assertRaises(ValueError): batch.validate_step_traces(dict(expected, unknown=b""))
    @staticmethod
    def parent_fixture(kind):
        cls, names, prefix, start = {
            "sql": ("dev.codex.schubert.nk.api.maintenance.InspectionParentBoundaryTest",
                    ("summaryStatesAndCounts", "identityAndTimeBoundaries", "parentLockNamespaces", "roleAndCatalog",
                     "freshReadAndRollback", "concurrentOwners", "noMutationOrPrivateProjection", "appendOnlyMigration"), "PT-DB-INBOX", 251),
            "repository": ("dev.codex.schubert.nk.batch.repository.InspectionSummaryRepositoryTest",
                    ("summaryValueInvariants", "realBoundedRead", "parentStateAndLock", "projectionAndNull",
                     "allJdbcFailurePositions", "historicalUtcIdentity", "freshVisibilityAndBorrowing", "interruptAndRuntime"), "PT-BAT", 114),
            "attempt": ("dev.codex.schubert.nk.batch.cleanup.InspectionAttemptTest",
                    ("matchingSuccessAndWarning", "zeroAndResumedAttemptCounts", "completedBaselineImmutability",
                     "countRegressionAndOverflow", "runIdentityAndMissingEnd", "receiptCodesAndNulls",
                     "redactionAndValueOwnership", "independentConcurrentObservations"), "PT-BAT", 122),
        }[kind]
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"{prefix}-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_parent_summary_inventories(self):
        for kind, validate in (("sql", parent_summary.validate_suite), ("repository", batch.validate_summary_suite),
                               ("attempt", batch.validate_attempt_suite)):
            suite, expected = self.parent_fixture(kind)
            self.assertEqual(expected, validate(suite))
            for position in range(8):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "7"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[0].set(key, value)
                with self.assertRaises(ValueError): validate(wrong)

    def test_parent_summary_literal_trace(self):
        literal = (b"absent=[]\nopen=[0, 0, 0, false]\nemptyEnd=[0, 0, 0, true]\n"
                   b"mixedEnd=[9, 5, 4, true]\nmaxEnd=[9223372036854775807, 9223372036854775806, 1, true]\n")
        expected = {"PT-DB-INBOX-251-states.txt": literal}
        self.assertEqual(expected, parent_summary.TRACES)
        self.assertIsNone(parent_summary.validate_traces(expected))
        for wrong in ({}, dict(expected, unknown=b""), {"PT-DB-INBOX-251-states.txt": literal + b"\0"}):
            with self.assertRaises(ValueError): parent_summary.validate_traces(wrong)

    def test_retirement_literal_traces(self):
        io = b"{acl=1075, attributes=1075, close=854, create=2, filesystem=1075, force=2, namesClose=54, namesHasNext=138, namesIterator=54, namesNext=84, namesOpen=54, openDirectory=477, openEntry=324, openRead=57, openRoot=53, openWriter=2, publish=2, read=114, readClose=57, readSize=114, readonly=1075, sync=13, unlink=5, write=2, writeSize=4, writerClose=2}"
        self.assertEqual(io, batch.RETIREMENT_IO_TRACE)
        with self.assertRaises(ValueError):
            batch.validate_retirement_io(b"{acl=1075, attributes=1075, close=854, create=2, filesystem=1075, force=2, namesClose=54, namesHasNext=138, namesIterator=54, namesNext=84, namesOpen=54, openDirectory=477, openEntry=324, openRead=57, openRoot=53, openWriter=2, publish=2, read=114, readClose=57, readonly=1075, readSize=114, sync=13, unlink=5, write=2, writerClose=2, writeSize=4}")
        self.assertIsNone(batch.validate_retirement_io(io))
        for wrong in (b"", io + b"\0", io.replace(b"openDirectory=477", b"openDirectory=461"),
                      io.replace(b"close=854", b"close=838"), io + b"\n"):
            with self.assertRaises(ValueError): batch.validate_retirement_io(wrong)
        expected = {
            "PT-BAT-090-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n1\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
            "PT-BAT-090-maximum.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n2147483647\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
            "PT-BAT-099-two-activation-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-03T00:00:00.000000Z\n2026-02-07T00:00:00.000001Z\n2\ne6ff18dc21a10852fe4de7e8606fe0ad005c8e242bdc535ea8d391dd052528de\n",
            "PT-BAT-102-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n1\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
            "PT-BAT-102-phases.txt": b"phase0:\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase1:\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase2:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase3:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase4:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase5:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nphase6:\n12345678-9abc-def0-8123-456789abcdef.retire\nphase7:\n",
        }
        self.assertEqual(expected, batch.RETIREMENT_TRACES)
        self.assertIsNone(batch.validate_retirement_traces(expected))
        for key in expected:
            wrong = dict(expected); del wrong[key]
            with self.assertRaises(ValueError): batch.validate_retirement_traces(wrong)
            wrong = dict(expected); wrong[key] += b"\0"
            with self.assertRaises(ValueError): batch.validate_retirement_traces(wrong)
        for wrong in ({}, dict(expected, unknown=b"")):
            with self.assertRaises(ValueError): batch.validate_retirement_traces(wrong)

    @staticmethod
    def retirement_fixture(records=False):
        cls = ("dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest" if records else
               "dev.codex.schubert.nk.batch.file.MaintenanceRunRetirementTest")
        names = (("literalMarkerAndPlanHash", "temporalAndCountInvariants", "nullAndOwnership", "malformedMarkerBytes", "markerAliases", "boundedStorageRecords", "planNameBinding", "concurrentCanonicalRecords") if records else
                 ("candidatesAndProtectedRuns", "strictAgeAndLatestCompletion", "referenceCombinations", "missingAndContradictoryIdentity", "newRetirementPreservesOtherRuns", "preMarkerPlanRecovery", "markerOriginalRecovery", "metadataOnlyRecovery", "planCompletenessAndDigest", "namespaceAndForeignArtifacts", "referenceReappearanceAndDbFaults", "publicationAndDeletionCrashes", "everyIoFailurePreservesState", "scopeNullAndInterruption", "concurrentAndClosedScope", "resourceCloseAndDigestFailure"))
        suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        start = 90 if records else 98
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_retirement_inventory_rejects_nonpassing_cases(self):
        for records in (False, True):
            suite, expected = self.retirement_fixture(records)
            validate = batch.validate_retirement_record_suite if records else batch.validate_retirement_suite
            self.assertEqual(expected, validate(suite))
            for position in range(len(suite)):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "0"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[0].set(key, value)
                with self.assertRaises(ValueError): validate(wrong)

    @staticmethod
    def references_fixture(sql=False):
        cls = ("dev.codex.schubert.nk.api.maintenance.RunReferenceBoundaryTest" if sql else
               "dev.codex.schubert.nk.batch.repository.RunReferenceRepositoryTest")
        names = (("referenceCombinations", "identityConsistency", "temporalAndNullBoundaries", "lockOwnership",
                  "roleAndCatalog", "transactionVisibility", "concurrentOwnership", "migrationAndReadOnlyHistory", "jdbcUtcVectors", "productionUtcBoundaryInventory") if sql else
                 ("referenceValueInvariants", "realReferenceRead", "transactionAndLockContracts",
                  "projectionAndNullContracts", "jdbcFailureMatrix", "interruptionAndRuntime",
                  "rollbackAndFreshVisibility", "independentConcurrentConnections"))
        suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        prefix, start = ("PT-DB-INBOX", 241) if sql else ("PT-BAT", 82)
        return suite, {f"{prefix}-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_run_reference_inventories_and_traces(self):
        for sql in (False, True):
            suite, expected = self.references_fixture(sql)
            validate = references.validate_suite if sql else batch.validate_references_suite
            self.assertEqual(expected, validate(suite))
            for position in range(len(suite)):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "7"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[0].set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
        literal = ("0:[false, false, false, true]\n1:[true, false, false, true]\n"
                   "2:[false, true, false, true]\n3:[true, true, false, true]\n"
                   "4:[false, false, true, true]\n5:[true, false, true, true]\n"
                   "6:[false, true, true, true]\n7:[true, true, true, true]\n").encode("ascii")
        traces = {"PT-DB-INBOX-241-combinations.txt": literal}
        self.assertEqual(traces, references.TRACES)
        self.assertIsNone(references.validate_traces(traces))
        for wrong in ({}, dict(traces, unknown=b""), {"PT-DB-INBOX-241-combinations.txt": literal + b"\0"}):
            with self.assertRaises(ValueError): references.validate_traces(wrong)

    @staticmethod
    def lifecycle_fixture():
        cls = "dev.codex.schubert.nk.batch.file.MaintenanceRunFilesTest"
        names = ("newRunPublication", "resumeActive", "resumeOrphanAnchor", "resumePendingBegin",
                 "resumeCompletedHistory", "completedActiveRecovery", "completeSuccessAndWarning",
                 "completionRetryAndMismatch", "noImplicitNewIdentity", "malformedGraphReferences",
                 "ambiguousPendingStates", "inventoryUnknownAndPartial", "namespacePermissions",
                 "namespaceReplacement", "recordReplacementDuringScan", "listingAndIoFailures",
                 "rootAcquisitionAndCloseFailures", "startCrashBoundaries", "resumeCrashBoundaries",
                 "completionCrashBoundaries", "nullAndClosedContracts", "interruptionAndRuntime",
                 "concurrentScopeOwnership", "fixedFactoryAndReopen")
        suite = ET.Element("testsuite", name=cls, tests="24", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 58)}

    def test_run_lifecycle_inventory_and_nonpassing_cases(self):
        suite, expected = self.lifecycle_fixture()
        self.assertEqual(suite.get("name"), batch.LIFECYCLE_CLASS)
        self.assertEqual(tuple(c.get("name") for c in suite), batch.LIFECYCLE_METHODS)
        self.assertEqual(expected, batch.validate_lifecycle_suite(suite))
        run = "12345678-9abc-def0-8123-456789abcdef"
        activation = "fedcba98-7654-3210-8fed-cba987654321"
        prefix = run + "\n2026-09-12T04:05:06.123456Z\n"
        names = ("attempts/" + activation + ".begin\nattempts/" + activation + ".done\nruns/" + run + ".run\n").encode("ascii")
        traces = {"PT-BAT-058-anchor.txt": ("NKRUN1\n" + prefix).encode("ascii"),
                  "PT-BAT-058-begin.txt": ("NKACT1\n" + prefix + activation + "\n").encode("ascii"),
                  "PT-BAT-058-active.txt": ("NKACT1\n" + prefix + activation + "\n").encode("ascii"),
                  "PT-BAT-064-done-0.txt": ("NKDONE1\n" + prefix + activation + "\n2026-09-12T05:06:07.234567Z\n0\n").encode("ascii"),
                  "PT-BAT-064-done-10.txt": ("NKDONE1\n" + prefix + activation + "\n2026-09-12T05:06:07.234567Z\n10\n").encode("ascii"),
                  "PT-BAT-064-names-0.txt": names, "PT-BAT-064-names-10.txt": names}
        self.assertEqual(traces, batch.LIFECYCLE_TRACES)
        self.assertIsNone(batch.validate_lifecycle_traces(traces))
        for name in traces:
            wrong = dict(traces); del wrong[name]
            with self.assertRaises(ValueError): batch.validate_lifecycle_traces(wrong)
            wrong = dict(traces); wrong[name] = traces[name] + b"\x00"
            with self.assertRaises(ValueError): batch.validate_lifecycle_traces(wrong)
        with self.assertRaises(ValueError): batch.validate_lifecycle_traces(dict(traces, unknown=b""))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_lifecycle_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): batch.validate_lifecycle_suite(wrong)
        for key, value in (("tests", "23"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): batch.validate_lifecycle_suite(wrong)
        for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(key, value)
            with self.assertRaises(ValueError): batch.validate_lifecycle_suite(wrong)

    @staticmethod
    def durable_fixture():
        cls = "dev.codex.schubert.nk.batch.file.DurableRecordFilesTest"
        names = ("literalReads", "newPublication", "sameRecordReuse", "expectedRetirement",
                 "nameContentAndNull", "metadataAndFilesystems", "boundedChannels",
                 "namespaceAndReplacement", "allReadFailures", "allWriteRetireFailures",
                 "interruptionsAndUnknownRuntime", "concurrencyAndNative")
        suite = ET.Element("testsuite", name=cls, tests="12", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 46)}

    def test_durable_record_inventory_and_nonpassing_cases(self):
        suite, expected = self.durable_fixture()
        self.assertEqual(suite.get("name"), batch.DURABLE_CLASS)
        self.assertEqual(tuple(c.get("name") for c in suite), batch.DURABLE_METHODS)
        self.assertEqual(expected, batch.validate_durable_suite(suite))
        prefix = "12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\n"
        activation = "fedcba98-7654-3210-8fed-cba987654321\n"
        traces = {"PT-BAT-047-anchor.txt": ("NKRUN1\n" + prefix).encode("ascii"),
                  "PT-BAT-047-active.txt": ("NKACT1\n" + prefix + activation).encode("ascii"),
                  "PT-BAT-047-begin.txt": ("NKACT1\n" + prefix + activation).encode("ascii"),
                  "PT-BAT-047-done-10.txt": ("NKDONE1\n" + prefix + activation + "2026-09-12T05:06:07.234567Z\n10\n").encode("ascii")}
        self.assertEqual(traces, batch.DURABLE_TRACES)
        self.assertIsNone(batch.validate_durable_traces(traces))
        for name in traces:
            wrong = dict(traces); del wrong[name]
            with self.assertRaises(ValueError): batch.validate_durable_traces(wrong)
            wrong = dict(traces); wrong[name] = b"unknown"
            with self.assertRaises(ValueError): batch.validate_durable_traces(wrong)
        with self.assertRaises(ValueError): batch.validate_durable_traces(dict(traces, unknown=b""))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_durable_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): batch.validate_durable_suite(wrong)
        for key, value in (("tests", "11"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): batch.validate_durable_suite(wrong)
        for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(key, value)
            with self.assertRaises(ValueError): batch.validate_durable_suite(wrong)

    @staticmethod
    def record_fixture():
        cls = "dev.codex.schubert.nk.batch.file.MaintenanceRecordsTest"
        names = ("literalRecords", "identityTemporalBoundaries", "malformedSources", "scalarAliases",
                 "completionInvariants", "nullContracts", "ownershipAndRedaction", "concurrentUse")
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 38)}

    def test_run_record_inventory_and_nonpassing_cases(self):
        suite, expected = self.record_fixture()
        self.assertEqual(suite.get("name"), batch.RECORD_CLASS)
        self.assertEqual(tuple(c.get("name") for c in suite), batch.RECORD_METHODS)
        self.assertEqual(expected, batch.validate_record_suite(suite))
        prefix = "12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\n"
        activation = "fedcba98-7654-3210-8fed-cba987654321\n"
        end = "2026-09-12T05:06:07.234567Z\n"
        traces = {"PT-BAT-038-anchor.txt": ("NKRUN1\n" + prefix).encode("ascii"),
                  "PT-BAT-038-activation.txt": ("NKACT1\n" + prefix + activation).encode("ascii"),
                  "PT-BAT-038-completion-0.txt": ("NKDONE1\n" + prefix + activation + end + "0\n").encode("ascii"),
                  "PT-BAT-038-completion-10.txt": ("NKDONE1\n" + prefix + activation + end + "10\n").encode("ascii")}
        self.assertEqual(traces, batch.RECORD_TRACES)
        self.assertIsNone(batch.validate_record_traces(traces))
        for name in traces:
            wrong = dict(traces); del wrong[name]
            with self.assertRaises(ValueError): batch.validate_record_traces(wrong)
            wrong = dict(traces); wrong[name] = b"unknown"
            with self.assertRaises(ValueError): batch.validate_record_traces(wrong)
        with self.assertRaises(ValueError): batch.validate_record_traces(dict(traces, unknown=b""))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_record_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): batch.validate_record_suite(wrong)
        for key, value in (("tests", "7"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): batch.validate_record_suite(wrong)
        for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(key, value)
            with self.assertRaises(ValueError): batch.validate_record_suite(wrong)

    @staticmethod
    def handoff_fixture():
        cls = "dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoffTest"
        names = ("actualTransactionHandoff", "preconditionsAndReentrantLock", "callbackFailuresAndNull",
                 "reacquisitionConflict", "jdbcFailureMatrix", "invalidResultMatrix",
                 "stateChangesAndInterrupts", "concurrentGapCompetition",
                 "callbackIdentitySurvivesReacquisitionSqlFailure")
        suite = ET.Element("testsuite", name=cls, tests="9", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        expected = {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names[:8], 30)}
        expected["PT-BAT-282"] = cls + "#" + names[8]
        return suite, expected

    def test_handoff_inventory_and_nonpassing_cases(self):
        suite, expected = self.handoff_fixture()
        self.assertEqual(suite.get("name"), batch.HANDOFF_CLASS)
        self.assertEqual(tuple(c.get("name") for c in suite), batch.HANDOFF_METHODS)
        self.assertEqual(expected, batch.validate_handoff_suite(suite))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_handoff_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): batch.validate_handoff_suite(wrong)
        for key, value in (("tests", "8"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): batch.validate_handoff_suite(wrong)
        for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(key, value)
            with self.assertRaises(ValueError): batch.validate_handoff_suite(wrong)

    def test_unit_literal_traces(self):
        expected = {
            "PT-OPS-UNIT-001-state.txt": b"quiescent=true\nreceipt=10\nsameInvocationReceipt=none\n",
            "PT-OPS-UNIT-010-receipt-0.txt": b"receipt=0\ncommands=3\n",
            "PT-OPS-UNIT-010-receipt-10.txt": b"receipt=10\ncommands=3\n"}
        self.assertEqual(expected, launch.UNIT_TRACES)
        launch.validate_unit_traces(expected)
        for name in expected:
            wrong = dict(expected); del wrong[name]
            with self.assertRaises(ValueError): launch.validate_unit_traces(wrong)
            for changed in (b"", expected[name] + b"\0", expected[name].replace(b"receipt=", b"receipt=9")):
                wrong = dict(expected); wrong[name] = changed
                with self.assertRaises(ValueError): launch.validate_unit_traces(wrong)
        with self.assertRaises(ValueError): launch.validate_unit_traces(dict(expected, unknown=b""))

    def test_unit_independent_golden(self):
        data = (Path(__file__).resolve().parents[2] / "src/schubert-nk-batch/src/test/resources/inspector/unit-golden.txt").read_bytes()
        self.assertEqual(373, len(data))
        self.assertEqual("2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6",
                         hashlib.sha256(data).hexdigest())
        launch.validate_unit_golden(data)
        for wrong in (b"", data[:-1], data + b"\n"):
            with self.assertRaises(ValueError): launch.validate_unit_golden(wrong)
        for position in range(len(data)):
            wrong = bytearray(data); wrong[position] ^= 1
            with self.assertRaises(ValueError): launch.validate_unit_golden(bytes(wrong))

    def test_shared_batch_program_ownership(self):
        names = ("dev.codex.schubert.nk.batch.repository.CleanupRepositoryTest",
                 "dev.codex.schubert.nk.batch.cleanup.LogCleanupServiceTest",
                 "dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoffTest",
                 "dev.codex.schubert.nk.batch.file.MaintenanceRecordsTest",
                 "dev.codex.schubert.nk.batch.file.DurableRecordFilesTest",
                 "dev.codex.schubert.nk.batch.file.MaintenanceRunFilesTest",
                 "dev.codex.schubert.nk.batch.repository.RunReferenceRepositoryTest",
                 "dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest",
                 "dev.codex.schubert.nk.batch.file.MaintenanceRunRetirementTest",
                 "dev.codex.schubert.nk.batch.repository.InspectionSummaryRepositoryTest",
                 "dev.codex.schubert.nk.batch.cleanup.InspectionAttemptTest",
                 "dev.codex.schubert.nk.batch.repository.BatchStepValuesTest",
                 "dev.codex.schubert.nk.batch.repository.BatchRunRepositoryTest",
                 "dev.codex.schubert.nk.batch.repository.CleanupStepValuesTest",
                 "dev.codex.schubert.nk.batch.repository.CleanupStepRepositoryTest",
                 "dev.codex.schubert.nk.batch.cleanup.StepCleanupServiceTest",
                 "dev.codex.schubert.nk.batch.backup.BackupManifestValuesTest",
                 "dev.codex.schubert.nk.batch.file.BackupManifestCodecTest",
                 "dev.codex.schubert.nk.batch.file.BackupArtifactVerifierTest",
                 "dev.codex.schubert.nk.batch.repository.BackupStepRepositoryTest",
                 "dev.codex.schubert.nk.batch.backup.BackupCommitServiceTest",
                 "dev.codex.schubert.nk.batch.file.BackupManifestReaderTest",
                 "dev.codex.schubert.nk.batch.file.BackupManifestPublisherTest",
                 "dev.codex.schubert.nk.batch.file.BackupBundlePublisherTest",
                 "dev.codex.schubert.nk.batch.file.BackupBundleCompletionTest",
                 "dev.codex.schubert.nk.batch.bootstrap.BatchRuntimeDependencyTest",
                 "dev.codex.schubert.nk.batch.repository.ExpiryAuditRepositoryTest",
                 "dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest",
                 "dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest",
                 "dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest",
                 "dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest",
                 "dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest",
                 "dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest",
                 "dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest",
                 "dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest",
                 "dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest",
                 "dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest",
                 "dev.codex.schubert.nk.batch.platform.InspectorUnitProbeTest",
                 "dev.codex.schubert.nk.batch.mq.ArtemisReadinessClientTest",
                 "dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessClientTest",
                 "dev.codex.schubert.nk.batch.mq.ArtemisAddressSettingsReadinessClientTest",
                 "dev.codex.schubert.nk.batch.mq.ArtemisAcceptorReadinessClientTest",
                 "dev.codex.schubert.nk.batch.mq.ArtemisRoleReadinessClientTest",
                 "dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClientTest",
                 "dev.codex.schubert.nk.batch.mq.ArtemisExpiryManagementAuthorizationTest",
                 "dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeClientTest")
        names += ("dev.codex.schubert.nk.batch.mq.ArtemisStartupObservationTest",)
        suites = [ET.Element("testsuite", name=n) for n in names]
        self.assertEqual(47, len(suites))
        self.assertEqual(suites[:27], batch.select_program_suites(suites))
        for bad in ([], suites[:-1], suites + [suites[0]], [suites[0], suites[0], suites[2]]):
            with self.assertRaises(ValueError): batch.select_program_suites(bad)
        # BUG-150/YKT-116: visit every independently specified class after inventory growth.
        for position in range(len(suites)):
            bad = copy.deepcopy(suites); bad[position].set("name", "unknown")
            with self.assertRaises(ValueError): batch.select_program_suites(bad)
            bad = copy.deepcopy(suites); del bad[position]
            with self.assertRaises(ValueError): batch.select_program_suites(bad)
            bad = copy.deepcopy(suites); bad[position] = copy.deepcopy(suites[(position + 1) % len(suites)])
            with self.assertRaises(ValueError): batch.select_program_suites(bad)

    def test_shared_storage_program_ownership(self):
        self.assertFalse(scenario.scenario_storage_suite("dev.codex.schubert.nk.storage.LinuxFileLockTest"))
        self.assertFalse(scenario.scenario_storage_suite("dev.codex.schubert.nk.storage.PrivateDirectoryEntryTest"))
        self.assertFalse(scenario.scenario_storage_suite("dev.codex.schubert.nk.storage.ChildDirectoryPublicationTest"))
        self.assertFalse(scenario.scenario_storage_suite("dev.codex.schubert.nk.storage.PrivateChildDirectoryTest"))
        self.assertFalse(scenario.scenario_storage_suite("dev.codex.schubert.nk.api.maintenance.InspectorDeploymentTest"))
        for name in ("LinuxDirectoryCallsTest", "OwnedTransferDirectoryTest", "LinuxInodeSecurityTest"):
            self.assertTrue(scenario.scenario_storage_suite("dev.codex.schubert.nk.storage." + name))

    def test_current_ownership_and_scope_descriptions(self):
        suffix = ("Full module coverage includes both; OPS IDs are certified separately by022/018_NK-OPS-001. "
                  "No duplicate PT credit.")
        self.assertEqual("Batch module327 PT = NK-BAT-001241 + NK-OPS-00186. " + suffix,
                         batch.ownership_description(327, 241))
        self.assertEqual("Batch module247 PT = NK-BAT-001177 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(247, 177))
        self.assertEqual("Batch module263 PT = NK-BAT-001193 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(263, 193))
        self.assertEqual("Batch module311 PT = NK-BAT-001225 + NK-OPS-00186. " + suffix,
                         batch.ownership_description(311, 225))
        self.assertEqual("Batch module295 PT = NK-BAT-001209 + NK-OPS-00186. " + suffix,
                         batch.ownership_description(295, 209))
        self.assertEqual("Batch module279 PT = NK-BAT-001209 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(279, 209))
        self.assertEqual("Batch module65 PT = NK-BAT-00137 + NK-OPS-00128. " + suffix,
                         batch.ownership_description(65, 37))
        self.assertEqual("Batch module91 PT = NK-BAT-00137 + NK-OPS-00154. " + suffix,
                         batch.ownership_description(91, 37))
        self.assertEqual("Batch module107 PT = NK-BAT-00137 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(107, 37))
        self.assertEqual("Batch module115 PT = NK-BAT-00145 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(115, 45))
        self.assertEqual("Batch module127 PT = NK-BAT-00157 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(127, 57))
        self.assertEqual("Batch module151 PT = NK-BAT-00181 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(151, 81))
        self.assertEqual("Batch module159 PT = NK-BAT-00189 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(159, 89))
        self.assertEqual("Batch module183 PT = NK-BAT-001113 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(183, 113))
        self.assertEqual(("OS lock continuity and child termination",
                          "durable authoritative run and parent lifecycle", "real backup artifact and full cleanup callers",
                          "actual root systemd credential deployment", "actual NK characterization and IT/ST"),
                         launch.UNVERIFIED_PARENT_GATES)
        self.assertIn("borrowed-root admission/read/publish", launch.DEPLOYMENT_LIMITATIONS)
        self.assertIn("Root UID/GID/tmpfs admission is synthetic", launch.DEPLOYMENT_LIMITATIONS)
        for gate_name in launch.UNVERIFIED_PARENT_GATES:
            self.assertIn(gate_name, launch.DEPLOYMENT_LIMITATIONS)
        self.assertEqual((
            {"method": "MaintenanceFileLock.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS341/343 require fixed Linux /run", "owner": "NK-OPS-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-OPS-LOCK-007", "coverageExcluded": False},
            {"method": "InspectorEnvironmentFiles.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS343 require fixed Linux /etc and /run", "owner": "NK-OPS-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-OPS-NS-008", "coverageExcluded": False},
            {"method": "MaintenanceRunFiles.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS343 require fixed Linux /var", "owner": "NK-BAT-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-BAT-081", "coverageExcluded": False}),
            launch.REVIEWED_STATIC_DIAGNOSTICS)
        self.assertEqual((launch.REVIEWED_STATIC_DIAGNOSTICS[2],), batch.REVIEWED_STATIC_DIAGNOSTICS)

    def test_backup_rerun_inventory_and_nonpassing_cases(self):
        cls = "dev.codex.schubert.nk.api.maintenance.BackupRerunBoundaryTest"
        names = ("sameDayBackupReruns", "ordinarySuccessStillUnique", "attemptAndDateBoundaries",
                 "failureAndLatestSuccessHistory", "transactionRollbackAndMigration",
                 "concurrentSuccessAndAttemptConflicts", "cleanupGatesWithRepeatedBackups", "catalogAndPrivileges")
        self.assertEqual(cls, backup.CLASS)
        self.assertEqual(names, backup.METHODS)
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-DB-INBOX-{i:03}": cls + "#" + name for i, name in enumerate(names, 233)}, backup.validate_suite(suite))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): backup.validate_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): backup.validate_suite(wrong)
        for key, value in (("tests", "7"), ("name", "other"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): backup.validate_suite(wrong)
        for key, value in (("name", "other"), ("name", names[1]), ("classname", "other")):
            wrong = copy.deepcopy(suite); wrong[0].set(key, value)
            with self.assertRaises(ValueError): backup.validate_suite(wrong)

    def test_launch_inventory_and_nonpassing_cases(self):
        prefix = "dev.codex.schubert.nk.api.maintenance."
        groups = [(prefix + "InspectorLaunchConfigurationTest", 221,
                   ("validConfiguration", "missingUnknownAndArguments", "scalarBoundaries", "versionAndSnapshotContracts")),
                  (prefix + "InspectorLauncherTest", 225,
                   ("successWarningAndFailureStatus", "expectedFailuresAndRedaction", "nativeFactoryFailure", "receiptAndOutputFailure",
                    "nullContracts", "mainAndFatalHandler", "concurrentInvocations", "actualJvmEntry"))]
        self.assertEqual(groups, list(launch.GROUPS))
        self.check_launch_inventory(groups, False)

    def test_deployment_inventory_and_nonpassing_cases(self):
        groups = [("dev.codex.schubert.nk.storage.ResourceScopeTest", 1,
                   ("successfulOwnership", "knownIoFailures", "unknownBodyFailures", "knownBodyUnknownCleanup",
                    "unknownCompoundFailures", "nullAndNullableContracts", "nestedScopes", "concurrentScopes")),
                  ("dev.codex.schubert.nk.api.maintenance.InspectorDeploymentTest", 1,
                   ("renderedShellCheck", "statusMapping", "malformedReceipts", "argumentsAndPlaceholders",
                    "realMainBridge", "baseUnitAndSyntax", "previousProfiles", "releaseClasspathAndIsolation")),
                  ("dev.codex.schubert.nk.storage.LinuxFileLockTest", 1,
                   ("nativeRoundTrip", "externalFlockInteroperability", "fcntlIsNotFlock", "callbackFailureAndClose",
                    "nativeErrorsAndFlags", "inputAndPlatformContracts", "concurrentSingleWinner", "retainedInodeAndDescriptorLifetime")),
                  ("dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest", 1,
                   ("admittedRealLock", "contentionAndIndependentInvocations", "rootAndFilesystemPolicy", "inodeAndAttributePolicy",
                    "replacementAndPostconditions", "ioAndCloseFailures", "constructorAndNativeBoundary", "fixedProvisioningContract")),
                  ("dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest", 1,
                   ("literalAndOrder", "nonStoppedStates", "malformedFields", "byteAndNullContracts",
                    "gateOrderAndFreshReads", "interruptAndFailure", "concurrentChecks", "factoryAndContracts")),
                  ("dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest", 9,
                   ("fixedCommandAndSuccess", "commandFailure", "timeoutAndTermination", "interruptedWait",
                    "outputBoundaries", "closeFailures", "nativeEnvironmentAndRead", "nullAndRuntimeContracts")),
                  ("dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest", 1,
                   ("independentGolden", "mutationAndRunBinding", "boundariesNullAndOwnership", "concurrentUse")),
                  ("dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest", 1,
                   ("canonicalFixtures", "sourceAndSyntaxRejection", "urlBoundaries", "versionBoundaries", "sizeNullAndRedaction", "concurrentValidation")),
                  ("dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest", 1,
                   ("staticReadAndBoundaries", "runReadAndBinding", "permissionAndFilesystem", "metadataAndNull",
                    "boundedReadsAndMutation", "inodeReplacementAndOwnership", "ioFaultsAndRedaction", "concurrentAndConstructor")),
                  ("dev.codex.schubert.nk.storage.PrivateDirectoryEntryTest", 1,
                   ("nativePrivateCreation", "atomicNoReplace", "scopedOwnership", "nameAndNullContracts",
                    "faultAndUncertainOutcomes", "retainedNamespace", "concurrentSinglePublication", "unsupportedAndNativeArguments")),
                  ("dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest", 1,
                   ("createAndRetire", "sameRunAndDifferentRun", "privatePartCollisions", "permissionsAndNull",
                    "boundedWrites", "replacementsAndRetention", "createFailureMatrix", "reuseFailureMatrix",
                    "retireFailureMatrix", "interruptionAndRuntime", "concurrentInvocations", "nativeAndConstructor")),
                  ("dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest", 1,
                   ("canonicalByteBoundaries", "malformedAndNull", "ownedCommandAndExit", "timeoutInterruptAndTermination",
                    "stdioFailureMatrix", "sourceBufferAndNoLeak", "concurrentLookup", "nativeFactory")),
                  ("dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest", 1,
                   ("prepareCallbackRetire", "callbackFailureRetention", "namespaceAndStaticIdentity", "permissionsAndAccounts",
                    "allOpenCloseFailures", "lateFailureAndInterruption", "concurrentScopes", "constructorAndFactory")),
                  ("dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest", 1,
                   ("strictGolden", "propertyInventory", "byteBoundaries", "scalarBounds",
                    "quiescentStates", "freshReceipt", "immutabilityAndNull", "concurrentSnapshots")),
                  ("dev.codex.schubert.nk.batch.platform.InspectorUnitProbeTest", 9,
                   ("fixedCommands", "stableTerminalAndReceipt", "unstableAndNonempty", "commandFailures",
                    "boundedOutputAndTimeout", "interruptions", "allResourceFailures", "nativeEnvironmentAndConcurrency"))]
        groups.append(("dev.codex.schubert.nk.storage.ChildDirectoryPublicationTest", 1,
                      ("nativeDirectoryPublication", "noReplaceAndSourceType", "nameNullAndClosed", "everyNativeFailure",
                       "uncertainPublication", "compoundFailures", "retainedParentCapability", "concurrentNoReplace")))
        groups.append(("dev.codex.schubert.nk.storage.PrivateChildDirectoryTest", 1,
                      ("nativePrivateCreation", "existingEntriesPreserved", "nameNullAndClosed", "everyNativeFailure",
                       "compoundFailures", "retainedParentCapability", "unsupportedAdapter", "concurrentNewOnly")))
        groups.append(("dev.codex.schubert.nk.api.database.PostgresDeploymentTest", 1,
                      ("literalConfiguration", "nativeConfiguration", "literalHba", "nativeHba",
                       "roleTimeouts", "invalidConfiguration", "invalidHba", "isolationAndEvidence")))
        groups.append(("dev.codex.schubert.nk.batch.mq.ArtemisReadinessClientTest", 1,
                      ("opsMq001ActualBrokerHasSixDurableAnycastPairs", "opsMq002MissingLiveQueueFailsWithoutRecreation",
                       "opsMq003EveryAddressAndQueueMismatchFailsClosed", "opsMq004NullProviderFaultAndBorrowedConcurrentSession")))
        groups.append(("dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessClientTest", 5,
                      ("opsMq005ReadsActualBrokerWithoutChangingOrClosingBorrowedSession",
                       "opsMq006EveryApprovedValueIsCheckedAndDiskBoundaryIsStrict",
                       "opsMq007NullMalformedAndProviderFailureAreRedactedWithoutSessionOwnership",
                       "opsMq008ProductionOpsRoleCanReadEffectiveManagementValues",
                       "opsMq009MissingManagementReplyIsBoundedAndInterruptIsRestored")))
        groups.append(("dev.codex.schubert.nk.batch.mq.ArtemisAddressSettingsReadinessClientTest", 10,
                      ("opsMq010ReadsSixEffectiveSettingsWithOpsRole",
                       "opsMq011RejectsEveryCommonAndCapacityDriftAndMissingValues",
                       "opsMq012RejectsNullMalformedUnknownAndProviderFailures")))
        groups.append(("dev.codex.schubert.nk.batch.mq.ArtemisAcceptorReadinessClientTest", 13,
                      ("opsMq013RealLoopbackCoreAcceptorAndOpsOnlyManagement",
                       "opsMq014RejectsEveryAcceptorFieldDriftAndExtraListener",
                       "opsMq015NullMalformedStartedAndProviderFailuresAreRedacted")))
        groups.append(("dev.codex.schubert.nk.batch.mq.ArtemisRoleReadinessClientTest", 16,
                      ("opsMq016LiveEffectiveSevenRoleMatchesAndApplicationDenial",
                       "opsMq017RejectsEachPermissionDriftMissingExcessRoleAndMalformedProjection",
                       "opsMq018NullMalformedProviderAndEncoderFailuresAreRedacted")))
        groups.append(("dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClientTest", 19,
                      ("opsMq019LiveSixEmptyQueueMetricsAndApplicationDenial",
                       "opsMq020EveryCountAndByteBoundaryIncludingDlqAlert",
                       "opsMq021NullInvalidMetricsAndProviderFaultAreRedacted")))
        groups.append(("dev.codex.schubert.nk.batch.mq.ArtemisExpiryManagementAuthorizationTest", 22,
                      ("opsMq022MaintenanceCanOnlyInspectAndRemoveSelectedExpiryMessages",)))
        groups.append(("dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeClientTest", 23,
                      ("opsMq023FixedCutoffCountAndByteReconciliationWithoutCallerSelector",
                       "opsMq024RejectsEveryCounterDriftOverflowAndProviderFailure",
                       "opsMq025RejectsMissingMalformedOrUnboundedManagementSelector",
                       "opsMq026RealBrokerRemovesOnlyActualExpiredMessage",
                       "opsMq027RejectsUnstagedOrDriftedObservationBeforeRemove",
                       "opsMq028StrictSevenDayCutoffRetainsSubmillisecondPrecision")))
        groups.append(("dev.codex.schubert.nk.batch.mq.ArtemisStartupObservationTest", 29,
                       ("opsMq029OrderedReadOnlyObservation", "opsMq030FailClosedAndNoLaterChecks",
                       "opsMq031MalformedPressureAndFatalContracts")))
        groups.append(("dev.codex.schubert.nk.api.maintenance.ApplicationServiceUnitTest", 1,
                       ("apiDependencyCredentialAndResourceContract", "webDependencyCredentialAndResourceContract",
                        "noSecretInEnvironmentOrShellAndNoAutomaticWritableEscalation",
                        "renderedSyntaxIsAcceptedWithoutStartingService")))
        groups.append(("dev.codex.schubert.nk.api.bootstrap.ApiJdbcPoolTest", 1,
                       ("opsDbpool001RealRoleAndFixedConfiguration", "opsDbpool002EightBorrowersAndNinthTimeout",
                        "opsDbpool003NullAndUnavailableFailBeforeReady")))
        groups.append(("dev.codex.schubert.nk.web.bootstrap.WebJdbcPoolTest", 4,
                       ("opsDbpool004RealRoleAndFixedConfiguration", "opsDbpool005TwoBorrowersAndThirdTimeout",
                        "opsDbpool006NullAndUnavailableFailBeforeReady")))
        groups.append(("dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest", 1,
                       ("opsApiCfg001IndependentDefaultsAndCanonicalHash", "opsApiCfg002LayeredNonSecretOverridesAndScalarTypes",
                        "opsApiCfg003YamlsRejectDuplicateUnknownSecretAndStructures", "opsApiCfg004AllFixedKeysUrlsAndRootsFailClosed",
                        "opsApiCfg005NullUnknownAndConcurrentDeterminism", "opsApiCfg006ShippedTemplatesMatchApprovedDefaults")))
        groups.append(("dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfigTest", 1,
                       ("opsWebCfg001IndependentDefaultsAndCanonicalHash", "opsWebCfg002LayeredRangesAndScalarTypes",
                        "opsWebCfg003RejectMalformedUnknownSecretAndDecodedValues", "opsWebCfg004FixedKeysPortsTimeoutsCountsAndRoots",
                        "opsWebCfg005NullUnknownAndConcurrentDeterminism", "opsWebCfg006ShippedTemplatesMatchApprovedDefaults",
                        "opsWebCfg007ExplicitDbMqSourcesAndNegativeBoundaries")))
        groups.append(("dev.codex.schubert.nk.storage.ServiceConfigFilesTest", 1,
                       ("opsCfgfile001FixedNamesAndIndependentBytes", "opsCfgfile002MissingSymlinkAndNonRegularAreRejected",
                        "opsCfgfile003LengthEncodingAndModeBoundaries", "opsCfgfile004RootAndFileIdentityPolicy",
                        "opsCfgfile005IndependentAttributeMutationMatrix", "opsCfgfile006NullConcurrentAndOwnedCloseFailure",
                        "opsCfgfile007MidReadFaultsAndInodeDrift")))
        groups.append(("dev.codex.schubert.nk.storage.ServiceCredentialLocationTest", 1,
                       ("opsCredloc001AcceptsPrivateAbsoluteLocationWithoutOtherEnvironmentRetention",
                        "opsCredloc002RejectsMissingEmptyRelativeAndRoot",
                        "opsCredloc003RejectsAliasTraversalAndControlBytes", "opsCredloc004BoundsAndNullContracts",
                        "opsCredloc005ConcurrentFreshMapsDoNotChangeSnapshot")))
        groups.append(("dev.codex.schubert.nk.storage.ServiceCredentialIdTest", 1,
                       ("opsCredid001ApiExactlyFiveRequiredIds", "opsCredid002WebExactlyFiveRequiredIds",
                        "opsCredid003ServicesAreDisjointAndImmutable", "opsCredid004NullServiceRejected")))
        groups.append(("dev.codex.schubert.nk.api.bootstrap.ApiConfigurationLoaderTest", 1,
                       ("opsApiLoad001FixedServiceAndLayerOrder", "opsApiLoad002SourceAndParserFailuresStayDistinct",
                        "opsApiLoad003NullContractsAndProductionFactory", "opsApiLoad004ConcurrentFreshReads",
                        "opsApiLoad005EnvironmentIsExactBeforeFileRead")))
        groups.append(("dev.codex.schubert.nk.web.bootstrap.WebConfigurationLoaderTest", 1,
                       ("opsWebLoad001FixedServiceAndLayerOrder", "opsWebLoad002SourceAndParserFailuresStayDistinct",
                        "opsWebLoad003NullContractsAndProductionFactory", "opsWebLoad004ConcurrentFreshReads",
                        "opsWebLoad005EnvironmentIsExactBeforeFileRead")))
        groups.append(("dev.codex.schubert.nk.api.bootstrap.ApiStartupInputsTest", 1,
                       ("opsApiInput001CombinesIndependentFixedInputs", "opsApiInput002MissingPrivateLocationStopsBeforeSourceRead",
                        "opsApiInput003SourceFailureAndConfigAdmissionStayDistinct", "opsApiInput004NullContracts")))
        groups.append(("dev.codex.schubert.nk.web.bootstrap.WebStartupInputsTest", 1,
                       ("opsWebInput001CombinesIndependentFixedInputs", "opsWebInput002MissingPrivateLocationStopsBeforeSourceRead",
                        "opsWebInput003SourceFailureAndConfigAdmissionStayDistinct", "opsWebInput004NullContracts")))
        groups.append(("dev.codex.schubert.nk.api.file.ServiceCredentialReaderTest", 1,
                       ("opsCredread001AllFixedIdsReturnOwnedExactBytes",
                        "opsCredread002RejectsCrossServiceAndNullBeforeIo",
                        "opsCredread003MissingSymlinkAndNonregularFailClosed",
                        "opsCredread004RootAndAclAdmissionBeforeContent",
                        "opsCredread005KeyPasswordSizeMetadataAndDeviceBoundaries",
                        "opsCredread006ReadSizeCloseAndRootDriftFailuresEraseBuffer",
                        "opsCredread007EntryCloseAndBorrowedRootLifetime",
                        "opsCredread008ConcurrentIndependentOwnedReads",
                        "opsCredread009DbAndMqPasswordDecodeWithOwnedCopies",
                        "opsCredread010SixKeysDecodeCanonicalCurrentMaterial",
                        "opsCredread011KindServiceAndNullRejectBeforeIo",
                        "opsCredread012MalformedContentErasesOwnedBytesAndRedacts")))
        groups.append(("dev.codex.schubert.nk.api.maintenance.ServiceDatabaseAdmissionTest", 1,
                       ("opsDbadmit001ExactApiAndWebRolesOnIsolatedPg",
                        "opsDbadmit002WrongRoleTransactionAndReadonlyRejectWithoutOwningConnection",
                        "opsDbadmit003RowsNullMismatchDuplicateAndSqlFaultsFailClosed",
                        "opsDbadmit004StrictUrlAndNullContracts")))
        groups.append(("dev.codex.schubert.nk.api.file.ServiceCredentialSetTest", 1,
                       ("opsCredset001FiveFixedMaterialsPerServiceAreOwnedAndClosed",
                        "opsCredset002WrongIdNullAndClosedStateReject",
                        "opsCredset003MissingMalformedAndUncheckedFailureClearPartial",
                        "opsCredset004ConcurrentIndependentLoads",
                        "opsCredset005CallerMonitorCannotDelaySecretCopyOrClose")))
        groups.append(("dev.codex.schubert.nk.api.bootstrap.ApiProcessMainTest", 1,
                       ("opsApiMain001AdmissionBeforeAssemblyAndUnwiredNativeRefusal", "opsApiMain002FailuresAndUnknownRemainNonSuccess",
                        "opsApiMain003FatalDiagnosticIsFixed", "opsApiMain004ActualExternalMainRejectsMissingConfigAndArgv")))
        groups.append(("dev.codex.schubert.nk.web.bootstrap.WebProcessMainTest", 1,
                       ("opsWebMain001AdmissionBeforeAssemblyAndUnwiredNativeRefusal", "opsWebMain002FailuresAndUnknownRemainNonSuccess",
                        "opsWebMain003FatalDiagnosticIsFixed", "opsWebMain004ActualExternalMainRejectsMissingConfigAndArgv")))
        groups.append(("dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSourceTest", 1,
                       ("opsDbsource001BothFixedRolesAndInputErasure", "opsDbsource002EveryPhysicalPoolConnectionIsAdmitted",
                        "opsDbsource003NullProviderWrongRoleAndSqlFailuresCloseBeforeRefusal",
                        "opsDbsource004UnknownAndCompoundFailuresPreserveIdentity",
                        "opsDbsource005OptionsNullUrlSizeAndConstructorFailureErasure",
                        "opsDbsource006ConcurrentConnectionsAndPrivateMonitor")))
        groups.append(("dev.codex.schubert.nk.api.file.ServiceProcessResourcesTest", 1,
                       ("opsApiRes001RealFiveMaterialsAndAdmittedPoolOwnedScope",
                        "opsApiRes002CallbackAndPoolCloseCompoundFailuresDoNotReturnSuccess",
                        "opsApiRes003PartialAcquisitionFailureClearsPasswordAndMaterials",
                        "opsApiRes004MissingMalformedAndAclFailureNeverCreatesDatabase",
                        "opsApiRes005NullAndNativeFactoryBoundaries", "opsApiRes006IndependentConcurrentScopes",
                        "opsWebRes001WebOnlyFiveMaterialsTechnicalRoleAndTwoConnectionCeiling")))
        groups.append(("dev.codex.schubert.nk.storage.LinuxProcessExecTest", 1, ("opsExec001LiteralVectorsAndArenaLifetime", "opsExec002EveryNativeReturnIsRedactedFailure", "opsExec003InputNullAndPathContracts", "opsExec004VectorAndStringBoundaries", "opsExec005PlatformAndSymbolContracts", "opsExec006UnknownFailureIdentityAndArenaClose", "opsExec007ConcurrentInputsRemainIndependent", "opsExec008ActualReplacementKeepsPidAndOnlyPreparedEnvironment")))
        groups.append(("dev.codex.schubert.nk.storage.LinuxExecDescriptorsTest", 1, ("opsXfd001ExactlyTwoFlagsRestoredInReverseOrder", "opsXfd002EveryNativeFailureAndPartialTransition", "opsXfd003IoAndUnknownBodyPreserveOwnership", "opsXfd004CompoundCleanupUnknownPriority", "opsXfd005NullDescriptorAndBoundaryContracts", "opsXfd006PlatformAndSymbolContracts", "opsXfd007ConcurrentDisjointCapabilities", "opsXfd008RealExecInheritsSameFlockUntilProcessExit")))
        groups.append(("dev.codex.schubert.nk.storage.LinuxSealedProofTest", 1, ("opsSeal001LiteralBytesFlagsOrderAndScopedClose", "opsSeal002AllCreationSyscallFailuresAndCleanup", "opsSeal003ReadSealEmptyOversizeAndNativeErrors", "opsSeal004BoundaryAndPartialIoIndependentVector", "opsSeal005NullAndPlatformContracts", "opsSeal006UnknownCompoundAndAllOwnedClose", "opsSeal007RealMemfdModeSealsAndMutationRefusal", "opsSeal008NativeConcurrentProofsNeverMix")))
        groups.append(("dev.codex.schubert.nk.storage.LinuxHostDirectoryCallsTest", 1, ("opsHost001FixedKernelAnchorAndNativeFlags", "opsHost002NoFollowChildrenAndOwnedCloseForwardOnly", "opsHost003EveryMutationRefusedWithoutDelegation", "opsHost004UidGateAndNativeFailureNeverFallBack", "opsHost005UnknownFailuresKeepIdentityAndArenaClosed", "opsHost006NullPlatformAndSymbolContracts", "opsHost007ActualOrdinaryUidCannotOpenHostAnchor", "opsHost008ConcurrentScopesKeepOnlyOwnPointers")))
        groups.append(("dev.codex.schubert.nk.storage.LinuxStartupAdmissionTest", 1, ("childfd001RootSealsImmediateCloexecAndEarlyProofClose", "childfd002EveryDescriptorInputAndNullContractBeforeOwnership", "childfd003BothFdInitialFlagsAllSyscallsAndReadonlyAccess", "childfd004EveryTypedAttributeRootModeLinkSizeAndUnsignedIdentity", "childfd005PayloadNullSizeIoAndProofCloseBeforeCallback", "childfd006UnknownAndCompoundFailurePriorityAndOneClose", "childfd007ConcurrentReadyAndOuterCleanupConsumeAExactlyOnce", "childfd008NativeFactoryBindingsAndOrdinaryUidCannotForgeRootMetadata")))
        groups.append(("dev.codex.schubert.nk.batch.file.StartupAdmissionFileTest", 1, ("admissionLock001TwoViewsSameOfdAndReadonlyPrivate", "admissionLock002ContentionAndCrossViewMismatch", "admissionLock003EveryTypedMetadataAndBoundaryRejected", "admissionLock004PhysicalSymlinkReplacementAndNoRepair", "admissionLock005AllIoAndCloseFaultsReleaseEveryOwner", "admissionLock006CompoundUnknownCleanupIsNeverDowngraded", "admissionLock007ConcurrentSingleWinnerAndReusableAfterRelease", "admissionLock008FactoryNullAndActualNioContracts")))
        groups.append(("dev.codex.schubert.nk.batch.platform.RootStartupContextTest", 1, ("rootctx001LiteralContextAndTwoObservations", "rootctx002RootProcInitBootAndInvocationDomains", "rootctx003StatStartBoundaryAndPidNamespaceBinding", "rootctx004EveryManagerPropertyAndCgroupRefused", "rootctx005AsciiBoundsNullAndObservationDrift", "rootctx006FixedSystemBusQueryAndAllProcessResults", "rootctx007NativeStreamsFaultsAndUnknownPriority", "rootctx008NativeKernelReadsAndOrdinaryUidRefusal")))
        groups.append(("dev.codex.schubert.nk.bootstrap.StartupProofFrameTest", 1, ("proof001IndependentGoldenAndExplicitFieldOrdering", "proof002EveryMissingExtraDuplicateAndNoncanonicalRow", "proof003AsciiByteSizeAndEveryNullContract", "proof004NumericLowerUpperOverflowAndCanonicalDecimals", "proof005StrictSortedGroupsAndInvalidGroupBoundary", "proof006ServiceBootEpochInvocationAndDigestDomains", "proof007ImmutableInputSnapshotAndByteOwnership", "proof008ConcurrentIndependentImmutableFrames")))
        groups.append(("dev.codex.schubert.nk.bootstrap.FixedServiceIdentityTest", 1, ("serviceid001BothFixedAccountsExplicitRequiredGroups", "serviceid002EveryFixedRowMalformedMissingAliasAndShadowMarker", "serviceid003UidGidBoundariesAndCanonicalDecimal", "serviceid004PrimaryMismatchDuplicateGroupsAndImplicitMembershipIgnored", "serviceid005ByteNullAndImmutableValueInvariant", "serviceid006NativeQueryTimeoutExitInterruptAndNoInheritedSecrets", "serviceid007EveryOwnedCloseAndUnknownFailurePreserved", "serviceid008ConcurrentLiteralVectorsAndNativeUnprovisionedRejection")))
        groups.append(("dev.codex.schubert.nk.bootstrap.ChildStartupContextTest", 1, ("childctx001IndependentGoldenBindingsAndBothUnits", "childctx002EnvironmentMissingAliasNullAndDescriptorBounds", "childctx003EveryAttestedFieldAndNativeIdentityMismatch", "childctx004KernelBoundariesCapabilitiesAndImmutableSnapshots", "childctx005MalformedKernelStatBootPidAndByteInputs", "childctx006EveryStatusMissingDuplicateBoundsAndMalformedValue", "childctx007NullUnknownFailureAndConcurrency", "childctx008NativeProcOnlyDoesNotGrantAuthority")))
        groups.append(("dev.codex.schubert.nk.batch.platform.BackupArchiveProcessTest", 1, ("fixedCommandAndEnvironment", "inputAndNullContracts", "statusDeadlineAndCancellation", "everyStreamFailureAndCompoundOwnership", "encryptedPipelineIsNotPlaintextArtifact", "actorGatesAndDatabaseListFailure", "concurrentIndependentScopes", "actualNativePublicTarAndBuilder")))
        groups.append(("dev.codex.schubert.nk.batch.file.BackupDatabaseCopyTest", 1, ("literalCreationErasureAndBorrowing", "boundaryAndNullContracts", "metadataSecurityAndNamespace", "everyIoPositionAndProgress", "callbackFailureAndRetainedCapability", "erasureAndNameBindings", "repeatedCollisionAndConcurrentRoots", "nativePrivateTmpfsPublicBytes")))
        groups.append(("dev.codex.schubert.nk.batch.platform.BackupWorkerRequestTest", 1, ("literalCanonicalAndIndependentDirectory", "dateAndMicroBoundaries", "everyNullAndValueInvariant", "missingExtraAndFixedFieldOrder", "asciiAndBoundedBytes", "uuidAndTimestampNoncanonical", "ownedByteMutationDoesNotMutateRecord", "concurrentIndependentConsumption")))
        groups.append(("dev.codex.schubert.nk.batch.platform.BackupUnitTerminationTest", 1, ("bterm001ColdAndPresentStableNamespace", "bterm002EveryPlacementByteAndField", "bterm003EveryMetadataAndFilesystemCondition", "bterm004MissingOnlyAtExactLeafAndDriftRefused", "bterm005AllAcquisitionIoUnknownAndCloseCompounds", "bterm006InterruptAndIndependentParallelInstances", "bterm007FixedQueryProjectionAndNioPort", "bterm008MorningContextAndNativeFactoryFailClosed")))
        groups.append(("dev.codex.schubert.nk.batch.file.RootBatchCredentialReaderTest", 1, ("literalUtf8AndOwnedBuffers", "nullAndFixedName", "everyMetadataAndPolicyBoundary", "allIoAndUnknownPositionsCloseExactlyOnce", "progressSizeAndIndependentCodecNegatives", "mutationAndInterruption", "sharedOwnerConcurrentIndependentMaterial", "nativePortPublicFileOnlyAndWrongActor")))
        groups.append(("dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest", 1, ("fixedUrlRootConstructorAndNullContracts", "literalAdmissionAndSessionLifetime", "roleRecoveryNullAndLockRejections", "allAdmissionResourceFailuresAndUnknownIdentity", "compoundUnknownAndNullMethodBoundaries", "interruptionAndForeignThreadCannotUseBorrowedSession", "actualBothBackupBeginsAreCommittedTogether", "actualCommitAmbiguityNeverReturnsHandles")))
        groups.append(("dev.codex.schubert.nk.batch.file.BackupWorkerRequestFilesTest", 1, ("literalPublicationReadAndRetirement", "nullActorAndPrivateMetadata", "collisionMissingAndFixedNameOnly", "allIoPositionsAndProgress", "sourceCanonicalAndOriginalBinding", "unknownCompoundAndInterrupt", "parallelBorrowedScopesAndNoRepair", "namespaceReadAndRetireUncertainty")))
        groups.append(("dev.codex.schubert.nk.batch.file.BackupDatabaseWorkerTest", 1, ("literalRequestDumpAndFullClose", "selfAndUnitAdmissionBeforePrivateIo", "nullBoundariesAndSecretOwnerBeforeAcquisition", "rootMetadataAndOutputBinding", "everyAcquisitionIoAndUnknownFailureCloses", "postconditionsAndCompoundCloseFailure", "newOnlyReplayAndIndependentParallelJobs", "fixedNativeEntryRefusalAndRedactedDiagnostic")))
        groups.append(("dev.codex.schubert.nk.api.file.BackupRequestCredentialLoaderTest", 1, ("literalAndOwnedCopy", "boundedSource", "fixedNameMissingAndNoFallback", "everyIoFailureClears", "namespaceAndSecurityFailures", "symlinkAndHardLinkRefused", "closeFailureAndNullContracts", "independentConcurrentCopies")))
        groups.append(("dev.codex.schubert.nk.api.file.BackupCredentialLoaderTest", 1, ("literalAndOwnedCopy", "boundedSource", "fixedNameMissingAndNoFallback", "everyIoFailureClears", "namespaceAndSecurityFailures", "symlinkAndHardLinkRefused", "closeFailureAndNullContracts", "independentConcurrentCopies")))
        groups.append(("dev.codex.schubert.nk.batch.file.StartupPermitFilesTest", 1, ("originalsAndPublicationOrder", "missingCorruptAndWrongBindings", "metadataAndSecurityMatrix", "everyOwnedIoFaultAndUncertainPublication", "inodeChangesAndNoRepair", "interruptionNullAndUnknownIdentity", "concurrentSinglePublication", "nativeIoAndBorrowedLifetime")))
        groups.append(("dev.codex.schubert.nk.batch.file.StartupPermitRecordsTest", 1, ("literalRecords", "syntaxFailures", "identityAndHashFailures", "stateTransitions", "issuedBinding", "cutoffContract", "nullAndOwnership", "concurrentSnapshots")))
        groups.append(("dev.codex.schubert.nk.bootstrap.StartupReleaseManifestTest", 1, ("release001ActualBytesFixedGoldenAndNoExportedOwner", "release002SelectorCanonicalBoundariesAndNonfollowTargets", "release003EveryTypedAttributeOwnerModeLinkAndAclRejection", "release004NamespaceAndMetadataChangesAtEveryRecheck", "release005ReadLengthEofBoundaryAndIoFailures", "release006EveryAcquisitionCloseFailureAndUnknownPriority", "release007NullInvariantUnsignedMetadataAndConcurrency", "release008NativeReaderDoesNotBypassOwnershipGate")))
        groups.append(("dev.codex.schubert.nk.bootstrap.ServiceStartupAdmissionTest", 1, ("startadmit001MandatoryOrderBeforeBusinessAndReady", "startadmit002MissingInvalidAndUntrustedDescriptorsHaveFactoryZero", "startadmit003MalformedRootProofIsRedactedAndNeverObservesBusiness", "startadmit004IndependentBindingsAndChangedKernelRefuseFactory", "startadmit005EveryObservationFailureAndUnknownIdentity", "startadmit006BusinessFailureCleansBeforeFinalAAndCloseNotSuccess", "startadmit007NullConstructorHashAndDescriptorNames", "startadmit008ConcurrentScopesAndNativeFailureNoBusiness")))
        groups.append(("dev.codex.schubert.nk.api.maintenance.SchemaHistoryAdmissionTest", 1, ("opsSchema001ExactFixedQueryAndBorrowedOwner", "opsSchema002EveryColumnMissingExtraAndFailedRow", "opsSchema003ExpectedRowInvariantBoundaries", "opsSchema004ExpectedProfileOrderingAndDefensiveCopy", "opsSchema005NullProviderSqlExceptionsAndAllOwnership", "opsSchema006KnownUnknownCloseMatrixAndSameThrowable", "opsSchema007InterruptBeforeAndAfterNeverAccepts", "opsSchema008IndependentConcurrentOwners")))
        groups.append(("dev.codex.schubert.nk.bootstrap.ReleaseApprovalTest", 1, ("approval001IndependentLiteral", "approval002VersionBoundaries", "approval003NullAndDigestContracts", "approval004ByteBoundsAndNonAscii", "approval005CanonicalOrderAndKeys", "approval006DefensiveCopies", "approval007ParallelOwners", "approval008HeaderAndFixedProfile")))
        groups.append(("dev.codex.schubert.nk.batch.file.RootReleaseApprovalReaderTest", 1, ("approvalRead001FixedLiteralAndClosedOwners", "approvalRead002NullAndNoFallback", "approvalRead003AllMetadataContracts", "approvalRead004EveryIoFaultAndCompoundIdentity", "approvalRead005ReadProgressAndCanonicalMaterial", "approvalRead006NamespaceAndHeldInodeChanges", "approvalRead007InterruptRootAndParallel", "approvalRead008NativePortAndRealContextRefusal")))
        groups.append(("dev.codex.schubert.nk.bootstrap.ReleaseSignatureVerifierTest", 1, ("sign001IndependentRfcVectors", "sign002MessageSignatureAndWrongKey", "sign003DerAndNullContracts", "sign004MaterialBoundaries", "sign005SnapshotAndErasedOwnedBuffers", "sign006KnownCryptoFailureIsRedacted", "sign007UnknownFailureIdentityAndErasure", "sign008ConcurrentNativeProviderAndMalformedPoint")))
        groups.append(("dev.codex.schubert.nk.bootstrap.ReleaseInventoryTest", 1, ("bomProfile001IndependentLiteralClaims", "bomProfile002FixedKeysTypesAndOrder", "bomProfile003ByteUtf8AndDocumentBounds", "bomProfile004StrictNumbersAndBoundaryValues", "bomProfile005ArtifactLexicalAndNullContracts", "bomProfile006DependencyContractsAndCopies", "bomProfile007RequiredPayloadAndOrdering", "bomProfile008ManagementSelfHashAndAncestorConflicts", "bomProfile009RegisteredLibCompleteSetAndCommonBytes", "bomProfile010SharedVersionsAndRequiredRoles", "bomProfile011SqlNamesRanksAndSchemaVersion", "bomProfile012IntegerNullableAndColumnContracts", "bomProfile013DefensiveInputAndCollections", "bomProfile014CollectionCapsAndExactPositiveBoundaries", "bomProfile015AllMetadataScalarContracts", "bomProfile016IndependentConcurrentParsers")))
        groups.append(("dev.codex.schubert.nk.bootstrap.ReleasePayloadVerificationTest", 1, ("fullBom001IndependentLiteralAndAllOwners", "fullBom002ByteInventoryAndNullContracts", "fullBom003ReadonlyAndNamespace", "fullBom004AcquisitionNullAndIo", "fullBom005IndependentSqlVectorsAndEmbeddedAgreement", "fullBom006ThinLayoutAndSharedShadow", "fullBom007IndependentConcurrentScopes", "fullBom008EveryRetainedOwnerAndUntrustedDigest")))
        groups.append(("dev.codex.schubert.nk.batch.platform.RootReleaseAdmissionTest", 1, ("rootBom001ClosedLoaderAndFreshBeforeEverySchema", "rootBom002NoPublicClaimsOrBooleanAuthority", "rootBom003EveryMetadataAndNullField", "rootBom004CloseOrChangedRootCannotMint", "rootBom005ActorAndSchemaFailureBeforeBegin", "rootBom006CurrentReloadAndInterruption", "rootBom007FixedOsVectors", "rootBom008IndependentConcurrentOwners")))
        groups[60:60] = [
            ("dev.codex.schubert.nk.batch.platform.MaintenanceStopSnapshotTest", 1, ("mstop001FixedNamesAndIndependentTerminalVectors", "mstop002MissingDuplicateUnknownAndSeparators", "mstop003ByteBoundsNullAndOriginalOwnership", "mstop004FixedPlacementAndNonTerminalStates", "mstop005InvocationAndUnsignedTimestampDomains", "mstop006AbaAndAllFieldChangesStayUnmatched", "mstop007IndependentParallelAndNoAmbientAuthorization")),
            ("dev.codex.schubert.nk.batch.platform.MaintenanceUnitTerminationTest", 1, ("mterm001AllFixedColdAndPresentLeaves", "mterm002UnboundBusyAndNestedProcessRefused", "mterm003AbaCurrentNamespaceAndWrongActor", "mterm004EveryIoUnknownAndClosePosition", "mterm005NullContractsAndAllOwnedMaterials", "mterm006InterruptAndIndependentParallel", "mterm007NativeFixedQueriesAndMaterials", "mterm008NativeFactoryAndOrdinaryHostRefusal")),
            ("dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopPolicyTest", 1, ("mpol001AllEightFixedPolicyAndOrderIndependent", "mpol002MissingDuplicateUnknownAndLineStructure", "mpol003ByteAndNullBounds", "mpol004WrongIdLoadKillAndAutomaticSigkillRefused", "mpol005FixedNativeQueryAndAllProcessOwners", "mpol006KnownUnknownNullAndInterrupts", "mpol007IndependentParallelAndNoStopAuthority")),
            ("dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopClientTest", 1, ("mclient001FixedEightNamesPolicyBeforeExactCommand", "mclient002PolicyAndRootRefusalIssueNoClient", "mclient003ClientNonzeroAndOwnerCloseNeverSucceeds", "mclient004TimeoutRetainsLiveProcessAndReapsSameOwner", "mclient005EveryCloseGetterAndUnknownFailurePoisoned", "mclient006StartAndPostContextUnknownAreNotStopSuccess", "mclient007InterruptionKeepsOwnerWithoutAutomaticKill", "mclient008FactoryNullActorAndHarmlessNativeProcessPort")),
            ("dev.codex.schubert.nk.batch.platform.ArtemisServiceUnitTest", 1, ("artunit001RealFixedDependencyIdentityAndInstance", "artunit002PrivateHashedCredentialIsFixedReadOnlyMount", "artunit003ExactStopAndResourceLimits", "artunit004HardeningAndNoHostSecretMutation")),
        ]
        self.assertEqual(groups, list(launch.DEPLOYMENT_GROUPS))
        for cls, _, _ in groups:
            expected_module = bootstrap_ownership.owner(cls, test=True)
            self.assertIn(expected_module, ("api", "web", "batch", "storage", "bootstrap"))
            self.assertEqual(expected_module, launch.module_for(cls))
        for cls in ("dev.codex.schubert.nk.web.bootstrap.WebJdbcPoolTest",
                    "dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfigTest"):
            self.assertEqual("web", launch.module_for(cls))
        with self.assertRaises(ValueError):
            launch.module_for("dev.codex.schubert.nk.unknown.FutureTest")
        self.check_launch_inventory(groups, True)

    def check_launch_inventory(self, groups, deployment):
        suites, expected = [], {}
        for cls, start, names in groups:
            prefix = ({"dev.codex.schubert.nk.storage.ResourceScopeTest": "PT-OPS-RSCOPE",
                       "dev.codex.schubert.nk.storage.LinuxFileLockTest": "PT-OPS-FLOCK",
                       "dev.codex.schubert.nk.storage.LinuxProcessExecTest": "PT-OPS-EXEC",
                       "dev.codex.schubert.nk.storage.LinuxExecDescriptorsTest": "PT-OPS-XFD",
                       "dev.codex.schubert.nk.storage.LinuxSealedProofTest": "PT-OPS-SEAL",
                       "dev.codex.schubert.nk.storage.LinuxHostDirectoryCallsTest": "PT-OPS-HOST",
                       "dev.codex.schubert.nk.storage.LinuxStartupAdmissionTest": "PT-OPS-CHILDFD",
                       "dev.codex.schubert.nk.batch.file.StartupAdmissionFileTest": "PT-OPS-ADMISSIONLOCK",
                       "dev.codex.schubert.nk.batch.platform.RootStartupContextTest": "PT-OPS-ROOTCTX",
                       "dev.codex.schubert.nk.bootstrap.StartupProofFrameTest": "PT-OPS-PROOF",
                       "dev.codex.schubert.nk.bootstrap.FixedServiceIdentityTest": "PT-OPS-SERVICEID",
                       "dev.codex.schubert.nk.bootstrap.ChildStartupContextTest": "PT-OPS-CHILDCTX",
                       "dev.codex.schubert.nk.batch.file.StartupPermitRecordsTest": "PT-OPS-PERMITREC",
                       "dev.codex.schubert.nk.batch.file.StartupPermitFilesTest": "PT-OPS-PERMITFILE",
                       "dev.codex.schubert.nk.batch.platform.BackupArchiveProcessTest": "PT-OPS-ARCHPROC",
                       "dev.codex.schubert.nk.batch.file.BackupDatabaseCopyTest": "PT-OPS-DBCP",
                       "dev.codex.schubert.nk.batch.platform.BackupWorkerRequestTest": "PT-OPS-BREQ",
                       "dev.codex.schubert.nk.batch.platform.BackupUnitTerminationTest": "PT-OPS-BTERM",
                       "dev.codex.schubert.nk.batch.platform.MaintenanceStopSnapshotTest": "PT-OPS-MSTOP",
                       "dev.codex.schubert.nk.batch.platform.MaintenanceUnitTerminationTest": "PT-OPS-MTERM",
                       "dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopPolicyTest": "PT-OPS-MPOL",
                       "dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopClientTest": "PT-OPS-MCLIENT",
                       "dev.codex.schubert.nk.batch.platform.ArtemisServiceUnitTest": "PT-OPS-ARTUNIT",
                       "dev.codex.schubert.nk.batch.file.RootBatchCredentialReaderTest": "PT-OPS-RBCR",
                       "dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest": "PT-OPS-MDB",
                       "dev.codex.schubert.nk.batch.file.BackupWorkerRequestFilesTest": "PT-OPS-BREQFILE",
                       "dev.codex.schubert.nk.batch.file.BackupDatabaseWorkerTest": "PT-OPS-BWORK",
                       "dev.codex.schubert.nk.api.file.BackupRequestCredentialLoaderTest": "PT-OPS-BREQUESTCRED",
                       "dev.codex.schubert.nk.api.file.BackupCredentialLoaderTest": "PT-OPS-BACKCRED",
                       "dev.codex.schubert.nk.bootstrap.StartupReleaseManifestTest": "PT-OPS-RELEASE",
                       "dev.codex.schubert.nk.bootstrap.ServiceStartupAdmissionTest": "PT-OPS-STARTADMIT",
                       "dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest": "PT-OPS-LOCK",
                       "dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest": "PT-OPS-STOP",
                       "dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest": "PT-OPS-STOP",
                       "dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest": "PT-OPS-ENV",
                       "dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest": "PT-OPS-CFG",
                       "dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest": "PT-OPS-EFILE",
                       "dev.codex.schubert.nk.storage.PrivateDirectoryEntryTest": "PT-OPS-PFILE",
                       "dev.codex.schubert.nk.storage.ChildDirectoryPublicationTest": "PT-OPS-PDIR",
                       "dev.codex.schubert.nk.storage.PrivateChildDirectoryTest": "PT-OPS-CDIR",
                       "dev.codex.schubert.nk.api.database.PostgresDeploymentTest": "PT-OPS-PGCFG",
                       "dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest": "PT-OPS-PUB",
                       "dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest": "PT-OPS-GID",
                       "dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest": "PT-OPS-NS",
                       "dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest": "PT-OPS-UNIT",
                       "dev.codex.schubert.nk.batch.platform.InspectorUnitProbeTest": "PT-OPS-UNIT",
                       "dev.codex.schubert.nk.batch.mq.ArtemisReadinessClientTest": "PT-OPS-MQ",
                       "dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessClientTest": "PT-OPS-MQ",
                       "dev.codex.schubert.nk.batch.mq.ArtemisAddressSettingsReadinessClientTest": "PT-OPS-MQ",
                       "dev.codex.schubert.nk.batch.mq.ArtemisAcceptorReadinessClientTest": "PT-OPS-MQ",
                       "dev.codex.schubert.nk.batch.mq.ArtemisRoleReadinessClientTest": "PT-OPS-MQ",
                       "dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClientTest": "PT-OPS-MQ",
                       "dev.codex.schubert.nk.batch.mq.ArtemisExpiryManagementAuthorizationTest": "PT-OPS-MQ",
                       "dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeClientTest": "PT-OPS-MQ",
                       "dev.codex.schubert.nk.batch.mq.ArtemisStartupObservationTest": "PT-OPS-MQ",
                       "dev.codex.schubert.nk.api.maintenance.ApplicationServiceUnitTest": "PT-OPS-SVC",
                       "dev.codex.schubert.nk.api.bootstrap.ApiJdbcPoolTest": "PT-OPS-DBPOOL",
                       "dev.codex.schubert.nk.web.bootstrap.WebJdbcPoolTest": "PT-OPS-DBPOOL",
                       "dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest": "PT-OPS-API-CFG",
                       "dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfigTest": "PT-OPS-WEB-CFG",
                       "dev.codex.schubert.nk.storage.ServiceConfigFilesTest": "PT-OPS-CFGFILE",
                       "dev.codex.schubert.nk.storage.ServiceCredentialLocationTest": "PT-OPS-CREDLOC",
                       "dev.codex.schubert.nk.storage.ServiceCredentialIdTest": "PT-OPS-CREDID",
                       "dev.codex.schubert.nk.api.bootstrap.ApiConfigurationLoaderTest": "PT-OPS-API-LOAD",
                       "dev.codex.schubert.nk.web.bootstrap.WebConfigurationLoaderTest": "PT-OPS-WEB-LOAD",
                       "dev.codex.schubert.nk.api.bootstrap.ApiStartupInputsTest": "PT-OPS-API-INPUT",
                       "dev.codex.schubert.nk.web.bootstrap.WebStartupInputsTest": "PT-OPS-WEB-INPUT",
                       "dev.codex.schubert.nk.api.file.ServiceCredentialReaderTest": "PT-OPS-CREDREAD",
                       "dev.codex.schubert.nk.api.maintenance.ServiceDatabaseAdmissionTest": "PT-OPS-DBADMIT",
                       "dev.codex.schubert.nk.api.maintenance.SchemaHistoryAdmissionTest": "PT-OPS-SCHEMA",
                       "dev.codex.schubert.nk.bootstrap.ReleaseApprovalTest": "PT-OPS-APPROVAL",
                       "dev.codex.schubert.nk.batch.file.RootReleaseApprovalReaderTest": "PT-OPS-APPROVALREAD",
                       "dev.codex.schubert.nk.bootstrap.ReleaseSignatureVerifierTest": "PT-OPS-SIGN",
                       "dev.codex.schubert.nk.bootstrap.ReleaseInventoryTest": "PT-OPS-BOMPROFILE",
                       "dev.codex.schubert.nk.bootstrap.ReleasePayloadVerificationTest": "PT-OPS-FULLBOM",
                       "dev.codex.schubert.nk.batch.platform.RootReleaseAdmissionTest": "PT-OPS-ROOTBOM",
                       "dev.codex.schubert.nk.api.file.ServiceCredentialSetTest": "PT-OPS-CREDSET",
                       "dev.codex.schubert.nk.api.bootstrap.ApiProcessMainTest": "PT-OPS-API-MAIN",
                       "dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSourceTest": "PT-OPS-DBSOURCE",
                       "dev.codex.schubert.nk.api.file.ServiceProcessResourcesTest": "PT-OPS-API-RES",
                       "dev.codex.schubert.nk.web.bootstrap.WebProcessMainTest": "PT-OPS-WEB-MAIN"}.get(cls, "PT-OPS-INBOX")
                      if deployment else "PT-DB-INBOX")
            suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
            for i, name in enumerate(names, start):
                ET.SubElement(suite, "testcase", classname=cls, name=name)
                expected[("PT-OPS-WEB-RES-001" if name == "opsWebRes001WebOnlyFiveMaterialsTechnicalRoleAndTwoConnectionCeiling" else f"{prefix}-{i:03}")] = cls + "#" + name
            suites.append(suite)
        self.assertEqual(expected, launch.validate_reports(suites, deployment))
        with self.assertRaises(ValueError): launch.validate_reports(suites, not deployment)
        for index, suite in enumerate(suites):
            for position in range(len(suite)):
                wrong = copy.deepcopy(suites); wrong[index].remove(wrong[index][position])
                with self.assertRaises(ValueError): launch.validate_reports(wrong, deployment)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suites); ET.SubElement(wrong[index][0], tag)
                with self.assertRaises(ValueError): launch.validate_reports(wrong, deployment)
            for key, value in (("tests", "0"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suites); wrong[index].set(key, value)
                with self.assertRaises(ValueError): launch.validate_reports(wrong, deployment)
            substitutions = [("classname", "unknown"), ("name", "unknown")]
            if len(suite) > 1:
                substitutions.append(("name", suite[1].get("name")))
            for key, value in substitutions:
                wrong = copy.deepcopy(suites); wrong[index][0].set(key, value)
                with self.assertRaises(ValueError): launch.validate_reports(wrong, deployment)
        for wrong in ([], suites[:-1], suites + [suites[0]]):
            with self.assertRaises(ValueError): launch.validate_reports(wrong, deployment)

    def test_application_inventory_and_nonpassing_cases(self):
        prefix = "dev.codex.schubert.nk.api."
        groups = [
            (prefix + "maintenance.InspectorSettingsTest", 209,
             ("validSnapshot", "invalidSettings", "sharedValidation")),
            (prefix + "file.InspectorApplicationTest", 212,
             ("successAndResume", "protectedResult", "databaseFailure", "credentialFailures", "rootFailures",
              "nativeAdmission", "nullContracts", "interruptedExecution", "concurrentLifetimes"))]
        self.assertEqual(groups, list(database.APPLICATION_GROUPS))
        suites = []
        expected = {}
        for cls, start, names in groups:
            suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
            for i, name in enumerate(names, start):
                ET.SubElement(suite, "testcase", classname=cls, name=name)
                expected[f"PT-DB-INBOX-{i:03}"] = cls + "#" + name
            suites.append(suite)
        self.assertEqual(expected, database.validate_reports(suites, True))
        with self.assertRaises(ValueError): database.validate_reports(suites)
        for index, suite in enumerate(suites):
            for position in range(len(suite)):
                wrong = copy.deepcopy(suites); wrong[index].remove(wrong[index][position])
                with self.assertRaises(ValueError): database.validate_reports(wrong, True)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
                wrong = copy.deepcopy(suites); ET.SubElement(wrong[index][0], tag)
                with self.assertRaises(ValueError): database.validate_reports(wrong, True)
            for key, value in (("tests", "0"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suites); wrong[index].set(key, value)
                with self.assertRaises(ValueError): database.validate_reports(wrong, True)
            for key, value in (("classname", "unknown"), ("name", "unknown"), ("name", suite[1].get("name"))):
                wrong = copy.deepcopy(suites); wrong[index][0].set(key, value)
                with self.assertRaises(ValueError): database.validate_reports(wrong, True)
        for wrong in ([], suites[:-1], suites + [suites[0]], [suites[0]] * 2):
            with self.assertRaises(ValueError): database.validate_reports(wrong, True)

    def test_database_credential_inventory_and_nonpassing_cases(self):
        prefix = "dev.codex.schubert.nk.api."
        groups = [
            (prefix + "maintenance.InspectorDbCredentialTest", 193,
             ("validUtf8AndNewlines", "invalidEncodingAndBounds", "ownedCopiesAndClose", "concurrentOwnership")),
            (prefix + "file.InspectorDatabaseCredentialLoaderTest", 197,
             ("validBoundedFile", "missingAndInvalidContent", "permissionsAndMetadata", "ioFailuresAndCleanup", "concurrentFilesAndAesRegression")),
            (prefix + "maintenance.InspectorDatabaseConnectionsTest", 202,
             ("fixedConnectionProperties", "urlAndNullContracts", "connectionAdmission", "sqlFailuresRemainRedacted",
              "closeAndConcurrentOpen", "realScramRoleAndPassword", "ownedInspectionConnection"))]
        self.assertEqual(groups, list(database.GROUPS))
        suites = []
        expected = {}
        for cls, start, names in groups:
            suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
            for i, name in enumerate(names, start):
                ET.SubElement(suite, "testcase", classname=cls, name=name)
                expected[f"PT-DB-INBOX-{i:03}"] = cls + "#" + name
            suites.append(suite)
        self.assertEqual(expected, database.validate_reports(suites))
        for index, suite in enumerate(suites):
            for position in range(len(suite)):
                wrong = copy.deepcopy(suites); wrong[index].remove(wrong[index][position])
                with self.assertRaises(ValueError): database.validate_reports(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
                wrong = copy.deepcopy(suites); ET.SubElement(wrong[index][0], tag)
                with self.assertRaises(ValueError): database.validate_reports(wrong)
            for key, value in (("tests", "0"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suites); wrong[index].set(key, value)
                with self.assertRaises(ValueError): database.validate_reports(wrong)
            for key, value in (("classname", "unknown"), ("name", "unknown"), ("name", suite[1].get("name"))):
                wrong = copy.deepcopy(suites); wrong[index][0].set(key, value)
                with self.assertRaises(ValueError): database.validate_reports(wrong)
        for wrong in ([], suites[:-1], suites + [suites[0]], [suites[0]] * 3):
            with self.assertRaises(ValueError): database.validate_reports(wrong)

    def test_mutation_inventory_rejects_nonpassing_cases(self):
        cls = "dev.codex.schubert.nk.api.maintenance.QuestionMutationInboxInspectorTest"
        names = ["validMutationReferences", "submitReferencesAndWork", "cancellationHistory",
                 "deletionHistoryAndAnswers", "exactStoredProfiles", "wireAndMetadataDamage",
                 "nullAndJdbcFailures", "equalTimeTargetsRemainDistinct", "leastPrivilegeCatalog",
                 "uniqueWorkProjection", "referencesAndPhantomsStayLocked", "canonicalRoutesAndRetention",
                 "ownedAtomicFailures", "durableMixedResume", "concurrentReferencesStayIndependent", "appendOnlyInventory"]
        self.assertEqual(cls, inspection.MUTATION_CLASS)
        self.assertEqual(names, inspection.MUTATION_METHODS)
        suite = ET.Element("testsuite", name=cls, tests="16", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual(16, len(inspection.validate_suite(suite, cls, names)))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite)
            wrong.remove(wrong[position])
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for kind in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite)
            ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for key, value in (("tests", "15"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite)
            wrong.set(key, value)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for key, value in (("classname", "Wrong"), ("name", "unknown"), ("name", names[1])):
            wrong = copy.deepcopy(suite)
            wrong[0].set(key, value)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)

    def test_result_binding_inventory_rejects_nonpassing_cases(self):
        cls = "dev.codex.schubert.nk.api.maintenance.ResultBoundResponseSnapshotCodecTest"
        names = ["independentWriteAndReadAllRoutes", "nullIdentityAndReferenceContracts",
                 "everyMetadataByteIsAuthenticated", "exactLengthAndLegacyRejection",
                 "keysAadAndCipherDamage", "borrowedOwnershipAndRedaction",
                 "concurrentBindingsNeverCross", "equalBusinessTimesDoNotAuthorizeAnotherTarget"]
        self.assertEqual(cls, inspection.BINDING_CLASS)
        self.assertEqual(names, inspection.BINDING_METHODS)
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual(8, len(inspection.validate_suite(suite, cls, names)))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite)
            wrong.remove(wrong[position])
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for kind in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite)
            ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for key, value in (("tests", "7"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite)
            wrong.set(key, value)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for key, value in (("classname", "Wrong"), ("name", "unknown"), ("name", names[1])):
            wrong = copy.deepcopy(suite)
            wrong[0].set(key, value)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)

    def test_question_query_inventory_rejects_nonpassing_cases(self):
        cls = "dev.codex.schubert.nk.api.maintenance.QuestionQueryInboxCleanupTest"
        names = ["queryProfilesAndFrozenSnapshots", "goldenBoundsAndSemanticDamage",
                 "canonicalIdentityReferencesAndNulls", "validRowsDeleteAndRetainExactMetadata",
                 "retentionBackupAndSqlAuthority", "failuresRollbackAndResume",
                 "concurrentAndDurableMixedRuns", "appendOnlyInventoryAndClosedRoutes"]
        self.assertEqual(cls, inspection.QUESTION_CLASS)
        self.assertEqual(names, inspection.QUESTION_METHODS)
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual(8, len(inspection.validate_suite(suite, cls, names)))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite)
            wrong.remove(wrong[position])
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for kind in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite)
            ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for key, value in (("tests", "7"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite)
            wrong.set(key, value)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for key, value in (("classname", "Wrong"), ("name", "unknown"), ("name", names[1])):
            wrong = copy.deepcopy(suite)
            wrong[0].set(key, value)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)

    def test_log_service_class_and_pt_ids_are_mandatory(self):
        cls = "dev.codex.schubert.nk.batch.cleanup.LogCleanupServiceTest"
        names = ["emptyAndCompletedRuns", "heldPrefixAndLargeChunks", "resumedAttemptCounts", "sessionLockOwnership",
                 "backupAndRowLockStop", "timeBoundaryAndClockWrap", "interruptsRemainSet", "rollbackAndUncertainCommit",
                 "restorationAndUnlockFailures", "invalidInputsAndProjections", "summaryInvariants", "failuresLeaveNoFalseSuccess"]
        suite = ET.Element("testsuite", name=cls, tests="12", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        expected = {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 18)}
        self.assertEqual(expected, batch.validate_log_suite(suite))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite)
            wrong.remove(wrong[position])
            with self.assertRaises(ValueError):
                batch.validate_log_suite(wrong)
        for kind in ("failure", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite)
            ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError):
                batch.validate_log_suite(wrong)
        # Repository method ownership is independently checked by the next test.
        repository = ET.Element("testsuite", name=batch.CLASS, tests="17", failures="0", errors="0", skipped="0")
        for name in batch.METHODS:
            ET.SubElement(repository, "testcase", classname=batch.CLASS, name=name)
        handoff, expected_handoff = self.handoff_fixture()
        records, expected_records = self.record_fixture()
        durable, expected_durable = self.durable_fixture()
        lifecycle, expected_lifecycle = self.lifecycle_fixture()
        refs, expected_refs = self.references_fixture()
        retirement_records, expected_retirement_records = self.retirement_fixture(True)
        retirement, expected_retirement = self.retirement_fixture()
        summary, expected_summary = self.parent_fixture("repository")
        attempt, expected_attempt = self.parent_fixture("attempt")
        step_values, expected_step_values = self.step_fixture()
        step_repository, expected_step_repository = self.step_fixture(True)
        reports = [suite, repository, handoff, records, durable, lifecycle, refs, retirement_records, retirement, summary, attempt, step_values, step_repository] + [self.atomic_fixture(i)[0] for i in range(3)]
        reports += [self.backup_fixture(False)[0], self.backup_fixture(True)[0]]
        artifact, expected_artifact = self.artifact_fixture()
        reports.append(artifact)
        reports += [self.pair_fixture(False)[0], self.pair_fixture(True)[0]]
        reader, reader_expected = self.reader_fixture()
        reports.append(reader)
        publication, publication_expected = self.publication_fixture()
        reports.append(publication)
        bundle, bundle_expected = self.bundle_fixture()
        reports.append(bundle)
        completion, completion_expected = self.completion_fixture()
        reports.append(completion)
        runtime_cls = batch.BATCH_RUNTIME_DEPENDENCY_CLASS
        runtime_name = batch.BATCH_RUNTIME_DEPENDENCY_METHODS[0]
        runtime = ET.Element("testsuite", name=runtime_cls, tests="1", failures="0", errors="0", skipped="0")
        ET.SubElement(runtime, "testcase", classname=runtime_cls, name=runtime_name)
        reports.append(runtime)
        expiry = ET.Element("testsuite", name=batch.EXPIRY_AUDIT_CLASS, tests="4", failures="0", errors="0", skipped="0")
        for name in batch.EXPIRY_AUDIT_METHODS:
            ET.SubElement(expiry, "testcase", classname=batch.EXPIRY_AUDIT_CLASS, name=name)
        reports.append(expiry)
        accepted = batch.validate_reports(reports)
        self.assertEqual(completion_expected,{k:v for k,v in accepted.items() if k in completion_expected})
        self.assertEqual(bundle_expected,{k:v for k,v in accepted.items() if k in bundle_expected})
        self.assertEqual(publication_expected, {k: v for k,v in accepted.items() if k in publication_expected})
        self.assertEqual(reader_expected, {k: v for k, v in accepted.items() if k in reader_expected})
        self.assertEqual(287, len(accepted))
        batch_ops = sum(len(names) for cls, _, names in launch.DEPLOYMENT_GROUPS if ".nk.batch." in cls)
        self.assertEqual(263, batch_ops)  # PG321: genuine Artemis Unit contract adds four PT.
        self.assertEqual(batch.BATCH_TEST_COUNT, len(accepted) + batch_ops)
        for service in (False, True):
            _, pair_expected = self.pair_fixture(service)
            self.assertEqual(pair_expected, {k: v for k, v in accepted.items() if k in pair_expected})
        self.assertEqual(expected_artifact, {k: v for k, v in accepted.items() if k in expected_artifact})
        for codec in (False, True):
            _, backup_expected = self.backup_fixture(codec)
            self.assertEqual(backup_expected, {k: v for k, v in accepted.items() if k in backup_expected})
        for i in range(3):
            _, atomic_expected = self.atomic_fixture(i)
            self.assertEqual(atomic_expected, {k: v for k, v in accepted.items() if k in atomic_expected})
        self.assertEqual(expected_step_values, {k: v for k, v in accepted.items() if k in expected_step_values})
        self.assertEqual(expected_step_repository, {k: v for k, v in accepted.items() if k in expected_step_repository})
        self.assertEqual(expected_summary, {k: v for k, v in accepted.items() if k in expected_summary})
        self.assertEqual(expected_attempt, {k: v for k, v in accepted.items() if k in expected_attempt})
        self.assertEqual(expected_retirement_records, {k: v for k, v in accepted.items() if k in expected_retirement_records})
        self.assertEqual(expected_retirement, {k: v for k, v in accepted.items() if k in expected_retirement})
        self.assertEqual(expected_refs, {k: v for k, v in accepted.items() if k in expected_refs})
        self.assertEqual(expected_lifecycle, {k: v for k, v in accepted.items() if k in expected_lifecycle})
        self.assertEqual(expected_durable, {k: v for k, v in accepted.items() if k in expected_durable})
        self.assertEqual(expected_records, {k: v for k, v in accepted.items() if k in expected_records})
        self.assertEqual(expected_handoff, {k: v for k, v in accepted.items() if k in expected_handoff})
        self.assertEqual(expected, {k: v for k, v in accepted.items() if k in expected})
        for position in range(len(reports)):
            wrong = copy.deepcopy(reports); del wrong[position]
            with self.assertRaises(ValueError): batch.validate_reports(wrong)
            wrong = copy.deepcopy(reports); wrong[position].set("name", "unknown")
            with self.assertRaises(ValueError): batch.validate_reports(wrong)
            wrong = copy.deepcopy(reports); wrong[position] = copy.deepcopy(reports[(position + 1) % len(reports)])
            with self.assertRaises(ValueError): batch.validate_reports(wrong)
        for reports in ([], [suite], [repository], [suite, suite], [repository, repository], [suite, repository, suite]):
            with self.assertRaises(ValueError):
                batch.validate_reports(reports)

    def test_batch_inventory_rejects_unrun_and_changed_tests(self):
        names = ["runIdentityBoundaries", "countInvariants", "cleanupAllowlist", "rejectionAndProgressContracts",
                 "emptyCleanupAndExplicitTransaction", "heldLogsAndDurableRead", "rollbackSavepointAndResume",
                 "backupAndAdvisoryRejection", "exactLimitsAndNullInputs", "rowProjectionFailures",
                 "progressProjectionFailures", "jdbcFailuresRemainRedacted", "roleIsolationAndNoInboxBypass",
                 "timezoneAndCutoffIdentity", "lockedLogsDoNotAdvance", "retentionAndResourceOwnership",
                 "moduleDependencyBoundary"]
        cls = "dev.codex.schubert.nk.batch.repository.CleanupRepositoryTest"
        suite = ET.Element("testsuite", name=cls, tests="17", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 1)}, batch.validate_suite(suite))
        for key, value in (("name", "Wrong"), ("tests", "16"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite)
            wrong.set(key, value)
            with self.assertRaises(ValueError):
                batch.validate_suite(wrong)
        for kind in ("missing", "duplicate", "unknown", "wrong-class", "failure", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite)
            if kind == "missing":
                wrong.remove(wrong[0])
            elif kind == "duplicate":
                wrong.append(copy.deepcopy(wrong[0]))
            elif kind == "unknown":
                wrong[0].set("name", "newUnmappedTest")
            elif kind == "wrong-class":
                wrong[0].set("classname", "Other")
            else:
                ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError):
                batch.validate_suite(wrong)

    def test_collector_manifest_is_constructed_before_subscript_metadata_updates(self):
        def check(source):
            tree = ast.parse(source)
            main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
            allocations = [n.lineno for n in ast.walk(main) if isinstance(n, ast.Assign)
                           and any(isinstance(t, ast.Name) and t.id == "manifest" for t in n.targets)]
            accesses = [n.lineno for n in ast.walk(main) if isinstance(n, ast.Subscript)
                        and isinstance(n.value, ast.Name) and n.value.id == "manifest"]
            if not allocations or (accesses and min(accesses) < min(allocations)):
                raise ValueError("manifest metadata precedes construction")
        for name in ("006_collect_scenario_evidence.py", "016_collect_inbox_inspection_evidence.py",
                     "021_collect_inspector_database_evidence.py", "022_collect_inspector_launch_evidence.py"):
            check(Path(__file__).with_name(name).read_text())
        check("def main():\n    manifest = {}\n    manifest['owner'] = 'bootstrap'\n")
        with self.assertRaisesRegex(ValueError, "precedes"):
            check("def main():\n    manifest['owner'] = 'bootstrap'\n    manifest = {}\n")

    def test_bootstrap_artifact_ownership_is_explicit_and_has_no_duplicate_source(self):
        repo = Path(__file__).resolve().parents[2]
        expected_main = {
            "file.InspectorCredentialLoader", "file.ServiceCredentialReader", "file.ServiceCredentialSet",
            "file.ServiceCredentialException", "file.InspectorCredentialException", "file.AesCredentialFile",
            "maintenance.InspectorAesCredential", "maintenance.InspectorDbCredential",
            "maintenance.InspectorCredentialAccess", "bootstrap.ServiceDatabaseAdmission", "bootstrap.ServiceDatabaseSource", "bootstrap.SchemaHistoryAdmission", "bootstrap.JdbcAdmissionFailures", "file.ServiceProcessResources"}
        self.assertEqual({"dev.codex.schubert.nk.api." + s for s in expected_main}
                         | {"dev.codex.schubert.nk.bootstrap." + s for s in
                            ("StartupProofFrame", "FixedServiceIdentity", "ChildStartupContext", "StartupReleaseManifest", "ServiceStartupAdmission", "ReleaseApproval", "ReleaseSignatureVerifier", "ReleaseInventory", "ReleasePayloadVerification")},
                         set(bootstrap_ownership.BOOTSTRAP_MAIN))
        for name in bootstrap_ownership.BOOTSTRAP_MAIN:
            source = bootstrap_ownership.source(repo, name)
            self.assertTrue(source.is_file())
            self.assertEqual("bootstrap", bootstrap_ownership.owner(name.replace(".", "/") + "$Nested"))
            self.assertFalse((repo / "src/schubert-nk-api/src/main/java" / (name.replace(".", "/") + ".java")).exists())
        for name in bootstrap_ownership.BOOTSTRAP_TEST:
            self.assertTrue(bootstrap_ownership.source(repo, name, test=True).is_file())
            self.assertEqual("bootstrap", launch.module_for(name))
        for name, expected in (("api.file.ServiceProcessResources", "bootstrap"), ("api.bootstrap.ApiProcessMain", "api"),
                               ("web.bootstrap.WebProcessMain", "web"), ("storage.ServiceConfigFiles", "storage")):
            self.assertEqual(expected, bootstrap_ownership.owner("dev.codex.schubert.nk." + name))
        for wrong in ("", "InspectorCredentialLoader", "dev.codex.schubert.nk.bootstrap.Unknown"):
            with self.assertRaises(ValueError):
                bootstrap_ownership.owner(wrong)

    def test_shared_package_and_exact_method_ownership(self):
        prefix = "dev.codex.schubert.nk.api.file."
        for name in ("AssetChecksumManifestTest", "AssetManifestLoaderTest", "HeldMediaFileInspectorTest"):
            self.assertEqual("NK-MED-001", media.shared_file_program(prefix + name))
        self.assertEqual("NK-DAT-001", media.shared_file_program(prefix + "InspectorCredentialLoaderTest"))
        self.assertEqual("NK-DAT-001", media.shared_file_program(prefix + "InspectorDatabaseCredentialLoaderTest"))
        self.assertEqual("NK-DAT-001", media.shared_file_program(prefix + "InspectorApplicationTest"))
        self.assertEqual("NK-OPS-001", media.shared_file_program(prefix + "ServiceCredentialReaderTest"))
        self.assertEqual("NK-OPS-001", media.shared_file_program(prefix + "ServiceCredentialSetTest"))
        # Every future OPS API-file test in the deployed inventory must be classified by the
        # independent media collector before a full formal run can be certified.
        deployed_file_tests = [cls for cls, _, _ in launch.DEPLOYMENT_GROUPS if cls.startswith(prefix)]
        self.assertGreaterEqual(len(deployed_file_tests), 2)
        for cls in deployed_file_tests:
            self.assertEqual("NK-OPS-001", media.shared_file_program(cls))
        with self.assertRaisesRegex(ValueError, "unmapped"):
            media.shared_file_program(prefix + "FutureServiceFileTest")
        for name in ("NewMediaTest", "", "InspectorCredentialLoaderTest"):
            with self.assertRaisesRegex(ValueError, "unmapped"):
                media.shared_file_program(name)
        expected = {"PT-MED-X": "A#one", "PT-MED-Y": "B#two"}
        media.validate_method_inventory(["B#two", "A#one"], expected)
        for methods in (["A#one"], ["A#one", "B#two", "A#new"],
                        ["A#one", "A#one"], ["A#one", "C#two"]):
            with self.assertRaisesRegex(ValueError, "Test IDs"):
                media.validate_method_inventory(methods, expected)

    def test_every_scope_run_source_and_integrity(self):
        # Independently enumerated mandatory inventory, not generated from gate.SCOPES.
        expected_scopes = ["008_NK-SCN-001", "007_NK-AUT-001", "003_NK-PRO-003",
                           "006_NK-MSG-002", "009_NK-MED-001", "010_NK-ADM-001", "015_NK-WEB-001", "017_NK-BAT-001", "011_NK-QST-001", "012_NK-ASY-001", "016_NK-WEB-002"]
        expected_scopes = [p + "/evidence" for p in expected_scopes] + [
            "004_NK-DAT-001/evidence/" + p for p in (
                "inbox-inspection", "authentication-inspection", "inspection-sql", "deletion-sql",
                "authentication-cleanup", "non-authentication-inspection", "full-inbox-sql",
                "full-inbox-cleanup", "outbox-only-cleanup", "inbox-progress-sql",
                "inbox-progress-service", "cleanup-safety", "inbox-run-executor",
                "inbox-aes-credential", "credential-access", "inode-security", "credential-loader",
            "inspector-process", "log-cleanup-progress", "question-query", "result-binding", "question-mutation", "inspector-database", "inspector-application", "inspector-launch")] + ["018_NK-OPS-001/evidence", "004_NK-DAT-001/evidence/backup-rerun", "004_NK-DAT-001/evidence/run-references", "004_NK-DAT-001/evidence/parent-summary", "004_NK-DAT-001/evidence/atomic-cleanup", "004_NK-DAT-001/evidence/expiry-audit", "005_NK-MSG-001/evidence/sync-consumers", "005_NK-MSG-001/evidence/web-reply-consumer", "006_NK-MSG-002/003_WebLogReplayWorker/evidence", "005_NK-MSG-001/evidence/api-web-log-consumer", "005_NK-MSG-001/evidence/api-messaging-parent", "005_NK-MSG-001/evidence/log-path-router", "005_NK-MSG-001/evidence/api-log-path-runtime", "005_NK-MSG-001/evidence/request-sender-resource", "005_NK-MSG-001/evidence/jms-resource-compounds", "006_NK-MSG-002/004_JmsResourceCompounds/evidence", "006_NK-MSG-002/005_LogReplayVertical/evidence"]
        self.assertEqual(expected_scopes, list(gate.SCOPES))
        with tempfile.TemporaryDirectory(prefix="nk-evidence-set-") as temporary:
            root = Path(temporary)
            for scope in expected_scopes:
                self.write_scope(root, scope)
            accepted = gate.validate_all(root, "PT-WEB-TEST", "a" * 40, "dev-foundation")
            self.assertEqual(expected_scopes, [item["scope"] for item in accepted])
            # Each scope must reject each wrong binding, even with a consistent checksum file.
            for scope in expected_scopes:
                for field, wrong in (("runId", "PT-WEB-OLD"), ("targetCommit", "b" * 40),
                                     ("branch", "main"), ("exitCode", 1)):
                    self.write_scope(root, scope, {field: wrong})
                    with self.assertRaisesRegex(ValueError, "mixed"):
                        gate.validate_scope(root, scope, "PT-WEB-TEST", "a" * 40, "dev-foundation")
                self.write_scope(root, scope)
            chosen = expected_scopes[-1]
            directory = root / chosen
            check = lambda: gate.validate_all(root, "PT-WEB-TEST", "a" * 40, "dev-foundation")
            baseline = (directory / "manifest.json").read_bytes()
            for wrong in ("missing.xml", "../results.xml", "/tmp/outside"):
                m = json.loads(baseline)
                m["files"][0]["path"] = wrong
                self.write_scope(root, chosen, m)
                with self.assertRaises(ValueError):
                    check()
            self.write_scope(root, chosen)
            for name in ("manifest.json", "results.xml", "checksums.sha256"):
                path = directory / name
                original = path.read_bytes()
                path.unlink()
                with self.assertRaises((ValueError, FileNotFoundError)):
                    check()
                path.write_bytes(original)
            (directory / "results.xml").write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError, "hash"):
                check()
            self.write_scope(root, chosen)
            for values in (
                {"files": []},
                {"files": json.loads(baseline)["files"] * 2},
                {"fullReactorManifest": "manifest.json"},
                {"fullReactorManifestSha256": "0" * 64},
            ):
                self.write_scope(root, chosen, values)
                with self.assertRaises(ValueError):
                    check()
            self.write_scope(root, chosen)
            original = (directory / "checksums.sha256").read_text()
            for wrong in ("bad\n", "", original + original, original.replace("  results.xml", "  unknown.xml")):
                (directory / "checksums.sha256").write_text(wrong)
                with self.assertRaises(ValueError):
                    check()
            self.write_scope(root, chosen)
            self.assertEqual(53, len(check()))
            outside = root / "outside.xml"
            outside.write_bytes(b"fixture")
            link = directory / "escape.xml"
            link.symlink_to(outside)
            for relative in ("", "../results.xml", str(outside), "missing.xml", "escape.xml"):
                with self.assertRaises(ValueError):
                    gate.local_file(directory, relative)

    def test_manifest_json_has_unique_keys_and_integer_exit(self):
        with tempfile.TemporaryDirectory(prefix="nk-manifest-schema-") as temporary:
            root = Path(temporary)
            scope = "009_NK-MED-001/evidence"
            self.write_scope(root, scope)
            directory = root / scope
            path = directory / "manifest.json"
            original = path.read_text()
            self.assertEqual(
                scope, gate.validate_scope(root, scope, "PT-WEB-TEST", "a" * 40, "dev-foundation")["scope"]
            )
            invalid = {
                "boolean_exit": original.replace('"exitCode": 0', '"exitCode": false'),
                "decimal_exit": original.replace('"exitCode": 0', '"exitCode": 0.0'),
                "duplicate_exit": original.replace('"exitCode": 0', '"exitCode": 1, "exitCode": 0'),
                "duplicate_nested_key": original.replace(
                    '"path": "results.xml"', '"path": "wrong.xml", "path": "results.xml"'
                ),
                "non_json_number": original[:-1] + ', "elapsed": NaN}',
            }
            for label, data in invalid.items():
                with self.subTest(label=label):
                    self.assertNotEqual(original, data)
                    path.write_text(data)
                    (directory / "checksums.sha256").write_text(
                        "".join(
                            hashlib.sha256((directory / name).read_bytes()).hexdigest()
                            + "  " + name + "\n"
                            for name in ("manifest.json", "results.xml")
                        )
                    )
                    with self.assertRaises(ValueError):
                        gate.validate_scope(root, scope, "PT-WEB-TEST", "a" * 40, "dev-foundation")

    def test_provisional_siblings_remain_outside_the_formal_inventory(self):
        with tempfile.TemporaryDirectory(prefix="nk-formal-inventory-") as temporary:
            root = Path(temporary)
            scope = "009_NK-MED-001/evidence"
            self.write_scope(root, scope)
            directory = root / scope

            def validate():
                return gate.validate_scope(root, scope, "PT-WEB-TEST", "a" * 40, "dev-foundation")

            for name in ("PG42740-study-v1", "PG18788-OLD-RANGE-V1", "provisional"):
                supplemental = directory / name
                supplemental.mkdir()
                (supplemental / "manifest.json").write_text('{"run":"separate"}')
                (supplemental / "results.xml").write_text("different results")
            self.assertEqual(scope, validate()["scope"])

            (directory / "logs").mkdir()
            for name in ("manifest.json", "checksums.sha256"):
                (directory / "logs" / name).write_text("separate scope metadata")
            self.assertEqual(scope, validate()["scope"])
            for candidate in ("PG42740.json", "PG0-empty", "logs/PG42740-nested/results.xml",
                              "logs/other-manifest.json"):
                unlisted = directory / candidate
                unlisted.parent.mkdir(parents=True, exist_ok=True)
                unlisted.write_text("unlisted")
                with self.assertRaisesRegex(ValueError, "file inventory"):
                    validate()
                unlisted.unlink()
            (directory / "PG42741-linked-v1").symlink_to(directory / "provisional")
            with self.assertRaisesRegex(ValueError, "symbolic link"):
                validate()
            (directory / "PG42741-linked-v1").unlink()

            supplemental_file = "PG42740-study-v1/results.xml"
            item = {"path": supplemental_file,
                    "sha256": hashlib.sha256((directory / supplemental_file).read_bytes()).hexdigest()}
            self.write_scope(root, scope, {"files": [item]})
            with self.assertRaisesRegex(ValueError, "file inventory"):
                validate()

    def test_persisted_reactor_receipt_is_bound_to_its_manifest(self):
        with tempfile.TemporaryDirectory(prefix="nk-reactor-receipt-") as scratch:
            root = Path(scratch)
            scope = gate.ROOT_MANIFEST.removesuffix("/manifest.json")
            self.write_scope(root, scope)
            directory = root / scope
            receipt = "logs/PT-WEB-TEST-junit-receipt.json"
            path = directory / receipt
            path.parent.mkdir()
            original = json.dumps({
                "schema": "pgpt-reactor-junit-v1", "runId": "PT-WEB-TEST", "targetCommit": "a" * 40
            }).encode()
            different_run = original.replace(b"PT-WEB-TEST", b"PT-WEB-OTHER")
            for linked, content, good_hash in (
                (receipt, original, True),
                (receipt, original, False),
                ("results.xml", original, True),
                (receipt, different_run, True),
            ):
                path.write_bytes(content)
                expected = hashlib.sha256(content).hexdigest()
                recorded = expected if good_hash else "b" * 64
                with self.subTest(linked=linked, recorded=recorded):
                    manifest = json.loads((directory / "manifest.json").read_bytes())
                    manifest["files"] = [
                        {"path": name, "sha256": hashlib.sha256((directory / name).read_bytes()).hexdigest()}
                        for name in ("results.xml", receipt)
                    ]
                    manifest["reactorJunitReceipt"] = linked
                    manifest["reactorJunitReceiptSha256"] = recorded
                    (directory / "manifest.json").write_text(json.dumps(manifest))
                    (directory / "checksums.sha256").write_text("".join(
                        hashlib.sha256((directory / name).read_bytes()).hexdigest() + "  " + name + "\n"
                        for name in ("manifest.json", "results.xml", receipt)
                    ))
                    if linked == receipt and content == original and good_hash:
                        result = gate.validate_scope(root, scope, "PT-WEB-TEST", "a" * 40, "dev-foundation")
                        self.assertEqual(scope, result["scope"])
                    else:
                        with self.assertRaisesRegex(ValueError, "persisted reactor JUnit receipt"):
                            gate.validate_scope(root, scope, "PT-WEB-TEST", "a" * 40, "dev-foundation")

    def test_candidate_reservation_rejects_existing_inside_or_aliased_paths(self):
        with tempfile.TemporaryDirectory(prefix="nk-formal-reservation-") as scratch:
            base = Path(scratch)
            repo = base / "repo"
            repo.mkdir()
            run = "PT-WEB-RESERVATION"
            candidate = gate.reserve_candidate(repo, run)
            self.assertEqual(base / "pgpt-formal-candidates" / run, candidate)
            self.assertEqual(0o700, candidate.stat().st_mode & 0o777)
            retained = candidate / "retained"
            retained.write_bytes(b"prior")
            with self.assertRaises(FileExistsError):
                gate.reserve_candidate(repo, run)
            self.assertEqual(b"prior", retained.read_bytes())
            with self.assertRaisesRegex(ValueError, "outside"):
                gate.reserve_candidate(repo, run, repo / "evidence-new")
            alias = base / "alias"
            alias.symlink_to(candidate)
            with self.assertRaisesRegex(ValueError, "non-aliased"):
                gate.reserve_candidate(repo, run, alias / "elsewhere")
            with patch.dict("os.environ", {}, clear=True):
                self.assertEqual(repo / "evidence/01_PT", evidence_output_root(repo))
            with patch.dict("os.environ", {CANDIDATE_ROOT_ENV: str(base / "unreserved")}):
                with self.assertRaisesRegex(ValueError, "not reserved"):
                    evidence_output_root(repo)

    def test_candidate_root_is_forwarded_to_all_calls_and_validated(self):
        with tempfile.TemporaryDirectory(prefix="nk-formal-all-candidate-") as scratch:
            base = Path(scratch)
            repo = base / "repo"
            repo.mkdir()
            candidate = gate.reserve_candidate(repo, "PT-WEB-TEST", base / "private")
            canonical = repo / "evidence/01_PT"
            self.write_scope(canonical, gate.ROOT_MANIFEST.removesuffix("/manifest.json"),
                             {"runId": "PT-WEB-PREVIOUS"})
            stored = (canonical / gate.ROOT_MANIFEST).read_bytes()
            calls = []

            def complete(command, *, cwd, check, env):
                self.assertEqual(repo, cwd)
                self.assertTrue(check)
                self.assertEqual(str(candidate), env[CANDIDATE_ROOT_ENV])
                self.assertEqual("PT-WEB-TEST", command[3])
                calls.append(command)
                if Path(command[2]).name.startswith("040_"):
                    for scope in gate.SCOPES:
                        self.write_scope(candidate, scope)

            gate.collect(repo, "PT-WEB-TEST", execute=complete, candidate_root=candidate)
            self.assertEqual(53, len(calls))
            self.assertEqual("--preflight", calls[0][-1])
            self.assertEqual(53, len(gate.validate_all(candidate, "PT-WEB-TEST", "a" * 40, "dev-foundation")))
            self.assertEqual(stored, (canonical / gate.ROOT_MANIFEST).read_bytes())

    def test_late_writer_failure_preserves_prior_root_and_retains_partial_candidate(self):
        with tempfile.TemporaryDirectory(prefix="nk-formal-failed-candidate-") as scratch:
            base = Path(scratch)
            repo = base / "repo"
            repo.mkdir()
            candidate = gate.reserve_candidate(repo, "PT-WEB-TEST", base / "fresh")
            canonical = repo / "evidence/01_PT"
            scope = gate.ROOT_MANIFEST.removesuffix("/manifest.json")
            self.write_scope(canonical, scope, {"runId": "PT-WEB-PREVIOUS"})
            prior = (canonical / gate.ROOT_MANIFEST).read_bytes()
            calls = []

            def fail(command, *, cwd, check, env):
                name = Path(command[2]).name[:3]
                calls.append(name)
                if name == "006":
                    self.write_scope(Path(env[CANDIDATE_ROOT_ENV]), scope)
                elif name == "003":
                    raise subprocess.CalledProcessError(4, command)

            with self.assertRaises(subprocess.CalledProcessError) as error:
                gate.collect(repo, "PT-WEB-TEST", execute=fail, candidate_root=candidate)
            self.assertEqual(4, error.exception.returncode)
            self.assertEqual(["020", "006", "003"], calls)
            self.assertEqual(prior, (canonical / gate.ROOT_MANIFEST).read_bytes())
            self.assertTrue((candidate / gate.ROOT_MANIFEST).is_file())
            with self.assertRaises(FileNotFoundError):
                gate.validate_all(candidate, "PT-WEB-TEST", "a" * 40, "dev-foundation")

    def test_real_child_writer_reads_fixtures_from_checkout_and_writes_to_candidate(self):
        with tempfile.TemporaryDirectory(prefix="nk-formal-child-writer-") as scratch:
            base = Path(scratch)
            repo = base / "repo"
            program = repo / "evidence/01_PT/005_NK-MSG-001"
            program.mkdir(parents=True)
            fixture = "001_NK-MSG-001_単体テスト仕様書.md"
            (program / fixture).write_bytes(b"original test specification")
            (program / "002_NK-MSG-001_実行結果.md").write_bytes(b"prior documented result")
            candidate = gate.reserve_candidate(repo, "PT-WEB-TEST", base / "candidate")
            self.write_scope(candidate, gate.ROOT_MANIFEST.removesuffix("/manifest.json"))
            reactor = candidate / gate.ROOT_MANIFEST
            verified = json.loads(reactor.read_bytes())
            verified.update(startedAt="begin", completedAt="end", command="fixture",
                            environment={}, rawLogSha256="a" * 64)
            for filename in jms_compounds.SOURCES:
                path = repo / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"independent source fixture")
            with patch.dict("os.environ", {CANDIDATE_ROOT_ENV: str(candidate)}):
                jms_compounds.write_scope(repo, reactor, verified, "NK-MSG-001",
                                          "005_NK-MSG-001", {"PT-FAKE-01": "Fake#one"}, {})
            scope = "005_NK-MSG-001/evidence/jms-resource-compounds"
            self.assertEqual(b"original test specification", (candidate / scope / "logs" / fixture).read_bytes())
            self.assertFalse((program / "evidence").exists())
            gate.validate_scope(candidate, scope, "PT-WEB-TEST", "a" * 40, "dev-foundation")

    def test_collection_stops_at_each_failure(self):
        for failed_at in range(53):
            calls = []
            def fail(command, *, cwd, check):
                self.assertEqual(Path("/safe/repo"), cwd)
                self.assertTrue(check)
                calls.append(command)
                if len(calls) == failed_at + 1:
                    raise subprocess.CalledProcessError(1, command)
            with self.assertRaises(subprocess.CalledProcessError):
                gate.collect(Path("/safe/repo"), "PT-WEB-TEST", fail)
            self.assertEqual(failed_at + 1, len(calls))
        calls = []
        gate.collect(Path("/safe/repo"), "PT-WEB-TEST", lambda cmd, **kwargs: calls.append(cmd))
        self.assertEqual(53, len(calls))
        self.assertTrue(calls[0][2].endswith("/020_collect_batch_evidence.py"))
        self.assertEqual(["PT-WEB-TEST", "--preflight"], calls[0][3:])
        self.assertTrue(calls[1][2].endswith("/006_collect_scenario_evidence.py"))
        self.assertTrue(calls[-10][2].endswith("/030_collect_sync_consumers.py"))
        self.assertTrue(calls[-9][2].endswith("/031_collect_web_reply_consumers.py"))
        self.assertTrue(calls[-8][2].endswith("/032_collect_web_log_worker.py"))
        self.assertTrue(calls[-7][2].endswith("/033_collect_api_web_log_consumers.py"))
        self.assertTrue(calls[-6][2].endswith("/034_collect_api_messaging_runtime.py"))
        self.assertTrue(calls[-5][2].endswith("/035_collect_log_path_router.py"))
        self.assertTrue(calls[-4][2].endswith("/036_collect_api_log_path_runtime.py"))
        self.assertTrue(calls[-3][2].endswith("/038_collect_request_sender_resource.py"))
        self.assertTrue(calls[-2][2].endswith("/039_collect_jms_resource_compounds.py"))
        self.assertTrue(calls[-1][2].endswith("/040_collect_log_replay_vertical.py"))
        self.assertEqual("PT-WEB-TEST", calls[-1][-1])

    @staticmethod
    def write_scope(root, scope, changes=None):
        directory = root / scope
        directory.mkdir(parents=True, exist_ok=True)
        payload = b"<testsuite/>\n"
        (directory / "results.xml").write_bytes(payload)
        manifest = {
            "runId": "PT-WEB-TEST", "targetCommit": "a" * 40,
            "branch": "dev-foundation", "exitCode": 0,
            "files": [{"path": "results.xml", "sha256": hashlib.sha256(payload).hexdigest()}],
        }
        if scope.startswith(("004_", "005_", "006_NK-MSG-002/003_", "006_NK-MSG-002/004_", "006_NK-MSG-002/005_", "011_", "012_", "016_", "017_", "018_")):
            manifest.update({
                "fullReactorManifest": ("../../../" if scope.startswith(("004_", "005_", "006_NK-MSG-002/003_", "006_NK-MSG-002/004_", "006_NK-MSG-002/005_")) else "../../") + "008_NK-SCN-001/evidence/manifest.json",
                "fullReactorManifestSha256": hashlib.sha256(
                    (root / "008_NK-SCN-001/evidence/manifest.json").read_bytes()).hexdigest(),
            })
        manifest.update(copy.deepcopy(changes or {}))
        (directory / "manifest.json").write_text(json.dumps(manifest))
        (directory / "checksums.sha256").write_text("".join(
            hashlib.sha256((directory / name).read_bytes()).hexdigest() + "  " + name + "\n"
            for name in ("manifest.json", "results.xml")))


if __name__ == "__main__":
    unittest.main()
