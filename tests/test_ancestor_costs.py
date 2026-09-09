"""Historical preparation remains distinct from current-allocation verification."""
import copy
import hashlib
import json
import unittest
from lean_model_lab.ancestor_costs import preparation_ancestors
from lean_model_lab.contracts import ContractError


def fixture():
    records=[{'phase':'build','status':'FAILED','started_ns':10,'finished_ns':20,'bytes_acquired':7,'details':'first build'},
             {'phase':'build','status':'COMPLETED','started_ns':25,'finished_ns':50,'bytes_acquired':11,'details':'corrected build'}]
    raw=json.dumps({'records':records})
    ancestor={'source_receipt_raw_utf8':raw,'source_receipt_sha256':hashlib.sha256(raw.encode()).hexdigest()}
    return {'phase':'source-acquisition','status':'COMPLETED','started_ns':100,'finished_ns':110,'bytes_acquired':0,
            'details':json.dumps({'operation':'reuse-and-verification','ancestor':ancestor})}


class AncestorCostTests(unittest.TestCase):
    def test_failed_historical_costs_deduplicate_without_merging_new_clock(self):
        row=fixture();result=preparation_ancestors([row,copy.deepcopy(row)])
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['attributed_setup_ns'],35)
        self.assertEqual(result[0]['historical_setup_span_ns'],40)
        self.assertEqual(result[0]['failed_phases'],1)
        self.assertEqual(result[0]['known_acquired_bytes'],18)
        self.assertEqual(row['bytes_acquired'],0)

    def test_changed_ancestor_or_overlapping_clock_is_rejected(self):
        row=fixture();details=json.loads(row['details'])
        details['ancestor']['source_receipt_raw_utf8']+=' '
        row['details']=json.dumps(details)
        with self.assertRaises(ContractError):preparation_ancestors([row])
        row=fixture();row['started_ns']=40
        with self.assertRaises(ContractError):preparation_ancestors([row])

if __name__=='__main__':unittest.main()
