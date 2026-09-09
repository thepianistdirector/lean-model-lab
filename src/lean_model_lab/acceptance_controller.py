"""Bounded empirical controller training; no LLM training or risk guarantee.

The fitted depth-two tree predicts harmful omission (full correct, slice wrong).
Separate calibration selects a threshold using native request-cost proxies.
Those proxies omit preparation and training cost and never establish full-cost
improvement. Runtime prediction consumes only parameters and prompt text.
"""
from __future__ import annotations

import copy
from fractions import Fraction
import re

from .context_slice import MAX_RECORDS, _parse, transform_prompt
from .contracts import ContractError, canonical_bytes, digest

MAX_ROWS = 4096
MAX_NS = 2**63 - 1
MAX_DEPTH = 2
FEATURE_VERSION = 'prompt-graph-stats-v1'
FEATURE_BOUNDS = {
    'total_records': (1, MAX_RECORDS),
    'closure_records': (1, MAX_RECORDS),
    'overwritten_writes': (0, MAX_RECORDS-1),
    'min_retained_position_permille': (0, 1000),
    'max_retained_position_permille': (0, 1000),
}
FEATURE_NAMES = tuple(sorted(FEATURE_BOUNDS))
OUTCOMES = ('both_correct', 'full_only_correct', 'slice_only_correct', 'both_wrong')
GRID = (0, 0.05, 0.1, 0.25, 0.5, 1)
GRID_RATIONAL = tuple(Fraction(str(value)) for value in GRID)
MAX_CANDIDATES = sum(high-low for low, high in FEATURE_BOUNDS.values())
SELECTION_RULE = 'maximum_calibration_request_saving_then_lowest_threshold'
CLAIM_LIMIT = ('Empirical controller training with substantial prior-art overlap; no novelty, '
               'conformal, population-risk, LLM-training or full-cost-gain guarantee. '
               'Request cost is dispatch-to-completion only; root must account for all development and deployment costs.')
METADATA_FIELDS = {'model_profile_id', 'model_profile_sha256', 'template_sha256',
                   'source_build_sha256', 'fit_source_sha256', 'calibration_source_sha256'}
ROW_FIELDS = {'source_id', 'group_id', 'features', 'full_correct', 'slice_correct',
              'full_request_ns', 'slice_request_ns'}
NODE_FIELDS = {'node_id', 'depth', 'kind', 'samples', 'outcomes', 'harm_count',
               'feature', 'threshold', 'left', 'right'}
PARAMETER_FIELDS = {'schema_version', 'feature_version', 'mode', 'threshold_index',
                    'tree', 'formal_guarantee'}


def _object(value, fields, label):
    if type(value) is not dict or set(value) != set(fields):
        raise ContractError(label+' must have exactly the declared fields')


def _integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ContractError(label+' must be a bounded integer')


def _hash(value, label):
    if type(value) is not str or re.fullmatch(r'[0-9a-f]{64}', value) is None:
        raise ContractError(label+' must be a lowercase SHA-256 identity')


def _features(value):
    _object(value, FEATURE_BOUNDS, 'features')
    for name, (low, high) in FEATURE_BOUNDS.items():
        _integer(value[name], low, high, 'feature '+name)
    if (value['closure_records'] > value['total_records'] - value['overwritten_writes'] or
            value['min_retained_position_permille'] > value['max_retained_position_permille']):
        raise ContractError('inconsistent graph feature counts or positions')
    if value['total_records'] == 1 and (value['min_retained_position_permille'] or
                                      value['max_retained_position_permille']):
        raise ContractError('single-record positions must be zero')
    positions = {i*1000//max(value['total_records']-1, 1): i for i in range(value['total_records'])}
    low = value['min_retained_position_permille']; high = value['max_retained_position_permille']
    if low not in positions or high not in positions:
        raise ContractError('retained position is not on the declared record grid')
    if (positions[high]-positions[low]+1 < value['closure_records'] or
            value['closure_records'] == 1 and low != high):
        raise ContractError('closure count differs from retained position span')
    return value


def extract_features(prompt):
    """Return five bounded graph statistics, or None for malformed prompt text.

Positions are zero-based record positions scaled by 1000/(record_count-1),
rounded down. Overwritten writes count all superseded assignments, not only
those in the query closure. No literal key, value, family or answer is a feature.
    """
    if type(prompt) is not str:
        raise ContractError('controller prompt must be text')
    try:
        parsed = _parse(prompt)
    except ContractError:
        return None
    total = len(parsed['records'])
    positions = [row['line_index']-5 for row in parsed['closure']]
    result = {'total_records': total, 'closure_records': len(positions),
              'overwritten_writes': total-len(parsed['final']),
              'min_retained_position_permille': min(positions)*1000//max(total-1, 1),
              'max_retained_position_permille': max(positions)*1000//max(total-1, 1)}
    return _features(result)


def _outcome(row):
    return (('both_correct' if row['slice_correct'] else 'full_only_correct') if row['full_correct']
            else ('slice_only_correct' if row['slice_correct'] else 'both_wrong'))


def _counts(rows):
    result = dict.fromkeys(OUTCOMES, 0)
    for row in rows:
        result[_outcome(row)] += 1
    return result


def _validate_counts(value, count, label):
    _object(value, OUTCOMES, label)
    for number in value.values():
        _integer(number, 0, count, label)
    if sum(value.values()) != count:
        raise ContractError(label+' population differs')


def _rows(value, label):
    if type(value) is not list or not 1 <= len(value) <= MAX_ROWS:
        raise ContractError(label+' requires 1..4096 explicit rows')
    seen = set()
    for row in value:
        _object(row, ROW_FIELDS, label+' row')
        for field in ('source_id', 'group_id'):
            _hash(row[field], label+' '+field)
        if row['source_id'] in seen:
            raise ContractError('duplicate row source identity')
        seen.add(row['source_id'])
        _features(row['features'])
        if type(row['full_correct']) is not bool or type(row['slice_correct']) is not bool:
            raise ContractError('outcomes must be explicit booleans')
        for field in ('full_request_ns', 'slice_request_ns'):
            _integer(row[field], 1, MAX_NS, label+' '+field)
    return sorted(copy.deepcopy(value), key=lambda row: row['source_id'])


def _metadata(value):
    _object(value, METADATA_FIELDS, 'controller metadata')
    if (type(value['model_profile_id']) is not str or
            re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,127}', value['model_profile_id']) is None):
        raise ContractError('invalid model profile identity')
    for name in METADATA_FIELDS-{'model_profile_id'}:
        _hash(value[name], name)


def _gini(counts):
    count = sum(counts.values())
    harm = counts['full_only_correct']
    return Fraction(2*harm*(count-harm), count*count)


def _score(left, right):
    total = sum(left.values())+sum(right.values())
    return (sum(left.values())*_gini(left)+sum(right.values())*_gini(right))/total


def _candidates(rows):
    result = []
    for name in FEATURE_NAMES:
        ordered = sorted(rows, key=lambda row: row['features'][name])
        left = dict.fromkeys(OUTCOMES, 0)
        right = _counts(rows)
        for index, row in enumerate(ordered[:-1]):
            outcome = _outcome(row)
            left[outcome] += 1; right[outcome] -= 1
            threshold = row['features'][name]
            if threshold == ordered[index+1]['features'][name]:
                continue
            score = _score(left, right)
            result.append({'feature': name, 'threshold': threshold,
                           'left_outcomes': dict(left), 'right_outcomes': dict(right),
                           'weighted_gini_numerator': score.numerator,
                           'weighted_gini_denominator': score.denominator})
    return result


def _best(candidates, parent):
    if not candidates:
        return None
    selected = min(candidates, key=lambda row: (Fraction(row['weighted_gini_numerator'],
        row['weighted_gini_denominator']), row['feature'], row['threshold']))
    if Fraction(selected['weighted_gini_numerator'], selected['weighted_gini_denominator']) >= _gini(parent):
        return None
    return {'feature': selected['feature'], 'threshold': selected['threshold']}


def _fit(rows, node_id, depth, trace):
    counts = _counts(rows)
    node = {'node_id': node_id, 'depth': depth, 'kind': 'leaf', 'samples': len(rows),
            'outcomes': counts, 'harm_count': counts['full_only_correct'],
            'feature': None, 'threshold': None, 'left': None, 'right': None}
    reason = 'MAX_DEPTH' if depth == MAX_DEPTH else 'PURE_HARM_LABEL' if not _gini(counts) else None
    candidates = [] if reason else _candidates(rows)
    selected = _best(candidates, counts)
    trace.append({'node_id': node_id, 'candidate_splits': candidates, 'selected': selected,
                  'stop_reason': reason if reason else None if selected else 'NO_IMPROVING_SPLIT'})
    if selected:
        left = [row for row in rows if row['features'][selected['feature']] <= selected['threshold']]
        right = [row for row in rows if row['features'][selected['feature']] > selected['threshold']]
        node.update(kind='split', **selected, left=_fit(left, 2*node_id+1, depth+1, trace),
                    right=_fit(right, 2*node_id+2, depth+1, trace))
    return node


def _leaf(tree, features):
    node = tree
    while node['kind'] == 'split':
        node = node['left'] if features[node['feature']] <= node['threshold'] else node['right']
    return node


def _accept(tree, features, index):
    node = _leaf(tree, features)
    threshold = GRID_RATIONAL[index]
    return node['harm_count']*threshold.denominator <= node['samples']*threshold.numerator


def _summary(rows):
    return {'row_count': len(rows), 'rows_sha256': digest(rows), 'outcomes': _counts(rows),
            'source_ids': [row['source_id'] for row in rows],
            'group_ids': sorted({row['group_id'] for row in rows}),
            'full_request_ns': sum(row['full_request_ns'] for row in rows),
            'slice_request_ns': sum(row['slice_request_ns'] for row in rows)}


def _calibrate(tree, rows):
    full_correct = sum(row['full_correct'] for row in rows)
    trace = []
    for index, threshold in enumerate(GRID):
        accepted = [row for row in rows if _accept(tree, row['features'], index)]
        counts = _counts(accepted)
        routed = full_correct-counts['full_only_correct']+counts['slice_only_correct']
        full_ns = sum(row['full_request_ns'] for row in accepted)
        slice_ns = sum(row['slice_request_ns'] for row in accepted)
        trace.append({'threshold_index': index, 'threshold': threshold, 'accepted': len(accepted),
            'accepted_outcomes': counts, 'routed_correct': routed,
            'accepted_full_request_ns': full_ns, 'accepted_slice_request_ns': slice_ns,
            'request_saving_ns': full_ns-slice_ns,
            'eligible': len(accepted) >= 8 and counts['full_only_correct'] == 0 and
                        routed*100 >= 95*len(rows) and full_ns > slice_ns})
    selected = _selected_threshold(trace)
    return trace, selected


def _selected_threshold(trace):
    eligible = [row for row in trace if row['eligible']]
    if not eligible:
        return None
    return min(eligible, key=lambda row: (-row['request_saving_ns'], row['threshold_index']))['threshold_index']


def fit_controller(fit_rows, calibration_rows, *, metadata):
    """Fit on fit_rows only, select a fixed-grid operating point on calibration.

source_id identifies one paired observation; group_id identifies its whole
table/trajectory. Source IDs must be unique and fit/calibration groups disjoint.
Metadata identities are supplied assertions bound into the artifact, not evidence
of authenticity; the caller must verify native labels and model/build identity.
    """
    _metadata(metadata)
    fit_rows = _rows(fit_rows, 'fit'); calibration_rows = _rows(calibration_rows, 'calibration')
    if len(fit_rows)+len(calibration_rows) > MAX_ROWS:
        raise ContractError('fit and calibration exceed combined 4096-row budget')
    for field in ('source_id', 'group_id'):
        if {row[field] for row in fit_rows} & {row[field] for row in calibration_rows}:
            raise ContractError('fit/calibration '+field+' overlap')
    trace = []
    tree = _fit(fit_rows, 0, 0, trace)
    calibration_trace, selected = _calibrate(tree, calibration_rows)
    value = {'schema_version': 1, 'controller_kind': 'DEPTH2_EMPIRICAL_HARM_GATE',
        'metadata': copy.deepcopy(metadata),
        'parameters': {'schema_version': 1, 'feature_version': FEATURE_VERSION,
            'mode': 'ALWAYS_FULL' if selected is None else 'LEARNED_GATE',
            'threshold_index': selected, 'tree': tree, 'formal_guarantee': False},
        'training': {**_summary(fit_rows), 'target': 'full_correct_and_not_slice_correct',
            'split_rule': 'strict_binary_harm_gini_improvement_then_feature_then_threshold',
            'max_depth': MAX_DEPTH, 'trace': sorted(trace, key=lambda row: row['node_id'])},
        'calibration': {**_summary(calibration_rows), 'grid': list(GRID), 'trace': calibration_trace,
            'selection_rule': SELECTION_RULE, 'selected_threshold_index': selected,
            'refusal_reason': 'NO_FEASIBLE_CALIBRATION_THRESHOLD' if selected is None else None},
        'formal_guarantee': False, 'claim_limit': CLAIM_LIMIT}
    value['controller_sha256'] = digest(value)
    return validate_controller(value)


def _validate_tree(node, node_id=0, depth=0, nodes=None, bounds=None):
    if nodes is None:
        nodes = {}
    if bounds is None:
        bounds = FEATURE_BOUNDS
    if depth > MAX_DEPTH:
        raise ContractError('controller exceeds depth-two tree budget')
    _object(node, NODE_FIELDS, 'tree node')
    _integer(node['node_id'], node_id, node_id, 'tree node identity')
    _integer(node['depth'], depth, depth, 'tree depth')
    _integer(node['samples'], 1, MAX_ROWS, 'tree samples')
    _validate_counts(node['outcomes'], node['samples'], 'node outcomes')
    _integer(node['harm_count'], 0, node['samples'], 'node harm count')
    if node['harm_count'] != node['outcomes']['full_only_correct']:
        raise ContractError('node harmful-omission counter differs')
    nodes[node_id] = node
    if node['kind'] == 'leaf':
        if any(node[field] is not None for field in ('feature', 'threshold', 'left', 'right')):
            raise ContractError('leaf contains split fields')
    elif node['kind'] == 'split':
        if depth == MAX_DEPTH or type(node['feature']) is not str or node['feature'] not in FEATURE_BOUNDS:
            raise ContractError('unknown or over-depth tree split')
        low, high = bounds[node['feature']]
        _integer(node['threshold'], low, high-1, 'split threshold')
        left_bounds = dict(bounds); right_bounds = dict(bounds)
        left_bounds[node['feature']] = (low, node['threshold'])
        right_bounds[node['feature']] = (node['threshold']+1, high)
        _validate_tree(node['left'], 2*node_id+1, depth+1, nodes, left_bounds)
        _validate_tree(node['right'], 2*node_id+2, depth+1, nodes, right_bounds)
        for label in OUTCOMES:
            if node['outcomes'][label] != node['left']['outcomes'][label]+node['right']['outcomes'][label]:
                raise ContractError('child outcome populations differ from parent')
    else:
        raise ContractError('unknown tree node kind')
    return nodes


def _validate_parameters(value):
    _object(value, PARAMETER_FIELDS, 'controller parameters')
    _integer(value['schema_version'], 1, 1, 'parameter schema')
    if value['feature_version'] != FEATURE_VERSION or value['formal_guarantee'] is not False:
        raise ContractError('unsupported feature contract or false guarantee')
    if value['mode'] == 'ALWAYS_FULL':
        if value['threshold_index'] is not None:
            raise ContractError('refusal policy cannot contain an acceptance threshold')
    elif value['mode'] == 'LEARNED_GATE':
        _integer(value['threshold_index'], 0, len(GRID)-1, 'threshold index')
    else:
        raise ContractError('unknown controller mode')
    return _validate_tree(value['tree'])


def _validate_summary(value, extras, label):
    _object(value, {'row_count', 'rows_sha256', 'outcomes', 'source_ids', 'group_ids',
                    'full_request_ns', 'slice_request_ns'} | set(extras), label)
    _integer(value['row_count'], 1, MAX_ROWS, label+' row count')
    _hash(value['rows_sha256'], label+' row hash')
    _validate_counts(value['outcomes'], value['row_count'], label+' outcomes')
    for name in ('source_ids', 'group_ids'):
        ids = value[name]
        if type(ids) is not list or not 1 <= len(ids) <= value['row_count']:
            raise ContractError(label+' invalid identity inventory')
        for identity in ids:
            _hash(identity, label+' '+name)
        if ids != sorted(set(ids)) or name == 'source_ids' and len(ids) != value['row_count']:
            raise ContractError(label+' identities are duplicated or unordered')
    for name in ('full_request_ns', 'slice_request_ns'):
        _integer(value[name], value['row_count'], value['row_count']*MAX_NS, label+' '+name)


def _validate_training(value, nodes):
    _validate_summary(value, {'target', 'split_rule', 'max_depth', 'trace'}, 'training summary')
    if (value['target'] != 'full_correct_and_not_slice_correct' or
            value['split_rule'] != 'strict_binary_harm_gini_improvement_then_feature_then_threshold'):
        raise ContractError('unsupported training objective')
    _integer(value['max_depth'], MAX_DEPTH, MAX_DEPTH, 'training depth')
    if value['outcomes'] != nodes[0]['outcomes'] or value['row_count'] != nodes[0]['samples']:
        raise ContractError('tree root differs from fit population')
    if type(value['trace']) is not list or len(value['trace']) != len(nodes):
        raise ContractError('training node trace inventory differs')
    for node_id, row in zip(sorted(nodes), value['trace']):
        _object(row, {'node_id', 'candidate_splits', 'selected', 'stop_reason'}, 'training trace')
        _integer(row['node_id'], node_id, node_id, 'trace node identity')
        node = nodes[node_id]; candidates = row['candidate_splits']
        if type(candidates) is not list or len(candidates) > MAX_CANDIDATES:
            raise ContractError('candidate split trace exceeds budget')
        seen = []
        for candidate in candidates:
            _object(candidate, {'feature', 'threshold', 'left_outcomes', 'right_outcomes',
                'weighted_gini_numerator', 'weighted_gini_denominator'}, 'split candidate')
            name = candidate['feature']
            if type(name) is not str or name not in FEATURE_BOUNDS:
                raise ContractError('unknown candidate feature')
            low, high = FEATURE_BOUNDS[name]
            _integer(candidate['threshold'], low, high-1, 'candidate threshold')
            seen.append((name, candidate['threshold']))
            for key in ('left_outcomes', 'right_outcomes'):
                _object(candidate[key], OUTCOMES, key)
                for number in candidate[key].values():
                    _integer(number, 0, node['samples'], key)
                if not 1 <= sum(candidate[key].values()) < node['samples']:
                    raise ContractError('candidate child is empty or exceeds population')
            for outcome in OUTCOMES:
                if candidate['left_outcomes'][outcome]+candidate['right_outcomes'][outcome] != node['outcomes'][outcome]:
                    raise ContractError('candidate outcome populations differ')
            score = _score(candidate['left_outcomes'], candidate['right_outcomes'])
            _integer(candidate['weighted_gini_numerator'], 0, MAX_ROWS**3, 'gini numerator')
            _integer(candidate['weighted_gini_denominator'], 1, MAX_ROWS**3, 'gini denominator')
            if (candidate['weighted_gini_numerator'], candidate['weighted_gini_denominator']) != (score.numerator, score.denominator):
                raise ContractError('candidate Gini score differs from outcome counts')
        if seen != sorted(set(seen)):
            raise ContractError('candidate trace is duplicated or unordered')
        reason = 'MAX_DEPTH' if node['depth'] == MAX_DEPTH else 'PURE_HARM_LABEL' if not _gini(node['outcomes']) else None
        if reason and candidates:
            raise ContractError('terminal node may not search more splits')
        selected = _best(candidates, node['outcomes'])
        if canonical_bytes(row['selected']) != canonical_bytes(selected):
            raise ContractError('selected split differs from deterministic Gini rule')
        if selected:
            if node['kind'] != 'split' or any(node[k] != selected[k] for k in selected) or row['stop_reason'] is not None:
                raise ContractError('tree split differs from training trace')
            candidate = next(c for c in candidates if all(c[k] == selected[k] for k in selected))
            if node['left']['outcomes'] != candidate['left_outcomes'] or node['right']['outcomes'] != candidate['right_outcomes']:
                raise ContractError('selected split child populations differ')
        elif node['kind'] != 'leaf' or row['stop_reason'] != (reason or 'NO_IMPROVING_SPLIT'):
            raise ContractError('tree leaf differs from stopping rule')


def _validate_calibration(value, parameters):
    _validate_summary(value, {'grid', 'trace', 'selection_rule', 'selected_threshold_index',
                              'refusal_reason'}, 'calibration summary')
    if type(value['grid']) is not list or canonical_bytes(value['grid']) != canonical_bytes(list(GRID)):
        raise ContractError('calibration grid differs from fixed finite grid')
    if value['selection_rule'] != SELECTION_RULE or type(value['trace']) is not list or len(value['trace']) != len(GRID):
        raise ContractError('invalid calibration selection trace')
    previous = None
    full_correct = value['outcomes']['both_correct']+value['outcomes']['full_only_correct']
    for index, row in enumerate(value['trace']):
        _object(row, {'threshold_index', 'threshold', 'accepted', 'accepted_outcomes', 'routed_correct',
            'accepted_full_request_ns', 'accepted_slice_request_ns', 'request_saving_ns', 'eligible'}, 'calibration trace')
        _integer(row['threshold_index'], index, index, 'calibration threshold index')
        if canonical_bytes(row['threshold']) != canonical_bytes(GRID[index]):
            raise ContractError('calibration threshold differs')
        _integer(row['accepted'], 0, value['row_count'], 'accepted population')
        _validate_counts(row['accepted_outcomes'], row['accepted'], 'accepted outcomes')
        for outcome in OUTCOMES:
            if row['accepted_outcomes'][outcome] > value['outcomes'][outcome] or (previous and row['accepted_outcomes'][outcome] < previous['accepted_outcomes'][outcome]):
                raise ContractError('acceptance populations are inconsistent or not nested')
        for label in ('full', 'slice'):
            cost = row['accepted_'+label+'_request_ns']
            _integer(cost, row['accepted'], min(row['accepted']*MAX_NS, value[label+'_request_ns']), 'accepted request cost')
            if previous and cost < previous['accepted_'+label+'_request_ns']:
                raise ContractError('accepted request costs are not nested')
        _integer(row['request_saving_ns'], -MAX_ROWS*MAX_NS, MAX_ROWS*MAX_NS, 'request saving')
        if row['request_saving_ns'] != row['accepted_full_request_ns']-row['accepted_slice_request_ns']:
            raise ContractError('request saving differs from measured request proxies')
        routed = full_correct-row['accepted_outcomes']['full_only_correct']+row['accepted_outcomes']['slice_only_correct']
        _integer(row['routed_correct'], 0, value['row_count'], 'routed correct')
        if row['routed_correct'] != routed:
            raise ContractError('routed quality omitted full-model failures')
        eligible = row['accepted'] >= 8 and row['accepted_outcomes']['full_only_correct'] == 0 and routed*100 >= 95*value['row_count'] and row['request_saving_ns'] > 0
        if type(row['eligible']) is not bool or row['eligible'] != eligible:
            raise ContractError('calibration feasibility differs from empirical rule')
        previous = row
    if previous['accepted'] != value['row_count'] or previous['accepted_outcomes'] != value['outcomes'] or any(previous['accepted_'+label+'_request_ns'] != value[label+'_request_ns'] for label in ('full', 'slice')):
        raise ContractError('threshold one must include every calibration row')
    selected = _selected_threshold(value['trace'])
    if (type(value['selected_threshold_index']) is not type(selected) or value['selected_threshold_index'] != selected or
            parameters['threshold_index'] != selected or
            parameters['mode'] != ('ALWAYS_FULL' if selected is None else 'LEARNED_GATE') or
            value['refusal_reason'] != ('NO_FEASIBLE_CALIBRATION_THRESHOLD' if selected is None else None)):
        raise ContractError('controller operating point differs from calibration selection')


def validate_controller(value):
    """Validate bounded JSON structure, trace arithmetic and artifact identity.

Rows hashes bind caller-supplied evidence. Without the raw rows, this validator
cannot establish that traces exhaust every candidate or authenticate observations.
    """
    _object(value, {'schema_version', 'controller_kind', 'metadata', 'parameters', 'training',
                    'calibration', 'formal_guarantee', 'claim_limit', 'controller_sha256'}, 'controller')
    _integer(value['schema_version'], 1, 1, 'controller schema')
    if value['controller_kind'] != 'DEPTH2_EMPIRICAL_HARM_GATE' or value['formal_guarantee'] is not False or value['claim_limit'] != CLAIM_LIMIT:
        raise ContractError('unsupported controller claim or kind')
    _metadata(value['metadata'])
    nodes = _validate_parameters(value['parameters'])
    _validate_training(value['training'], nodes)
    _validate_calibration(value['calibration'], value['parameters'])
    if value['training']['row_count']+value['calibration']['row_count'] > MAX_ROWS:
        raise ContractError('combined controller row budget exceeded')
    for field in ('source_ids', 'group_ids'):
        if set(value['training'][field]) & set(value['calibration'][field]):
            raise ContractError('fit/calibration identity overlap')
    _hash(value['controller_sha256'], 'controller hash')
    if value['controller_sha256'] != digest({k:v for k,v in value.items() if k != 'controller_sha256'}):
        raise ContractError('controller artifact identity differs')
    return value


def predict(parameters, prompt):
    """Select original full text or certified dependency slice using prompt only."""
    _validate_parameters(parameters)
    if type(prompt) is not str:
        raise ContractError('controller prompt must be text')
    result = {'decision': 'FULL', 'prompt': prompt, 'reason': 'CALIBRATION_REFUSED',
              'features': None, 'risk_numerator': None, 'risk_denominator': None,
              'formal_guarantee': False}
    if parameters['mode'] == 'ALWAYS_FULL':
        return result
    features = extract_features(prompt)
    if features is None:
        result['reason'] = 'MALFORMED_PROMPT'
        return result
    node = _leaf(parameters['tree'], features)
    result.update(features=features, risk_numerator=node['harm_count'], risk_denominator=node['samples'],
                  reason='RISK_ABOVE_THRESHOLD')
    if _accept(parameters['tree'], features, parameters['threshold_index']):
        transformed = transform_prompt(prompt, 'dependency-slice-v1')
        if transformed['decision'] == 'CERTIFIED_SLICE' and transformed['certificate']['dependency_closure_preserved'] is True:
            result.update(decision='DEPENDENCY_SLICE', prompt=transformed['prompt'], reason='EMPIRICAL_CALIBRATION_ACCEPT')
        else:
            result['reason'] = 'DEPENDENCY_CERTIFICATE_REFUSED'
    return result
