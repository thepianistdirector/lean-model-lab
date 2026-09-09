"""Research proposals, admitted experiments and auditable language-model evidence."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .config import validate_config
from .artifacts import write_json_new, write_new
from .contracts import ContractError, digest, make_workload, read_json, validate_workload


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='lean-model-lab', description=__doc__)
    p.add_argument('--version', action='version', version=__version__)
    commands = p.add_subparsers(dest='command', required=True)
    trace = commands.add_parser('trace', help='create or verify the frozen synthetic workload')
    action = trace.add_subparsers(dest='action', required=True)
    create = action.add_parser('create'); create.add_argument('--output', type=Path, required=True)
    validate = action.add_parser('validate'); validate.add_argument('path', type=Path)
    evaluate = commands.add_parser('evaluate', help='validate every attempt in a directory and derive metrics')
    evaluate.add_argument('--workload', type=Path, required=True)
    evaluate.add_argument('--config', type=Path, required=True)
    evaluate.add_argument('--attempts', type=Path, required=True)
    evaluate.add_argument('--output', type=Path, required=True)
    evaluate.add_argument('--html', type=Path)
    run = commands.add_parser('run', help='execute the admitted CPU study; exact local artifacts and setup ledger required')
    run.add_argument('--server',type=Path,required=True)
    run.add_argument('--model',type=Path,required=True)
    run.add_argument('--setup',type=Path,required=True)
    run_auth=run.add_mutually_exclusive_group(required=True)
    run_auth.add_argument('--admission',type=Path)
    run_auth.add_argument('--recipe',type=Path)
    run.add_argument('--predecessor',type=Path,action='append',default=[],help='retain complete prior recipe-study costs from the same allocation')
    run.add_argument('--output',type=Path,required=True)
    inspect = commands.add_parser('inspect', help='verify authoritative inventory, raw hashes and unfinished attempts')
    inspect.add_argument('study',type=Path)
    recover = commands.add_parser('recover-journal', help='archive and rebuild a torn index; never rerun inference')
    recover.add_argument('study',type=Path)
    report = commands.add_parser('report', help='derive a report from a reconciled study inventory')
    report.add_argument('study',type=Path)
    report.add_argument('--output',type=Path,required=True)
    report.add_argument('--html',type=Path)
    reconcile=commands.add_parser('reconcile',help='close unfinished same-boot attempts without fabricating lost observations')
    reconcile.add_argument('study',type=Path)
    resume=commands.add_parser('resume',help='restart unfinished cells with new attempt IDs and retained prior costs')
    resume.add_argument('study',type=Path)
    resume.add_argument('--server',type=Path,required=True)
    resume.add_argument('--model',type=Path,required=True)
    resume_auth=resume.add_mutually_exclusive_group(required=True)
    resume_auth.add_argument('--admission',type=Path)
    resume_auth.add_argument('--recipe',type=Path)
    commands.add_parser('profiles',help='list exact reviewed model profiles; no download or inference')
    allocation=commands.add_parser('allocation',help='record an explicitly approved finite local allocation')
    alloc_sub=allocation.add_subparsers(dest='action',required=True)
    alloc_create=alloc_sub.add_parser('create')
    alloc_create.add_argument('--hours',type=int,required=True)
    alloc_create.add_argument('--disk-gb',type=int,required=True)
    alloc_create.add_argument('--memory-gb',type=int,required=True)
    alloc_create.add_argument('--threads',type=int,required=True)
    alloc_create.add_argument('--approval-reference',required=True)
    alloc_create.add_argument('--approve',action='store_true',required=True,help='explicitly assert operator approval; not an authentication signature')
    alloc_create.add_argument('--output',type=Path,required=True)
    recipe=commands.add_parser('recipe',help='create or validate a frozen version2 comparison contract')
    recipe_sub=recipe.add_subparsers(dest='action',required=True)
    recipe_create=recipe_sub.add_parser('create')
    recipe_create.add_argument('--allocation',type=Path,required=True)
    recipe_create.add_argument('--model-profile',required=True)
    recipe_create.add_argument('--output',type=Path,required=True)
    recipe_create.add_argument('--requests',type=int,default=128)
    recipe_create.add_argument('--seed',type=int,default=20260907)
    recipe_create.add_argument('--max-output-tokens',type=int,default=32)
    recipe_create.add_argument('--concurrency',type=int,nargs='+',default=[1,4])
    recipe_create.add_argument('--pairs',type=int,default=4)
    recipe_create.add_argument('--threads',type=int)
    recipe_create.add_argument('--purpose',choices=['DEVELOPMENT','MEASUREMENT'],default='MEASUREMENT')
    recipe_create.add_argument('--arrival',choices=['simultaneous','paced','burst'],default='simultaneous')
    recipe_create.add_argument('--interval-ms',type=int,default=0)
    recipe_create.add_argument('--burst-size',type=int,default=8)
    recipe_create.add_argument('--queue-capacity',type=int)
    recipe_create.add_argument('--admission-deadline-ms',type=int)
    recipe_create.add_argument('--ttft-slo-ms',type=int,default=15000)
    recipe_create.add_argument('--end-to-end-slo-ms',type=int,default=30000)
    recipe_validate=recipe_sub.add_parser('validate');recipe_validate.add_argument('path',type=Path)
    workbench=commands.add_parser('workbench',help='inspect compatible local studies and exact request evidence without model loading')
    workbench.add_argument('--study',type=Path,action='append',required=True)
    workbench.add_argument('--output',type=Path,required=True)
    workbench.add_argument('--html',type=Path,required=True)
    research=commands.add_parser('research',help='catalog known methods and freeze falsifiable research proposals; never execute proposal code')
    research_sub=research.add_subparsers(dest='action',required=True)
    catalog=research_sub.add_parser('catalog',help='inspect source-backed techniques and actual local support')
    catalog.add_argument('--domain',choices=['inference','training'])
    catalog.add_argument('--available-only',action='store_true')
    catalog.add_argument('--technique')
    research_sub.add_parser('mechanisms',help='list registered inference interventions and supported task families')
    research_sub.add_parser('templates',help='list a known control and unexecuted research hypotheses')
    propose=research_sub.add_parser('propose',help='write an immutable starting proposal for review')
    proposal_kind=propose.add_mutually_exclusive_group(required=True)
    proposal_kind.add_argument('--template');proposal_kind.add_argument('--mechanism')
    propose.add_argument('--output',type=Path,required=True)
    research_validate=research_sub.add_parser('validate',help='check proposal structure and missing capabilities')
    research_validate.add_argument('path',type=Path)
    freeze=research_sub.add_parser('freeze',help='retain proposal and exact catalog bytes without execution')
    freeze.add_argument('path',type=Path);freeze.add_argument('--output',type=Path,required=True)
    verify=research_sub.add_parser('verify',help='verify frozen proposal/catalog lineage without loading a model')
    verify.add_argument('path',type=Path)
    compose=research_sub.add_parser('compose',help='show integration and interaction gaps for proposed technique combinations')
    compose.add_argument('--technique',action='append',required=True)
    compile_research=research_sub.add_parser('compile',help='bind only the registered known cache control to an unchanged accepted v2 recipe')
    compile_research.add_argument('--proposal',type=Path,required=True)
    compile_research.add_argument('--recipe',type=Path,required=True)
    compile_research.add_argument('--output',type=Path,required=True)
    protocol=research_sub.add_parser('protocol',help='write a starting prospective protocol for a registered inference proposal')
    protocol.add_argument('--proposal',type=Path,required=True);protocol.add_argument('--output',type=Path,required=True)
    study_create=research_sub.add_parser('study-create',help='freeze a registered candidate/proposal/protocol into an executable v3 recipe; does not run inference')
    study_create.add_argument('--proposal',type=Path,required=True)
    study_create.add_argument('--protocol',type=Path,required=True)
    study_create.add_argument('--controller',type=Path,help='frozen model-bound controller.json for learned-gated-slice-v1 only')
    study_create.add_argument('--allocation',type=Path,required=True)
    study_create.add_argument('--model-profile',required=True)
    study_create.add_argument('--output',type=Path,required=True)
    from .structured_workloads import FAMILIES
    study_create.add_argument('--family',choices=FAMILIES,required=True)
    study_create.add_argument('--context-records',type=int,choices=[8,24,64],default=24)
    study_create.add_argument('--split',choices=['development','confirmation'],required=True)
    study_create.add_argument('--requests',type=int,default=128)
    study_create.add_argument('--seed',type=int,required=True)
    study_create.add_argument('--max-output-tokens',type=int,default=32)
    study_create.add_argument('--concurrency',type=int,nargs='+',default=[1])
    study_create.add_argument('--pairs',type=int,default=2)
    study_create.add_argument('--threads',type=int)
    study_create.add_argument('--purpose',choices=['DEVELOPMENT','MEASUREMENT'],required=True)
    study_create.add_argument('--arrival',choices=['simultaneous','paced','burst'],default='simultaneous')
    study_create.add_argument('--interval-ms',type=int,default=0)
    study_create.add_argument('--burst-size',type=int,default=8)
    study_create.add_argument('--queue-capacity',type=int)
    study_create.add_argument('--admission-deadline-ms',type=int)
    study_create.add_argument('--ttft-slo-ms',type=int,default=15000)
    study_create.add_argument('--end-to-end-slo-ms',type=int,default=30000)
    training_protocol=research_sub.add_parser('training-protocol',help='freeze exact fit/calibration recipes before native label collection')
    training_protocol.add_argument('--fit-recipe',type=Path,action='append',required=True)
    training_protocol.add_argument('--calibration-recipe',type=Path,action='append',required=True)
    training_protocol.add_argument('--output',type=Path,required=True)
    train=research_sub.add_parser('train-controller',help='audit actual paired development outputs, fit a small tree and calibrate; no LLM training')
    train.add_argument('--fit-study',type=Path,action='append',required=True)
    train.add_argument('--calibration-study',type=Path,action='append',required=True)
    train.add_argument('--protocol',type=Path,required=True)
    train.add_argument('--output',type=Path,required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command=='research':
            from . import research
            if args.action=='training-protocol':
                from .controller_training import make_training_protocol
                result=make_training_protocol([read_json(p) for p in args.fit_recipe],
                    [read_json(p) for p in args.calibration_recipe])
                write_json_new(args.output,result)
            elif args.action=='train-controller':
                from .controller_training import train_native_controller
                result=train_native_controller(fit_studies=args.fit_study,calibration_studies=args.calibration_study,
                    protocol=read_json(args.protocol),output=args.output)
            elif args.action=='protocol':
                from .research_studies import default_protocol
                result=default_protocol(read_json(args.proposal));write_json_new(args.output,result)
            elif args.action=='study-create':
                from .recipes_v3 import make_recipe_v3
                from .structured_workloads import make_workload_v3
                proposal=research.validate_proposal(read_json(args.proposal))
                workload=make_workload_v3(family=args.family,context_records=args.context_records,split=args.split,
                    request_count=args.requests,seed=args.seed,max_output_tokens=args.max_output_tokens,
                    concurrency_modes=args.concurrency,arrival_mode=args.arrival,interval_ns=args.interval_ms*1000000,
                    burst_size=args.burst_size,max_queue_requests=args.queue_capacity,
                    request_deadline_ns=None if args.admission_deadline_ms is None else args.admission_deadline_ms*1000000)
                recipe=make_recipe_v3(model_profile_id=args.model_profile,workload=workload,
                    allocation=read_json(args.allocation),mechanism_id=proposal['mechanism_id'],proposal=proposal,
                    protocol=read_json(args.protocol),compute_threads=args.threads,pair_count=args.pairs,
                    purpose=args.purpose,ttft_slo_ns=args.ttft_slo_ms*1000000,end_to_end_slo_ns=args.end_to_end_slo_ms*1000000,
                    controller=read_json(args.controller) if args.controller else None)
                write_json_new(args.output,recipe)
                result={'status':'FROZEN_REGISTERED_STUDY_NOT_EXECUTED','schema_version':3,
                    'recipe_sha256':digest(recipe),'proposal_sha256':digest(proposal),
                    'workload_sha256':digest(workload),'execution_performed':False,
                    'next_step':'Use run --recipe with the exact prepared backend/model/setup and remaining allocation.'}
            elif args.action=='catalog':
                result=research.catalog_view(args.domain,args.available_only,args.technique)
            elif args.action=='mechanisms':
                from .recipes_v3 import MECHANISMS
                from .structured_workloads import FAMILIES, CONTEXT_RECORD_COUNTS
                result={'registered_mechanisms':list(MECHANISMS),'workload_families':list(FAMILIES),
                    'context_record_counts':list(CONTEXT_RECORD_COUNTS),'execution_performed':False,
                    'scope':'Registered bounded CPU inference. No training, arbitrary plugins, automatic novelty or protected isolation.',
                    'entrypoint':'research propose --mechanism ID; research protocol; research study-create; run --recipe'}
            elif args.action=='templates':
                result={'templates':research.template_list(),'execution_performed':False,
                        'scope':'Starting proposals, not demonstrated novelty or executed research.'}
            elif args.action=='propose':
                if args.mechanism:
                    from .research_studies import build_proposal
                    value=build_proposal(args.mechanism)
                else:value=research.template(args.template)
                write_json_new(args.output,value)
                result=research.readiness(value)
            elif args.action=='validate':
                result=research.readiness(read_json(args.path,max_bytes=256*1024))
            elif args.action=='freeze':
                result=research.freeze_proposal(read_json(args.path,max_bytes=256*1024),args.output)
            elif args.action=='verify':
                result=research.verify_frozen(args.path)
            elif args.action=='compose':
                result=research.composition(args.technique)
            else:
                result=research.compile_control(read_json(args.proposal,max_bytes=256*1024),
                                                read_json(args.recipe),args.output)
            print(json.dumps(result,ensure_ascii=False))
        elif args.command=='profiles':
            from .profiles import SMALL_PROFILE,LARGE_PROFILE,get_model_profile
            print(json.dumps({'profiles':[get_model_profile(p['profile_id']) for p in (SMALL_PROFILE,LARGE_PROFILE)],
                'scope':'Reviewed pinned artifacts only; no download, inference or new allocation.'}))
        elif args.command=='allocation':
            from .allocation import make_allocation
            if args.output.exists():raise FileExistsError('allocation record already exists; never reset its start/deadline')
            allocation=make_allocation(full_wall_seconds=args.hours*3600,disk_bytes=args.disk_gb*10**9,
                memory_bytes=args.memory_gb*10**9,compute_threads=args.threads,approval_reference=args.approval_reference)
            write_json_new(args.output,allocation)
            print(json.dumps({'allocation_id':allocation['allocation_id'],'deadline_ns':allocation['deadline_ns'],
                'limits':allocation['limits'],'scope':'Operator assertion only; no inference or publication performed.'}))
        elif args.command=='recipe':
            from .recipes import make_recipe,validate_recipe,workload_from_recipe
            from .workloads import make_workload_v2
            if args.action=='create':
                workload=make_workload_v2(request_count=args.requests,seed=args.seed,max_output_tokens=args.max_output_tokens,
                    arrival_mode=args.arrival,interval_ns=args.interval_ms*10**6,burst_size=args.burst_size,
                    max_queue_requests=args.queue_capacity,request_deadline_ns=None if args.admission_deadline_ms is None else args.admission_deadline_ms*10**6,
                    concurrency_modes=args.concurrency)
                recipe=make_recipe(model_profile_id=args.model_profile,workload=workload,allocation=read_json(args.allocation),
                    compute_threads=args.threads,pair_count=args.pairs,purpose=args.purpose,
                    ttft_slo_ns=args.ttft_slo_ms*10**6,end_to_end_slo_ns=args.end_to_end_slo_ms*10**6)
                write_json_new(args.output,recipe)
            else:recipe=validate_recipe(read_json(args.path));workload=workload_from_recipe(recipe)
            print(json.dumps({'status':'VALID','recipe_sha256':digest(recipe),'model_profile':recipe['model_profile_id'],
                'requests':len(workload['requests']),'concurrency_modes':recipe['evaluation']['concurrency_modes'],
                'pairs_per_concurrency':recipe['evaluation']['pairs_per_concurrency'],'purpose':recipe['purpose'],
                'inference_performed':False}))
        elif args.command=='workbench':
            from .workbench import build_catalog,render_workbench
            outputs=[args.output.resolve(),args.html.resolve()]
            if outputs[0]==outputs[1] or any(p.exists() for p in outputs):raise FileExistsError('choose separate new catalog and HTML paths')
            if any(p.is_relative_to(study.resolve()) for p in outputs for study in args.study):
                raise ContractError('workbench outputs must be outside immutable input studies')
            catalog=build_catalog(args.study);document=render_workbench(catalog)
            write_json_new(args.output,catalog);write_new(args.html,document.encode('utf-8'))
            print(json.dumps({'studies':len(catalog['studies']),'compatibility_groups':len(catalog['compatibility_groups']),
                'inference_performed':False,'scope':catalog['scope']}))
        elif args.command == 'trace':
            if args.action == 'create':
                workload = make_workload(); validate_workload(workload)
                write_json_new(args.output, workload)
            else: workload = validate_workload(read_json(args.path))
            print(json.dumps({'status':'VALID','evidence':'MODEL_FREE_CONTRACT',
                              'requests':len(workload['requests']), 'workload_sha256':digest(workload)}))
        elif args.command == 'evaluate':
            from .evidence import evaluate_campaign
            from .report import render_report
            workload = validate_workload(read_json(args.workload))
            config = validate_config(read_json(args.config))
            attempts = [read_json(path) for path in sorted(args.attempts.glob('*.json'))]
            result = evaluate_campaign(attempts, workload, config=config, config_sha256=digest(config),
                                       workload_sha256=digest(workload))
            # Check destinations before either publication; both remain no-clobber.
            if args.output.exists() or (args.html and args.html.exists()):
                raise FileExistsError('Choose new report paths; existing evidence is never overwritten')
            write_json_new(args.output, result)
            if args.html:
                write_new(args.html, render_report(result).encode('utf-8'))
            print(json.dumps({'finding':result['finding'], 'eligible':result['eligible'],
                              'measured_claim_eligible':result['measured_claim_eligible'],
                              'attempt_count':result['accounting']['attempt_count']}))
        elif args.command == 'run':
            from .runner import run_study
            result=run_study(server=args.server,model=args.model,output=args.output,
                             setup_receipt=read_json(args.setup),admission=read_json(args.admission) if args.admission else None,
                             recipe=read_json(args.recipe) if args.recipe else None,predecessors=args.predecessor)
            print(json.dumps({'reserved_attempts':result['reservation_count'],
                              'terminal_attempts':len(result['attempts']),
                              'inventory_complete':result['inventory_complete']}))
        elif args.command in ('reconcile','resume'):
            from .recovery import reconcile_unfinished,resume_study
            from .session import Session
            if args.command=='reconcile':
                with Session.open(args.study) as session:
                    recovered=reconcile_unfinished(session)
                print(json.dumps({'reconciled_attempt_ids':recovered,'inference_restarted':False}))
            else:
                inventory=resume_study(study=args.study,server=args.server,model=args.model,
                                       admission=read_json(args.admission) if args.admission else None,
                                       recipe=read_json(args.recipe) if args.recipe else None)
                print(json.dumps({'retained_attempts':len(inventory['attempts']),
                                  'inventory_complete':inventory['inventory_complete'],
                                  'note':'earlier interrupted/failed attempts remain part of fixed-design eligibility'}))
        elif args.command in ('inspect','recover-journal','report'):
            from .session import Session
            with Session.open(args.study) as session:
                if args.command=='recover-journal':
                    backup=session.recover_journal()
                    print(json.dumps({'journal_rebuilt':backup is not None,
                                      'inference_restarted':False}))
                else:
                    inventory=session.inspect()
                    if args.command=='inspect':
                        print(json.dumps({'reservation_count':inventory['reservation_count'],
                            'terminal_attempt_count':len(inventory['attempts']),
                            'inventory_complete':inventory['inventory_complete'],
                            'journal_recovery_required':inventory['journal_recovery_required'],
                            'unfinished':[{'attempt_id':r['attempt_id'],'state':r['state'],
                                          'observed_requests':r['observed_requests'],
                                          'known_observed_wall_ns_lower_bound':r['known_observed_wall_ns_lower_bound']}
                                         for r in inventory['unresolved_attempts']],
                            'setup_accounting':inventory['setup_accounting']}))
                    else:
                        from .study_report import evaluate_inventory
                        from .report import render_report
                        import time
                        report_started=time.monotonic_ns()
                        result=evaluate_inventory(inventory,study_root=args.study)
                        if (args.output.exists() or (args.html and args.html.exists()) or
                            args.output.with_suffix(args.output.suffix+'.receipt.json').exists()):
                            raise FileExistsError('Choose new report paths; existing evidence is never overwritten')
                        write_json_new(args.output,result)
                        if args.html:write_new(args.html,render_report(result).encode('utf-8'))
                        report_finished=time.monotonic_ns()
                        write_json_new(args.output.with_suffix(args.output.suffix+'.receipt.json'),{
                            'schema_version':1,'phase':'report-generation','status':'COMPLETED',
                            'source_config_sha256':result['config_sha256'],
                            'started_ns':report_started,'finished_ns':report_finished,
                            'duration_ns':report_finished-report_started,
                            'scope':'this renderer only; producer inventory is unchanged',
                            'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()})
                        print(json.dumps({'finding':result['finding'],
                                          'measured_claim_eligible':result['measured_claim_eligible'],
                                          'full_cost_accounting':result['accounting']['full_cost_accounting']['status']}))
        return 0
    except (ContractError, OSError, ValueError, RuntimeError) as exc:
        print(f'lean-model-lab: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
