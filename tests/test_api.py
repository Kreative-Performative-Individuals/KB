import pytest
import requests

BASE_URL = "http://localhost:8000"  

def test_get_kpi():
    params = {"kpi_label": "consumption_sum"}
    response = requests.get(f"{BASE_URL}/get_formulas/", params = params)

    assert response.json()["formula"] == 'A°sum°mo[ A°sum°t[ D°consumption_sum°t°m°o° ] ]'
    params = {"kpi_label": "cost_sum"}
    response = requests.get(f"{BASE_URL}/get_formulas/", params = params)

    assert response.json()["formula"] == 'A°sum°mo[ A°sum°t[ D°cost_sum°t°m°o° ] ]'

    params = {"kpi_label": "consumption_max"}
    response = requests.get(f"{BASE_URL}/get_formulas/", params = params)

    assert response.json()["formula"] == 'A°max°mo[ A°max°t[ D°consumption_max°t°m°o° ] ]'
