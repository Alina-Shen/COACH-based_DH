"""Adversarial scientific-contract and filesystem-boundary regressions; no chemistry."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
module=importlib.util.spec_from_file_location('coach_spec_validator',ROOT/'scripts/validate_scientific_spec.py')
v=importlib.util.module_from_spec(module);module.loader.exec_module(v)

class ScientificContractTests(unittest.TestCase):
    def setUp(self): self.spec=v.read(v.SPEC)

    def reject(self,path,value,expected):
        data=copy.deepcopy(self.spec);cursor=data
        for key in path[:-1]:cursor=cursor[key]
        cursor[path[-1]]=value
        self.assertFalse(v.semantic_checks(data)[expected],path)

    def test_complete_contract_passes(self):
        self.assertTrue(all(x is True for x in v.semantic_checks(self.spec).values()))

    def test_each_omega_location_must_be_027(self):
        for path,value in [(['energy','omega','value_bohr_inverse'],.3),
            (['semilocal','exchange','omega_bohr_inverse'],.3),
            (['qchem_feature_contract','OMEGA'],300),(['qchem_feature_contract','OMEGA2'],300)]:
            with self.subTest(path=path):self.reject(path,value,'omega_consistency')

    def test_parent_contamination(self):
        self.reject(['parent','method'],'omegaB97M-V','COACH_source')
        self.reject(['parent','new_scf_cycles'],50,'no_orbital_updates')
        self.reject(['parent','same_archive_all_orbital_dependent_terms'],False,'no_orbital_updates')

    def test_reference_layout_cannot_silently_replace_COACH(self):
        self.reject(['feature_layout','selected_integrated_dv_rows'],[64,153,166],'292_layout')
        self.reject(['feature_layout','pt2'],291,'292_layout')
        self.reject(['semilocal','same_spin_correlation','variables','u','gamma'],.2,'semilocal_same_spin_correlation')

    def test_fixed_partition_and_dispersion(self):
        self.reject(['energy','fixed_terms'],['nuclear_repulsion'],'fixed_energy')
        self.reject(['energy','vv10','b'],10.,'VV10')
        self.reject(['energy','d4_atm','parameters','s6'],1.,'pure_ATM')

    def test_PT2_model_and_frozen_core(self):
        self.reject(['energy','pt2','independent_spin_coefficients'],True,'total_PT2')
        self.reject(['energy','pt2','frozen_core'],False,'total_PT2')
        self.reject(['energy','pt2','denominator_regularization'],.1,'total_PT2')

    def test_mandatory_slot_is_not_nonzero_HF_requirement(self):
        self.reject(['constraints','mandatory_SRHF_can_be_zero'],False,'C0_support')
        self.reject(['constraints','support_constraint'],'sum(z)==K','C0_support')
        self.reject(['constraints','cross_scalar_equalities'],['VV10+PT2=1'],'C0_UEG_and_independent_scalars')

    def test_grid_selection_and_acceptance(self):
        self.reject(['grids','selection','additional_remaining_l1'],0,'remaining_row_selection')
        self.reject(['grids','pass2_constraints'],'all_rows','grid_acceptance')
        self.reject(['grids','internal_safety_factor'],1.,'grid_limits')

    def test_holdout_leakage(self):
        self.reject(['data_roles','final_assessment','may_change_model'],True,'final_roles')
        self.reject(['selection','protected_from_selection'],['SC74'],'final_roles')
        self.reject(['data_policy','random_point_split'],True,'no_leakage_or_silent_shrink')

    def test_old_optimizer_and_campaign_rejected(self):
        self.reject(['optimization','objective_representation'],'explicit_weighted_residuals','objective')
        self.reject(['optimization','ridge'],0.,'objective')
        self.reject(['optimization','budgets'],[14,24,32,40,48,64,80],'campaign')
        self.reject(['optimization','starts','noise_clip_or_project'],True,'noise_mapping')

    def test_future_scan_and_runtime_not_enabled(self):
        self.reject(['future_options','omega_scan','enabled'],True,'future_omega_disabled')
        self.reject(['validation','runtime_ready'],True,'no_transferred_runtime_pass')
        self.reject(['validation','native_COACH_gates_passed'],True,'no_transferred_runtime_pass')

    def test_wrong_roots_and_escapes(self):
        self.reject(['storage','heavy_root'],str(ROOT.parent/'revwb97m2'),'three_write_roots')
        for path in [ROOT.parent/'revwb97m2/results/forbidden.json',str(ROOT)+'_other/out.json',ROOT/'../bad.json']:
            with self.subTest(path=str(path)),self.assertRaises(ValueError):v.confined(path)
        self.assertEqual(v.confined(ROOT/'results/future.json'),ROOT/'results/future.json')

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tests') as directory:
            p=Path(directory)/'escape';p.symlink_to(ROOT.parent/'revwb97m2',target_is_directory=True)
            with self.assertRaises(ValueError):v.confined(p/'results/forbidden.json')

    def test_content_hash_tampering_and_empty_lock(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tests') as directory:
            p=Path(directory)/'artifact.json';p.write_text('{}\n');lock={p.name:v.digest(p)}
            self.assertTrue(v.verify_hashes(lock,Path(directory)))
            p.write_text('{"changed":true}\n')
            self.assertFalse(v.verify_hashes(lock,Path(directory)))
            self.assertFalse(v.verify_hashes({},Path(directory)))

    def test_ambiguous_and_nonfinite_JSON(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tests') as directory:
            p=Path(directory)/'bad.json'
            for text in ['{"omega":0.27,"omega":0.3}','{"omega":NaN}','{"omega":Infinity}']:
                p.write_text(text)
                with self.assertRaises(ValueError):v.read(p)
        self.reject(['energy','omega','value_bohr_inverse'],float('nan'),'finite_numbers')

    def test_missing_required_sections_fail_closed(self):
        del self.spec['energy']
        self.assertFalse(v.semantic_checks(self.spec)['schema_shape'])

    def test_pre_freeze_sources_and_index(self):
        self.assertTrue(v.validate(require_freeze=False)['passed'])

if __name__=='__main__':unittest.main()
