"""Tests for BSM1 simulation engine."""

import pytest

from app.config import (
    COD_DEFAULT,
    IWA_SS_REF,
    IWA_SS_TSS,
    OUR_REF_O1,
    OUR_REF_O2,
    OUR_REF_O3,
    TKN_DEFAULT,
)
from app.engine import (
    decompose_influent,
    do_to_kla,
    error_pct,
    pre_check,
    srt_to_was,
    validate_components,
    validate_value,
)
from app.models import PlantParameters


class TestValidateValue:
    def test_exact_match(self):
        assert validate_value(10.415, 10.415) is True

    def test_within_tolerance(self):
        # 5% of 10.415 = 0.52075 -> 10.935 should pass
        assert validate_value(10.9, 10.415, tolerance=0.05) is True

    def test_outside_tolerance(self):
        assert validate_value(11.5, 10.415, tolerance=0.05) is False

    def test_zero_reference(self):
        assert validate_value(0.005, 0.0) is True
        assert validate_value(0.02, 0.0) is False

    def test_negative_error(self):
        # Below reference but within tolerance
        assert validate_value(9.9, 10.415, tolerance=0.05) is True


class TestErrorPct:
    def test_exact(self):
        assert error_pct(10.415, 10.415) == 0.0

    def test_positive(self):
        result = error_pct(11.0, 10.0)
        assert abs(result - 10.0) < 0.001

    def test_negative(self):
        result = error_pct(9.0, 10.0)
        assert abs(result - (-10.0)) < 0.001

    def test_zero_reference(self):
        assert error_pct(5.0, 0.0) == 0.0


class TestValidateComponents:
    def test_iwa_reference_validates_itself(self):
        """IWA reference values should all pass when validated against themselves."""
        values = {**IWA_SS_REF, 'TSS': IWA_SS_TSS}
        results = validate_components(values)
        assert len(results) == 14
        assert all(r.passed for r in results)

    def test_unknown_component_ignored(self):
        results = validate_components({'UNKNOWN': 99.9})
        assert len(results) == 0

    def test_partial_validation(self):
        results = validate_components({'S_NH': 1.733, 'S_NO': 10.415})
        assert len(results) == 2
        assert all(r.passed for r in results)

    def test_failing_component(self):
        results = validate_components({'S_NH': 5.0})  # way off from 1.733
        assert len(results) == 1
        assert results[0].passed is False


class TestDecomposeInfluent:
    def test_default_roundtrip(self):
        """Default aggregates should produce BSM1 default component concentrations."""
        result = decompose_influent(COD_DEFAULT, TKN_DEFAULT, 211.27)
        conc = result['concentrations']
        assert abs(conc['S_I'] - 30.0) < 0.01
        assert abs(conc['S_S'] - 69.5) < 0.01
        assert abs(conc['X_I'] - 51.2) < 0.01
        assert abs(conc['X_S'] - 202.32) < 0.01
        assert abs(conc['X_BH'] - 28.17) < 0.01
        assert abs(conc['S_NH'] - 31.56) < 0.01
        assert abs(conc['S_ND'] - 6.95) < 0.01
        assert abs(conc['X_ND'] - 10.59) < 0.01
        assert conc['S_ALK'] == 84

    def test_double_cod_doubles_components(self):
        result = decompose_influent(COD_DEFAULT * 2, TKN_DEFAULT, 211.27)
        conc = result['concentrations']
        assert abs(conc['S_I'] - 60.0) < 0.01
        assert abs(conc['S_S'] - 139.0) < 0.01

    def test_alk_stays_constant(self):
        result = decompose_influent(COD_DEFAULT * 3, TKN_DEFAULT * 2, 500)
        assert result['concentrations']['S_ALK'] == 84

    def test_units_format(self):
        result = decompose_influent(COD_DEFAULT, TKN_DEFAULT, 211.27)
        assert result['units'] == ('m3/d', 'mg/L')


class TestSrtToWas:
    def test_default_srt_gives_default_was(self):
        assert abs(srt_to_was(9.14) - 385) < 1.0

    def test_higher_srt_gives_lower_was(self):
        assert srt_to_was(18.28) < 385

    def test_lower_srt_gives_higher_was(self):
        assert srt_to_was(4.57) > 385


class TestPreCheck:
    def test_defaults_no_warnings(self):
        plant = PlantParameters()
        result = pre_check(plant)
        assert result.valid is True
        assert len(result.warnings) == 0

    def test_srt_mode_calculates_was(self):
        plant = PlantParameters(sludge_control='SRT', SRT_target=9.14, Q_WAS=None)
        result = pre_check(plant)
        assert result.Q_WAS_calculated is not None
        assert abs(result.Q_WAS_calculated - 385) < 2.0

    def test_low_hrt_warning(self):
        plant = PlantParameters(Q=200000, V_anoxic=100, V_aerobic=100)
        result = pre_check(plant)
        assert any('HRT' in w for w in result.warnings)

    def test_no_aeration_warning(self):
        # DO near DOsat means KLa ~0 (no effective aeration)
        # DO max is 7.0 in model, DOsat min is 6.0 — use DOsat=7.5 to get close
        plant = PlantParameters(DO_O1=7.0, DO_O2=7.0, DO_O3=7.0, DOsat=7.5)
        result = pre_check(plant)
        assert any('aireacion' in w.lower() or 'saturacion' in w.lower() for w in result.warnings)

    def test_high_ras_ratio_warning(self):
        plant = PlantParameters(Q_RAS=100000)
        result = pre_check(plant)
        assert any('RAS' in w for w in result.warnings)


class TestDoToKla:
    def test_reference_do_gives_reference_kla_o1(self):
        """DO=1.7174 with DOsat=8 should give KLa~240."""
        kla = do_to_kla(1.7174, 8.0, OUR_REF_O1)
        assert abs(kla - 240) < 1.0

    def test_reference_do_gives_reference_kla_o3(self):
        """DO=0.4902 with DOsat=8 should give KLa~84."""
        kla = do_to_kla(0.4902, 8.0, OUR_REF_O3)
        assert abs(kla - 84) < 1.0

    def test_do_at_dosat_gives_zero(self):
        """DO >= DOsat means no driving force -> KLa=0."""
        assert do_to_kla(8.0, 8.0, OUR_REF_O1) == 0.0
        assert do_to_kla(9.0, 8.0, OUR_REF_O1) == 0.0

    def test_higher_do_gives_higher_kla(self):
        """Higher DO setpoint requires more KLa (smaller driving force)."""
        kla_do1 = do_to_kla(1.0, 8.0, OUR_REF_O1)
        kla_do3 = do_to_kla(3.0, 8.0, OUR_REF_O1)
        assert kla_do3 > kla_do1  # smaller (DOsat-DO) -> needs higher KLa

    def test_higher_dosat_gives_lower_kla(self):
        """Higher DOsat increases driving force, so less KLa needed."""
        kla_8 = do_to_kla(2.0, 8.0, OUR_REF_O2)
        kla_10 = do_to_kla(2.0, 10.0, OUR_REF_O2)
        assert kla_10 < kla_8


class TestPreCheckKlaOutput:
    def test_precheck_returns_kla_values(self):
        """Pre-check should return calculated KLa for transparency."""
        plant = PlantParameters()
        result = pre_check(plant)
        assert result.KLa_O1 is not None
        assert result.KLa_O2 is not None
        assert result.KLa_O3 is not None
        # Default DO values should give approximately BSM1 reference KLa
        assert abs(result.KLa_O1 - 240) < 5
        assert abs(result.KLa_O2 - 240) < 5
        assert abs(result.KLa_O3 - 84) < 5


class TestFullSimulation:
    """Integration test - runs actual QSDsan simulation (~3-5 seconds)."""

    @pytest.mark.slow
    def test_steady_state_14_of_14_pass(self):
        from app.engine import run_steady_state_simulation

        result = run_steady_state_simulation(t_days=200, method='BDF')

        assert result.total_count == 14
        assert result.pass_count == 14
        assert result.all_passed is True
        assert result.method_used in ('BDF', 'Radau')
        assert result.compute_time_seconds > 0
        assert result.aggregates['COD_total'] < 100
        assert result.aggregates['TSS'] < 30
