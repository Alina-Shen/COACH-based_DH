import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from revwb97m2.scripts import full_training_feeder_v1 as f


class FeederTests(unittest.TestCase):
    def test_expanded_arrays_count_individually(self):
        rows = f.queue_rows('12_0|RUNNING|ours|cm1\n12_1|PENDING|ours|cm1\n13|RUNNING|unrelated|mhg\n')
        self.assertEqual(f.room(rows, []), 995)

    def test_compressed_arrays_rejected(self):
        with self.assertRaises(RuntimeError):
            f.queue_rows('12_[0-999]|PENDING|ours|cm1')

    def test_duplicate_queue_rejected(self):
        with self.assertRaises(RuntimeError):
            f.queue_rows('12|RUNNING|a|cm1\n12|RUNNING|a|cm1')

    def test_unknown_queue_state_rejected(self):
        with self.assertRaises(RuntimeError):
            f.queue_rows('12|WHAT|a|cm1')

    def test_exact_cap(self):
        self.assertEqual(f.room({str(i): {} for i in range(998)}, []), 0)
        self.assertEqual(f.room({str(i): {} for i in range(997)}, []), 1)

    def test_invisible_tasks_reserve_capacity(self):
        jobs = [dict(job_id='1', indices=[0, 1, 2], completed=[2])]
        self.assertEqual(f.room({'1_0': {}}, jobs), 996)

    def test_never_resubmit_completed_indices(self):
        self.assertEqual(f.remaining(dict(name='a', species=3),
                                     [dict(record='a', indices=[0, 2], completed=[0, 2])]), [1])

    def test_gateway_blocks_and_then_opens(self):
        gateway = dict(name='ecp21_gateway', species=21, memory_gib=14)
        ordinary = dict(name='ordinary', species=23, memory_gib=227)
        campaign = dict(records=[ordinary, gateway])
        self.assertEqual(f.eligible_records(campaign, {'jobs': []}), [gateway])
        self.assertEqual(f.eligible_records(campaign, {'jobs': [dict(record='ecp21_gateway', completed=list(range(21)))]}), [ordinary])

    def fixture(self):
        campaign = dict(active_limit=998, launcher='/launcher', job_prefix='test_', records=[])
        record = dict(name='ecp21_gateway', species=21, cpus=8, memory_gib=14, wall_hours=72,
                      plan='/plan', releases={'cm1': {'path': '/release'}})
        return campaign, record, dict(jobs=[], intent=None)

    def test_resources_unchanged_no_requeue(self):
        c, r, _ = self.fixture()
        args = f.sbatch_args(c, r, 'cm1', [0, 2], 0)
        for value in ('--mem=14G', '--cpus-per-task=8', '--time=72:00:00', '--array=0,2', '--no-requeue'):
            self.assertIn(value, args)

    def test_forbidden_route(self):
        c, r, _ = self.fixture()
        with self.assertRaises(RuntimeError):
            f.sbatch_args(c, r, 'lr_lowprio', [0], 0)

    def test_intent_durable_before_sbatch_uncertain_response(self):
        c, r, state = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'state.json'
            def ambiguous(argv):
                self.assertEqual(f.read(path)['intent']['indices'], [0])
                return 'no job id', ''
            with patch.object(f, 'queue', return_value={}), patch.object(f, 'command', side_effect=ambiguous):
                with self.assertRaises(RuntimeError):
                    f.submit(c, state, path, r, 'cm1', [0], {})
            self.assertIsNotNone(f.read(path)['intent'])
            self.assertEqual(state['jobs'], [])

    def test_success_persists_id_and_clears_intent(self):
        c, r, state = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'state.json'
            with patch.object(f, 'queue', return_value={}), patch.object(f, 'command', return_value=('123;cluster\n', '')):
                f.submit(c, state, path, r, 'cm1', [0], {})
            self.assertEqual(f.read(path)['jobs'][0]['job_id'], '123')
            self.assertIsNone(f.read(path)['intent'])

    def test_fresh_queue_prevents_overflow(self):
        c, r, state = self.fixture()
        with tempfile.TemporaryDirectory() as directory, patch.object(f, 'queue', return_value={str(i): {} for i in range(998)}), patch.object(f, 'command') as command:
            with self.assertRaises(RuntimeError):
                f.submit(c, state, Path(directory) / 'state.json', r, 'cm1', [0], {})
            command.assert_not_called()

    def test_stop_file_prevents_submission(self):
        c, r, state = self.fixture()
        with tempfile.TemporaryDirectory() as directory, patch.object(f, 'queue') as queue:
            (Path(directory) / 'STOP').touch()
            with self.assertRaises(RuntimeError):
                f.submit(c, state, Path(directory) / 'state.json', r, 'cm1', [0], {})
            queue.assert_not_called()

    def test_accounting_failure_halts(self):
        c, r, state = self.fixture()
        c['records'] = [r]
        state['jobs'] = [dict(record=r['name'], job_id='123', indices=[0], completed=[], submitted_epoch=0)]
        with patch.object(f, 'command', return_value=('123_0|OUT_OF_MEMORY|0:125\n', '')):
            with self.assertRaisesRegex(RuntimeError, 'OUT_OF_MEMORY'):
                f.reconcile(c, state, {})

    def test_accounting_lag_does_not_complete(self):
        c, r, state = self.fixture()
        c['records'] = [r]
        state['jobs'] = [dict(record=r['name'], job_id='123', indices=[0], completed=[], submitted_epoch=f.time.time())]
        with patch.object(f, 'command', return_value=('', '')):
            f.reconcile(c, state, {})
        self.assertEqual(state['jobs'][0]['completed'], [])

    def test_completed_requires_publication_audit(self):
        c, r, state = self.fixture()
        c['records'] = [r]
        state['jobs'] = [dict(record=r['name'], job_id='123', indices=[0], completed=[], submitted_epoch=0)]
        with patch.object(f, 'command', return_value=('123_0|COMPLETED|0:0\n', '')), patch.object(f, 'publication') as validate:
            f.reconcile(c, state, {})
        validate.assert_called_once_with(r, 0)
        self.assertEqual(state['jobs'][0]['completed'], [0])


if __name__ == '__main__':
    unittest.main()
