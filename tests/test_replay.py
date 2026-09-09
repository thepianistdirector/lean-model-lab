"""Fake-clock replay scenarios; no sleeps, inference, files, or external services."""
import copy
import unittest

from lean_model_lab.contracts import make_workload
from lean_model_lab.replay import LaneReplay, ReplayError
from lean_model_lab.workloads import MAX_NS, make_workload_v2


def workload(**kwargs):
    return make_workload_v2(**{'request_count': 8, 'concurrency_modes': (1, 2, 4), **kwargs})


def event(kind, index, now, concurrency=1):
    return {'kind': kind, 'index': index, 'slot': index % concurrency, 'observed_ns': now}


class LaneReplayTests(unittest.TestCase):
    def test_paced_arrivals_are_not_offered_early_or_lost_when_active_work_finishes(self):
        replay = LaneReplay(workload(request_count=4, arrival_mode='paced', interval_ns=10), 1, 100)
        self.assertEqual(100, replay.next_arrival_ns)
        self.assertFalse(replay.done)
        self.assertEqual([event('dispatch', 0, 100)], replay.advance(100))
        self.assertEqual(110, replay.next_arrival_ns)
        replay.complete(0, 0, 101)
        self.assertEqual([], replay.advance(109))
        self.assertEqual(0, replay.pending_count)
        self.assertEqual(0, replay.active_count)
        self.assertFalse(replay.done)
        self.assertEqual([event('dispatch', 1, 110)], replay.advance(110))
        replay.complete(0, 1, 111)
        self.assertEqual([event('dispatch', 2, 120)], replay.advance(120))
        replay.complete(0, 2, 121)
        self.assertEqual([event('dispatch', 3, 130)], replay.advance(130))
        self.assertIsNone(replay.next_arrival_ns)
        self.assertFalse(replay.done)
        replay.complete(0, 3, 131)
        self.assertTrue(replay.done)
        self.assertEqual([], replay.advance(131))

    def test_burst_overflow_offers_every_due_index_and_excludes_active_slots_from_capacity(self):
        replay = LaneReplay(workload(max_queue_requests=2), 2, 50)
        offered = replay.advance(50)
        self.assertEqual([event('dispatch', 0, 50, 2), event('dispatch', 1, 50, 2)] +
                         [event('queue_full', i, 50, 2) for i in range(4, 8)], offered)
        self.assertEqual(2, replay.active_count)
        self.assertEqual(2, replay.pending_count)
        self.assertIsNone(replay.next_arrival_ns)
        self.assertFalse(replay.done)
        replay.complete(0, 0, 51)
        replay.complete(1, 1, 51)
        dispatched = replay.advance(51)
        self.assertEqual([event('dispatch', 2, 51, 2), event('dispatch', 3, 51, 2)], dispatched)
        self.assertEqual(0, replay.pending_count)
        for row in dispatched:
            replay.complete(row['slot'], row['index'], 52)
        self.assertTrue(replay.done)
        self.assertEqual(set(range(8)), {row['index'] for row in offered + dispatched})

    def test_free_lane_direct_dispatch_is_allowed_when_other_lane_fills_global_queue(self):
        replay = LaneReplay(workload(request_count=4, max_queue_requests=1), 2, 0)
        self.assertEqual([event('dispatch', 0, 0, 2), event('dispatch', 1, 0, 2),
                          event('queue_full', 3, 0, 2)], replay.advance(0))
        self.assertEqual(1, replay.pending_count)
        self.assertEqual(2, replay.active_count)
        # A paced case isolates a free target slot while another lane's request waits.
        replay = LaneReplay(workload(arrival_mode='paced', interval_ns=1, max_queue_requests=1), 2, 0)
        self.assertEqual([event('dispatch', 0, 0, 2)], replay.advance(0))
        self.assertEqual([event('dispatch', 1, 1, 2)], replay.advance(1))
        replay.complete(1, 1, 2)
        self.assertEqual([], replay.advance(2))  # Index 2 waits for busy slot 0.
        self.assertEqual(1, replay.pending_count)
        self.assertEqual([event('dispatch', 3, 3, 2)], replay.advance(3))
        self.assertEqual(1, replay.pending_count)
        self.assertEqual(2, replay.active_count)

    def test_active_slots_need_no_waiting_capacity_and_eight_lanes_are_supported(self):
        replay = LaneReplay(workload(request_count=8, max_queue_requests=1,
                                     concurrency_modes=(8,)), 8, 20)
        self.assertEqual([event('dispatch', i, 20, 8) for i in range(8)], replay.advance(20))
        self.assertEqual(8, replay.active_count)
        self.assertEqual(0, replay.pending_count)
        self.assertIsNone(replay.next_arrival_ns)
        for index in range(8):
            replay.complete(index, index, 21)
        self.assertTrue(replay.done)

    def test_fixed_lane_affinity_prevents_idle_slot_stealing_and_preserves_lane_fifo(self):
        replay = LaneReplay(workload(max_queue_requests=8), 2, 0)
        replay.advance(0)
        replay.complete(1, 1, 1)
        self.assertEqual([event('dispatch', 3, 1, 2)], replay.advance(1))
        replay.complete(1, 3, 2)
        self.assertEqual([event('dispatch', 5, 2, 2)], replay.advance(2))
        replay.complete(1, 5, 3)
        self.assertEqual([event('dispatch', 7, 3, 2)], replay.advance(3))
        replay.complete(1, 7, 4)
        self.assertEqual([], replay.advance(4))
        self.assertEqual(1, replay.active_count)
        self.assertEqual(3, replay.pending_count)
        replay.complete(0, 0, 5)
        self.assertEqual([event('dispatch', 2, 5, 2)], replay.advance(5))

    def test_queued_dispatch_happens_before_new_offers_and_releases_capacity(self):
        replay = LaneReplay(workload(arrival_mode='burst', interval_ns=10, burst_size=2,
                                    max_queue_requests=1), 1, 0)
        self.assertEqual([event('dispatch', 0, 0)], replay.advance(0))
        replay.complete(0, 0, 10)
        self.assertEqual([event('dispatch', 1, 10), event('queue_full', 3, 10)], replay.advance(10))
        self.assertEqual(1, replay.pending_count)  # Index 2 acquired released capacity.
        replay.complete(0, 1, 11)
        self.assertEqual([event('dispatch', 2, 11)], replay.advance(11))

    def test_queued_deadlines_expire_on_boundary_before_dispatch_and_release_capacity(self):
        replay = LaneReplay(workload(arrival_mode='burst', interval_ns=10, burst_size=2,
                                    max_queue_requests=1, request_deadline_ns=10), 1, 100)
        self.assertEqual([event('dispatch', 0, 100)], replay.advance(100))
        self.assertEqual([], replay.advance(109))
        # The active slot remains busy. Expiry still frees the global queue.
        self.assertEqual([event('deadline', 1, 110), event('queue_full', 3, 110)], replay.advance(110))
        self.assertEqual(1, replay.pending_count)
        self.assertEqual(1, replay.active_count)
        replay.complete(0, 0, 111)  # Active work is retained beyond its deadline.
        self.assertEqual([event('dispatch', 2, 111)], replay.advance(111))

    def test_all_queued_expiry_events_precede_any_queued_dispatch(self):
        replay = LaneReplay(workload(arrival_mode='paced', interval_ns=1,
                                    request_deadline_ns=5), 2, 0)
        replay.advance(0)
        replay.advance(1)
        replay.advance(4)  # Queue 2, 3, 4; active 0 and 1.
        replay.complete(1, 1, 7)
        # Index 2 expires at 7; index 3 remains valid and gets the newly free slot.
        events = replay.advance(7)
        self.assertEqual(event('deadline', 2, 7, 2), events[0])
        self.assertEqual(event('dispatch', 3, 7, 2), events[1])
        self.assertEqual(2, replay.active_count)

    def test_due_arrivals_observed_late_expire_without_fabricated_earlier_dispatch(self):
        replay = LaneReplay(workload(request_count=4, arrival_mode='paced', interval_ns=10,
                                    request_deadline_ns=5), 2, 100)
        self.assertEqual([event('deadline', 0, 115, 2), event('deadline', 1, 115, 2)], replay.advance(115))
        self.assertEqual(0, replay.active_count)
        self.assertEqual(120, replay.next_arrival_ns)
        self.assertEqual([event('dispatch', 2, 122, 2)], replay.advance(122))
        replay.complete(0, 2, 200)
        self.assertEqual([event('deadline', 3, 200, 2)], replay.advance(200))
        self.assertTrue(replay.done)

    def test_no_deadline_keeps_waiting_and_inflight_requests_at_late_observation(self):
        replay = LaneReplay(workload(request_count=4), 1, 0)
        self.assertEqual([event('dispatch', 0, 1000)], replay.advance(1000))
        self.assertEqual([], replay.advance(1000000))
        self.assertEqual(3, replay.pending_count)
        self.assertEqual(1, replay.active_count)
        replay.complete(0, 0, 1000001)
        self.assertEqual([event('dispatch', 1, 1000001)], replay.advance(1000001))

    def test_exact_deadline_expiration_wins_over_newly_free_slot(self):
        replay = LaneReplay(workload(request_count=4, request_deadline_ns=10), 1, 0)
        replay.advance(0)
        replay.complete(0, 0, 10)
        self.assertEqual([event('deadline', i, 10) for i in (1, 2, 3)], replay.advance(10))
        self.assertTrue(replay.done)

    def test_complete_validates_identity_and_duplicate_without_mutating_state_or_clock(self):
        replay = LaneReplay(workload(request_count=4), 2, 100)
        replay.advance(100)
        for slot, index in ((0, 1), (1, 0), (0, 2), (1, 3)):
            with self.subTest(slot=slot, index=index), self.assertRaises(ReplayError):
                replay.complete(slot, index, 1000)
            self.assertEqual(2, replay.active_count)
        replay.complete(0, 0, 101)  # Failed calls did not advance the clock to 1000.
        with self.assertRaises(ReplayError):
            replay.complete(0, 0, 102)
        self.assertEqual([event('dispatch', 2, 101, 2)], replay.advance(101))
        self.assertEqual(2, replay.active_count)
        with self.assertRaises(ReplayError):
            replay.complete(0, 0, 101)

    def test_observations_use_one_nondecreasing_clock_across_advance_and_complete(self):
        replay = LaneReplay(workload(), 1, 100)
        with self.assertRaises(ReplayError):
            replay.advance(99)
        replay.advance(100)
        self.assertEqual([], replay.advance(100))
        replay.complete(0, 0, 110)
        with self.assertRaises(ReplayError):
            replay.advance(109)
        replay.advance(110)
        replay.advance(120)
        with self.assertRaises(ReplayError):
            replay.complete(0, 1, 119)
        replay.complete(0, 1, 120)

    def test_clock_and_identifiers_refuse_bool_float_nonfinite_and_out_of_range(self):
        bad_times = (True, False, 1.0, float('nan'), float('inf'), '100', None, -1, MAX_NS + 1)
        for value in bad_times:
            with self.subTest(value=value):
                with self.assertRaises(ReplayError):
                    LaneReplay(workload(), 1, value)
                replay = LaneReplay(workload(), 1, 0)
                replay.advance(0)
                with self.assertRaises(ReplayError):
                    replay.advance(value)
                with self.assertRaises(ReplayError):
                    replay.complete(0, 0, value)
                self.assertEqual(1, replay.active_count)
        for slot in (True, False, 0.0, -1, 2, None, '0'):
            replay = LaneReplay(workload(), 2, 0)
            replay.advance(0)
            with self.subTest(slot=slot), self.assertRaises(ReplayError):
                replay.complete(slot, 0, 0)
        for index in (True, False, 0.0, -1, 8, None, '0'):
            replay = LaneReplay(workload(), 2, 0)
            replay.advance(0)
            with self.subTest(index=index), self.assertRaises(ReplayError):
                replay.complete(0, index, 0)

    def test_admitted_concurrency_and_validated_v2_recipe_are_required(self):
        for concurrency in (True, 1.0, None, 0, -1, 3, 8, 9):
            with self.subTest(concurrency=concurrency), self.assertRaises(ReplayError):
                LaneReplay(workload(), concurrency, 0)
        mutated = workload()
        mutated['requests'][0]['arrival_offset_ns'] = 1
        for bad in (make_workload(), mutated, {}, None, []):
            with self.subTest(workload=str(bad)[:30]), self.assertRaises(ReplayError):
                LaneReplay(bad, 1, 0)

    def test_absolute_arrival_and_deadline_overflow_are_rejected(self):
        paced = workload(request_count=4, arrival_mode='paced', interval_ns=10)
        with self.assertRaisesRegex(ReplayError, 'epoch plus arrival'):
            LaneReplay(paced, 1, MAX_NS - 29)
        deadlines = workload(request_count=4, request_deadline_ns=10)
        with self.assertRaisesRegex(ReplayError, 'deadline'):
            LaneReplay(deadlines, 1, MAX_NS - 9)
        at_boundary = LaneReplay(deadlines, 1, MAX_NS - 10)
        self.assertEqual([event('deadline', i, MAX_NS) for i in range(4)], at_boundary.advance(MAX_NS))
        self.assertTrue(at_boundary.done)
        exact_arrival = LaneReplay(paced, 1, MAX_NS - 30)
        self.assertEqual(MAX_NS - 30, exact_arrival.next_arrival_ns)

    def test_input_mutation_cannot_change_frozen_replay(self):
        source = workload(request_count=4, arrival_mode='paced', interval_ns=10)
        before = copy.deepcopy(source)
        replay = LaneReplay(source, 1, 100)
        self.assertEqual(before, source)
        source['requests'][1]['arrival_offset_ns'] = 0
        source['max_queue_requests'] = 0
        source['request_deadline_ns'] = 1
        self.assertEqual([event('dispatch', 0, 100)], replay.advance(100))
        self.assertEqual(110, replay.next_arrival_ns)
        self.assertEqual([], replay.advance(110))
        self.assertEqual(1, replay.pending_count)

    def test_deterministic_replays_keep_concurrency_bounded_and_account_for_population(self):
        for concurrency in (1, 2, 4):
            for mode, interval, burst in (('simultaneous', 0, 4), ('paced', 3, 4), ('burst', 9, 4)):
                with self.subTest(concurrency=concurrency, mode=mode):
                    source = workload(request_count=20, arrival_mode=mode, interval_ns=interval,
                                      burst_size=burst, max_queue_requests=2, request_deadline_ns=10)
                    def run():
                        replay = LaneReplay(source, concurrency, 50)
                        retained, active, completed = [], {}, set()
                        now = 50
                        for _ in range(100):
                            for slot, (index, finish) in list(active.items()):
                                if finish <= now:
                                    replay.complete(slot, index, now)
                                    completed.add(index)
                                    del active[slot]
                            for row in replay.advance(now):
                                retained.append(row)
                                self.assertEqual(now, row['observed_ns'])
                                self.assertEqual(row['index'] % concurrency, row['slot'])
                                if row['kind'] == 'dispatch':
                                    self.assertNotIn(row['slot'], active)
                                    active[row['slot']] = (row['index'], now + 7 + row['slot'])
                            self.assertLessEqual(replay.active_count, concurrency)
                            self.assertLessEqual(replay.pending_count, 2)
                            self.assertEqual(len(active), replay.active_count)
                            if replay.done:
                                break
                            now += 2
                        self.assertTrue(replay.done)
                        self.assertEqual(set(range(20)), {row['index'] for row in retained})
                        self.assertEqual(20, len(retained))
                        self.assertEqual(completed, {row['index'] for row in retained if row['kind'] == 'dispatch'})
                        self.assertEqual([], replay.advance(now))
                        return retained
                    self.assertEqual(run(), run())


if __name__ == '__main__':
    unittest.main()
