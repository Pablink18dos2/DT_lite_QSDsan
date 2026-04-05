"""Tests for BSM1 simulator FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert 'qsdsan_version' in data
        assert 'python_version' in data


class TestReferenceEndpoint:
    def test_iwa_reference_returns_all_keys(self):
        response = client.get('/reference/iwa')
        assert response.status_code == 200
        data = response.json()
        assert 'steady_state' in data
        assert len(data['steady_state']) == 13
        assert 'S_NH' in data['steady_state']
        assert data['steady_state_tss'] == 12.497
        assert data['tolerance'] == 0.05

    def test_iwa_limits_present(self):
        response = client.get('/reference/iwa')
        data = response.json()
        assert data['limits']['COD'] == 100
        assert data['limits']['TN'] == 18


class TestLatestResults:
    def test_no_results_returns_404(self):
        # Reset latest result
        import app.main as main_module

        main_module._latest_result = None

        response = client.get('/results/latest')
        assert response.status_code == 404


class TestValidateEndpoint:
    def test_validate_iwa_values(self):
        response = client.post(
            '/validate',
            json={
                'values': {'S_NH': 1.733, 'S_NO': 10.415, 'TSS': 12.497},
                'tolerance': 0.05,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(item['passed'] for item in data)

    def test_validate_empty_values(self):
        response = client.post(
            '/validate',
            json={
                'values': {},
                'tolerance': 0.05,
            },
        )
        assert response.status_code == 400

    def test_validate_unknown_components(self):
        response = client.post(
            '/validate',
            json={
                'values': {'FAKE': 99.9},
                'tolerance': 0.05,
            },
        )
        assert response.status_code == 400

    def test_validate_failing_value(self):
        response = client.post(
            '/validate',
            json={
                'values': {'S_NH': 5.0},
                'tolerance': 0.05,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['passed'] is False


class TestPlantDefaultsEndpoint:
    def test_defaults_returns_200(self):
        response = client.get('/defaults/plant')
        assert response.status_code == 200
        data = response.json()
        assert 'Q' in data
        assert 'COD_total' in data
        assert data['Q']['value'] == 18446
        assert data['Q']['min'] == 1000

    def test_defaults_has_all_params(self):
        response = client.get('/defaults/plant')
        data = response.json()
        expected = [
            'Q',
            'COD_total',
            'TKN',
            'TSS_inf',
            'V_anoxic',
            'V_aerobic',
            'Clarifier_area',
            'Clarifier_height',
            'Q_RAS',
            'Q_WAS',
            'SRT_target',
            'Temperature',
            'DO_O1',
            'DO_O2',
            'DO_O3',
            'DOsat',
            'Q_intr',
        ]
        for k in expected:
            assert k in data, f'Missing key: {k}'


class TestPreCheckEndpoint:
    def test_precheck_defaults(self):
        response = client.post('/simulate/pre-check')
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is True

    def test_precheck_srt_mode(self):
        response = client.post(
            '/simulate/pre-check',
            json={
                'sludge_control': 'SRT',
                'SRT_target': 9.14,
                'Q_WAS': None,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data['Q_WAS_calculated'] is not None

    def test_precheck_extreme_params_warns(self):
        response = client.post(
            '/simulate/pre-check',
            json={
                'Q': 200000,
                'V_anoxic': 100,
                'V_aerobic': 100,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data['warnings']) > 0


class TestSimulationEndpoint:
    """Integration tests that run actual simulations (~3-5 seconds each)."""

    @pytest.mark.slow
    def test_simulate_default_params(self):
        response = client.post('/simulate/steady-state')
        assert response.status_code == 200
        data = response.json()
        assert data['total_count'] == 14
        assert data['pass_count'] == 14
        assert data['all_passed'] is True

    @pytest.mark.slow
    def test_latest_results_after_simulation(self):
        # Run simulation first
        client.post('/simulate/steady-state')
        # Now latest should return 200
        response = client.get('/results/latest')
        assert response.status_code == 200
        data = response.json()
        assert data['total_count'] == 14
