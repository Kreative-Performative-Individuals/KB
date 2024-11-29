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

def test_post_kpi():
    url = "http://localhost:8000/add_kpi/" 

    data = {
    "superclass": "downtime_kpi",
    "label": "mean_time_between_failures",
    "description": "Mean time between failures cumulative over machine-operation pairs",
    "unit_of_measure": "s",
    "parsable_computation_formula": "A°sum°mo[S°/[ R°bad_cycles_sum°T°m°o° ; R°time_sum°T°m°o° ]]",
    "human_readable_formula": "sum_M_O(bad_cycles_sum(T,m,o)/time_sum(T,m,o))",
    "depends_on_machine": True,
    "depends_on_operation": True
    }   
    
    response = requests.post(url, json=data)

    assert response.status_code == 200
