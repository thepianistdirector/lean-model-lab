"""Real inert HTTP process: transformed native inputs, journaling and inspection.

These are software controls, never actual model results.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from lean_model_lab.config import make_config_v2
from lean_model_lab.contracts import ContractError, digest, file_digest, read_json
from lean_model_lab.intervention_evidence import verify_interventions
from lean_model_lab.recipes_v3 import make_recipe_v3
from lean_model_lab.research_studies import build_proposal, default_protocol
from lean_model_lab.runner import execute_attempt, hardware
from lean_model_lab.session import Session
from lean_model_lab.structured_workloads import make_workload_v3
from lean_model_lab.workbench import build_catalog
from test_coordinator_v2 import inputs


class CoordinatorV3Tests(unittest.TestCase):
    def prepare(self, root, mechanism='dependency-slice-v1', family='record-updates'):
        _, old, server, model = inputs(root)
        workload = make_workload_v3(request_count=8, family=family, context_records=24,
                                    split='development', concurrency_modes=[1])
        proposal = build_proposal(mechanism)
        controller=None
        if mechanism=='learned-gated-slice-v1':
            from test_research_v3 import fixture_v3
            _,fixture=fixture_v3(mechanism_id=mechanism)
            controller=fixture['recipe']['controller']
        recipe = make_recipe_v3(model_profile_id=old['model']['profile_id'], workload=workload,
            allocation=old['recipe']['allocation'], mechanism_id=mechanism, proposal=proposal,
            protocol=default_protocol(proposal), purpose='DEVELOPMENT', compute_threads=2,controller=controller)
        config = make_config_v2(recipe=recipe, server_sha256=file_digest(server), evidence_class='TEST_FIXTURE',
                                hardware=hardware(), implementation_sha256='a'*64)
        study = root/'study'; Session.create(study, config, workload, [])
        return study, workload, config, server, model

    def test_mixed_native_protocol_reports_all_component_denominators(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);study,w,c,server,model=self.prepare(root,family='record-mixed-v1')
            with Session.open(study) as session, patch('lean_model_lab.runner_recipe.verify_model_files',return_value={'scope':'INERT FIXTURE'}):
                a=execute_attempt(session,server=server,model=model,config=c,workload=w,
                    concurrency=1,pair_index=0,arm='candidate',deadline_ns=c['recipe']['allocation']['deadline_ns'],project_root=root)
                self.assertEqual(a['status'],'COMPLETED')
                inventory=session.inspect()
            self.assertEqual(verify_interventions(study,inventory,a)['status'],'CONSISTENT')
            catalog=build_catalog([study])
            metric=catalog['studies'][0]['attempts'][0]['metrics']
            self.assertEqual(sorted(x['expected_count'] for x in metric['task_families'].values()),[2,3,3])
            from lean_model_lab.workbench import render_workbench
            self.assertIn('Mixed workload component results',render_workbench(catalog))

    def test_instruction_restatement_native_path_retains_full_records_and_audit(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);study,w,c,server,model=self.prepare(root,'explicit-grammar-v2')
            with Session.open(study) as session, patch('lean_model_lab.runner_recipe.verify_model_files',return_value={'scope':'INERT FIXTURE'}):
                a=execute_attempt(session,server=server,model=model,config=c,workload=w,
                    concurrency=1,pair_index=0,arm='candidate',deadline_ns=c['recipe']['allocation']['deadline_ns'],project_root=root)
                self.assertEqual(a['status'],'COMPLETED')
                inventory=session.inspect()
            rows=verify_interventions(study,inventory,a)['requests']
            self.assertTrue(all(r['result']['certificate']['retained_record_count']==24 for r in rows))
            self.assertTrue(all(r['result']['decision']=='EXPLICIT_GRAMMAR_RESTATEMENT' for r in rows))
            self.assertEqual(len(build_catalog([study])['studies']),1)

    def test_frozen_controller_executes_through_native_protocol_and_workbench(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);study,w,c,server,model=self.prepare(root,'learned-gated-slice-v1')
            with Session.open(study) as session, patch('lean_model_lab.runner_recipe.verify_model_files',return_value={'scope':'INERT FIXTURE'}):
                a=execute_attempt(session,server=server,model=model,config=c,workload=w,
                    concurrency=1,pair_index=0,arm='candidate',deadline_ns=c['recipe']['allocation']['deadline_ns'],project_root=root)
                self.assertEqual(a['status'],'COMPLETED')
                inventory=session.inspect()
            verified=verify_interventions(study,inventory,a)
            self.assertTrue(all('controller_prediction' in r['result'] for r in verified['requests']))
            self.assertEqual(len(build_catalog([study])['studies']),1)
            sidecar=study/'raw'/a['attempt_id']/'prompt-interventions.json'
            value=read_json(sidecar);value['requests'][0]['result']['controller_prediction']['reason']='forged'
            import json
            sidecar.write_text(json.dumps(value))
            with self.assertRaisesRegex(ContractError,'transformation differs'):
                verify_interventions(study,inventory,a)

    def test_native_transformation_raw_audit_and_workbench_preserve_task_and_costs(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);study,w,c,server,model=self.prepare(root)
            with Session.open(study) as session, patch('lean_model_lab.runner_recipe.verify_model_files',return_value={'scope':'INERT FIXTURE'}):
                attempts=[]
                for arm in ('baseline','candidate'):
                    a=execute_attempt(session,server=server,model=model,config=c,workload=w,
                        concurrency=1,pair_index=0,arm=arm,deadline_ns=c['recipe']['allocation']['deadline_ns'],project_root=root)
                    self.assertEqual(a['status'],'COMPLETED');attempts.append(a)
                inventory=session.inspect()
                self.assertTrue(inventory['inventory_complete'])
            for a in attempts:
                verified=verify_interventions(study,inventory,a)
                self.assertEqual(verified['status'],'CONSISTENT')
                self.assertGreater(verified['total_intervention_ns'],0)
                self.assertTrue(all(r['output_text']==e['expected'] for r,e in zip(a['requests'],w['requests'])))
                self.assertGreaterEqual(a['overhead_ns']['cache_preparation'],verified['total_intervention_ns'])
            self.assertTrue(all(b['prompt_tokens']>a['prompt_tokens'] for b,a in zip(attempts[0]['requests'],attempts[1]['requests'])))
            # Workbench independently normalizes raw SSE and permits declared
            # cross-arm input changes while retaining actual input IDs.
            catalog=build_catalog([study])
            self.assertEqual(len(catalog['studies']),1)
            self.assertFalse(catalog['studies'][0]['measured_claim_eligible'])
            changed=copy.deepcopy(inventory)
            changed['workload']['requests'][0]['prompt']+=' changed'
            with self.assertRaises(ContractError):verify_interventions(study,changed,attempts[1])

    def test_reconcile_after_publication_loss_retains_timed_preparation_and_native_evidence(self):
        from lean_model_lab.recovery import reconcile_unfinished
        from lean_model_lab.native_evidence import verify_native_inventory
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);study,w,c,server,model=self.prepare(root)
            with Session.open(study) as session, patch('lean_model_lab.runner_recipe.verify_model_files',return_value={'scope':'INERT FIXTURE'}):
                with patch.object(session,'publish',side_effect=OSError('injected terminal publication loss')):
                    with self.assertRaises(OSError):
                        execute_attempt(session,server=server,model=model,config=c,workload=w,
                            concurrency=1,pair_index=0,arm='candidate',deadline_ns=c['recipe']['allocation']['deadline_ns'],project_root=root)
                self.assertFalse(session.inspect()['inventory_complete'])
                with patch('lean_model_lab.recovery.current_boot',return_value='TEST_FIXTURE'):
                    ids=reconcile_unfinished(session)
                inventory=session.inspect()
            self.assertEqual(len(ids),1);self.assertTrue(inventory['inventory_complete'])
            a=inventory['attempts'][0]
            self.assertEqual(a['status'],'INTERRUPTED')
            self.assertGreater(a['overhead_ns']['cache_preparation'],0)
            self.assertEqual(verify_interventions(study,inventory,a)['status'],'CONSISTENT')
            self.assertEqual(verify_native_inventory(study,inventory)['successful_requests_reconciled'],8)

    def test_failed_verification_retains_v3_reservation_without_fabricated_inputs(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);study,w,c,server,model=self.prepare(root)
            with Session.open(study) as session, patch('lean_model_lab.runner_recipe.verify_model_files',side_effect=ContractError('fixture hash mismatch')):
                a=execute_attempt(session,server=server,model=model,config=c,workload=w,
                    concurrency=1,pair_index=0,arm='candidate',deadline_ns=c['recipe']['allocation']['deadline_ns'],project_root=root)
                inventory=session.inspect()
            self.assertEqual(a['status'],'FAILED');self.assertEqual(a['requests'],[])
            self.assertTrue(inventory['inventory_complete'])
            self.assertEqual(verify_interventions(study,inventory,a)['status'],'NOT_REACHED')

if __name__=='__main__':unittest.main()
