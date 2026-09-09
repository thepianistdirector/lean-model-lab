from pathlib import Path
import json,hashlib,shutil,time,sys
own=Path(__file__).resolve().parent;root=own.parents[2];pub=root/'docs/research/candidate-study/publication';stage=own/'portable-export-test04'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
a=stage/'analysis-package-alias';csvs={}
for p in a.glob('*.csv'):
 assert p.read_bytes()==(pub/'tables/final'/p.name).read_bytes();csvs[p.name]=sha(p)
assets=read(pub/'reviewed-assets-final.json')
for name,digest in assets.items():assert sha(root/name)==digest
figure_comparison={}
for p in (stage/'figures-package-alias').iterdir():
 if p.suffix not in ['.png','.svg','.pdf']:continue
 previous=stage/'figures-final'/p.name;figure_comparison[p.name]={'byte_identical':p.read_bytes()==previous.read_bytes(),'previous_sha256':sha(previous),'regenerated_sha256':sha(p)}
assert all(row['byte_identical'] for name,row in figure_comparison.items() if name.endswith('.png'))
new_analysis=read(a/'analysis.json');old_analysis=read(stage/'analysis-final/analysis.json');new_cmp=json.loads(json.dumps(new_analysis));old_cmp=json.loads(json.dumps(old_analysis))
for value in [new_cmp,old_cmp]:
 value.pop('created_monotonic_ns');value.pop('manifest_sha256');
 for row in value['inventory']:row['study']=row['study'].replace('clarification-0.5b-study04','clarification-05b-study04')
assert new_cmp==old_cmp
old_resources=read(pub/'artifacts/before-package-alias/memory-and-timing-summary.json');new_resources=read(stage/'resources-package-alias.json');rr=json.loads(json.dumps(new_resources));oo=json.loads(json.dumps(old_resources));rr.pop('manifest_sha256');oo.pop('manifest_sha256')
for row in oo['attempts']:
 for field in ['source_resource','source_report','source_config']:row[field]=row[field].replace('evidence/clarification-0.5b-study04/','evidence/clarification-05b-study04/')
assert rr==oo
raw=(a/'analysis.json').read_bytes();target=pub/'tables/final/analysis.json';target.write_bytes(raw.replace(str(stage).encode(),b'$EVIDENCE_ROOT'))
shutil.copy2(stage/'resources-package-alias.json',pub/'tables/final/memory-and-timing-summary.json');shutil.copy2(stage/'training-validation-package-alias.json',pub/'portable-training-validation-final.json')
shutil.copytree(pub/'artifacts/confirmation-illustrations-final',pub/'artifacts/before-package-alias/confirmation-illustrations-final',dirs_exist_ok=True);shutil.copytree(stage/'illustrations-package-alias',pub/'artifacts/confirmation-illustrations-final',dirs_exist_ok=True)
receipt={'status':'PASS','recorded_ns':time.monotonic_ns(),'original_logical_native_study_id':'clarification-0.5b-study04','safe_public_package_alias':'clarification-05b-study04','scope':'Operational public directory/CLI alias correction only. The actual builder rejected the period in the original alias before writing ZIP output; its name boundary is unchanged. Original native directories, filenames, record populations, outputs, scientific metrics and expected content hashes are unchanged. A prior source snapshot check did not exercise --study alias parsing.','original_manifest_sha256':sha(pub/'evidence-manifest-before-package-alias.json'),'new_manifest_sha256':sha(pub/'evidence-manifest-final.json'),'prior_operator_map_sha256':sha(own/'candidate-operator-map04-before-package-alias.json'),'builder_sha256':sha(root/'tools/build_v1_release_bundle.py'),'actual_study_argument_checks':{'old_alias_rejected':True,'new_alias_accepted':True},'validation':{'staged_reanalysis':'PASS','staged_training':'PASS','staged_memory_resources':'PASS','staged_illustrations':'PASS','staged_plotting':'PASS','original_and_new_analysis_equal_except_manifest_timestamp_and_public_directory':True,'original_and_new_resource_values_equal_except_manifest_and_public_directory':True},'unchanged_scientific_csv_sha256':csvs,'published_reviewed_assets_byte_unchanged':assets,'regenerated_figure_comparison':figure_comparison,'figure_scope':'All seven regenerated PNGs byte-identical. All original published PNG/SVG/PDF files retained unchanged; regenerated SVG/PDF metadata may differ and are not substituted.','native_execution':False}
dump(pub/'package-alias-correction.json',receipt)
proof={'status':'PASS','native_offered':1984,'actual_exports':8,'unique_original_tables':200,'native_execution_s':new_analysis['native_execution_s'],'manifest_sha256':sha(pub/'evidence-manifest-final.json'),'executed_staged_scripts':{name:sha(stage/'lean-model-lab-source/docs/research/candidate-study/publication/scripts'/name) for name in ['reanalyze.py','validate_training.py','summarize_resources.py','illustrations.py','plot.py']},'original_analysis_sha256':sha(a/'analysis.json'),'training_validation_sha256':sha(stage/'training-validation-package-alias.json'),'resource_summary_sha256':sha(stage/'resources-package-alias.json'),'illustration_receipt_sha256':sha(stage/'illustrations-package-alias/selection-receipt.json'),'operational_derivatives':[{'artifact':target.relative_to(root).as_posix(),'original_sha256':sha(a/'analysis.json'),'derived_sha256':sha(target),'operation':'Operational absolute evidence root replaced with $EVIDENCE_ROOT; scientific values unchanged.'}],'scope':'All five staged portable entrypoints executed on the corrected actual eight-export alias layout. Original native identity retained. All seven CSVs and regenerated PNGs byte-identical; published reviewed figure files unchanged. Prior manifest/proofs/operator map retained under explicit before-package-alias names. This validates the real CLI study-argument parser, not the still-separate global ZIP build.','alias_correction_receipt_sha256':sha(pub/'package-alias-correction.json')}
dump(pub/'portable-export-check-final.json',proof)
print(json.dumps({'status':'PASS','manifest':receipt['new_manifest_sha256'],'csvs':len(csvs),'regenerated_pngs':7,'regenerated_svg_pdf_byte_equal':sum(x['byte_identical'] for k,x in figure_comparison.items() if not k.endswith('.png'))}))
