"""Same-allocation history cannot be omitted or replaced by exported copies."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from lean_model_lab.contracts import ContractError,digest,file_digest
from lean_model_lab.runner_recipe import discover_predecessors,inherited_setup
from lean_model_lab.session import Session
from lean_model_lab.study_report import evaluate_inventory
from test_evidence_v2 import fixture,make_campaign
from test_study_report_v2 import inventory


def producer(root,*,unresolved=False):
    workload,config=fixture(modes=(1,));allocation=config['recipe']['allocation']
    Session.create(root,config,workload,[])
    with Session.open(root) as session:
        attempt=make_campaign(workload,config)[0]
        reservation=session.reserve(attempt['arm'],attempt['concurrency'],attempt['pair_index'],attempt['started_ns'])
        if not unresolved:
            attempt['attempt_id']=reservation['attempt_id'];attempt['status']='FAILED'
            session.publish(attempt)
    return allocation


class PredecessorDiscoveryTests(unittest.TestCase):
    def test_omitted_failed_measurement_is_discovered_and_blocks_retry(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);allocation=producer(root/'prior')
            paths=discover_predecessors(root,allocation)
            self.assertEqual(paths,[root/'prior'])
            rows=inherited_setup([],paths,allocation)
            self.assertEqual(len(rows),1);self.assertEqual(rows[0]['status'],'FAILED')
            value=inventory()
            # Move the new synthetic campaign after the retained predecessor.
            shift=100000
            for attempt in value['attempts']:
                for key in ('started_ns','service_started_ns','finished_ns'):attempt[key]+=shift
                for request in attempt['requests']:
                    for key in ('arrival_ns','admitted_ns','dispatch_ns','first_token_ns','completed_ns'):request[key]+=shift
                    for event in request['token_events']:event['observed_ns']+=shift
            value['setup_accounting']['records']+=rows
            result=evaluate_inventory(value)
            self.assertFalse(result['eligible'])
            self.assertIn('retained_prior_same_recipe_measurement',result['ineligibility_reasons'])

    def test_matching_unresolved_study_refuses_new_admission(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);allocation=producer(root/'prior',unresolved=True)
            with self.assertRaisesRegex(ContractError,'reconcile every'):discover_predecessors(root,allocation)

    def test_identical_original_copies_deduplicate_and_derivative_cannot_replace_source(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);allocation=producer(root/'prior')
            shutil.copytree(root/'prior',root/'duplicate')
            shutil.copytree(root/'prior',root/'derivative')
            (root/'derivative/EXPORT-PROVENANCE.json').write_text('{}')
            self.assertEqual(len(discover_predecessors(root,allocation)),1)
            shutil.rmtree(root/'prior');shutil.rmtree(root/'duplicate')
            with self.assertRaisesRegex(ContractError,'lacks its original'):discover_predecessors(root,allocation)

    def test_partial_local_producer_cannot_disappear_from_discovery(self):
        for missing in ('attempts','workload.json','session.json','config.json'):
            with self.subTest(missing=missing),tempfile.TemporaryDirectory() as raw:
                root=Path(raw);allocation=producer(root/'prior',unresolved=True)
                path=root/'prior'/missing;path.rename(path.with_name(path.name+'.retained'))
                with self.assertRaises((ValueError,OSError)):discover_predecessors(root,allocation)

    def test_linked_partial_export_still_requires_its_original_producer(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);allocation=producer(root/'prior')
            sidecars=root/'export/original-provenance';sidecars.mkdir(parents=True)
            derived=root/'export/study';derived.mkdir()
            for name in ('config.json','session.json','workload.json'):
                shutil.copyfile(root/'prior'/name,sidecars/name)
            (derived/'EXPORT-PROVENANCE.json').write_text(json.dumps({'source_session_sha256':file_digest(sidecars/'session.json')}))
            self.assertEqual(len(discover_predecessors(root,allocation)),1)
            shutil.rmtree(root/'prior')
            with self.assertRaisesRegex(ContractError,'lacks its original'):discover_predecessors(root,allocation)

    def test_allocation_id_with_changed_clock_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);allocation=producer(root/'prior')
            path=root/'prior/config.json';value=json.loads(path.read_text())
            value['recipe']['allocation']['deadline_ns']+=1;path.write_text(json.dumps(value))
            with self.assertRaisesRegex(ContractError,'conflicting bounds'):discover_predecessors(root,allocation)

if __name__=='__main__':unittest.main()
