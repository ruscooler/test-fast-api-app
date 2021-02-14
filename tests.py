import pytest
from fastapi.testclient import TestClient

from main import app
from helpers import TAXES, DISCOUNTS

client = TestClient(app)


@pytest.mark.parametrize("params", [
    {'count': 12, 'price': 123.43, 'state_code': 'TX'},
])
def test_success(params):
    response = client.get("/get_order_cost", params=params)
    assert response.status_code == 200
    assert list(response.json().keys()) == ['subtotal', 'tax', 'total']


@pytest.mark.parametrize("params", [
    {'count': 12, 'price': 123.43, 'state_code': 'TX'},
])
def test_without_necessary_param(params):
    for key in params.keys():
        payload = params.copy()
        payload.pop(key, None)
        response = client.get("/get_order_cost", params=payload)
        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == 'field required'


@pytest.mark.parametrize("params", [
    {'count': 0, 'price': 223.42, 'state_code': 'NV'},
    {'count': 1234, 'price': 0, 'state_code': 'NV'},
])
def test_zero_values(params):
    response = client.get("/get_order_cost", params=params)
    assert response.status_code == 200
    for field in ['subtotal', 'tax', 'total']:
        assert response.json()[field] == 0


@pytest.mark.parametrize("params", [
    {'count': -190, 'price': 10.42, 'state_code': 'NV'},
    {'count': 1234, 'price': -102.45, 'state_code': 'NV'},
])
def test_negative_values(params):
    response = client.get("/get_order_cost", params=params)
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == 'ensure this value is greater than or equal to 0'


@pytest.mark.parametrize("params", [
    {'count': 190, 'price': 14.99, 'state_code': 'RU'},
])
def test_wrong_state_code(params):
    response = client.get("/get_order_cost", params=params)
    assert response.status_code == 400
    assert response.json()['detail'] == 'State code not found'


@pytest.mark.parametrize("params", [
    {'count': 1000, 'price': 5, 'state_code': 'TX'},
    {'count': 2000, 'price': 25, 'state_code': 'TX'},
    {'count': 350, 'price': 20, 'state_code': 'TX'},
])
def test_calculate_discount(params):
    total = params['count'] * params['price']
    response = client.get("/get_order_cost", params=params)
    assert response.status_code == 200
    assert list(response.json().keys()) == ['subtotal', 'tax', 'total']
    assert (total - response.json()['subtotal']) / total == DISCOUNTS[total]


@pytest.mark.parametrize("params", [
    {'count': 1000, 'price': 5, 'state_code': 'UT'},
    {'count': 2000, 'price': 25, 'state_code': 'NV'},
    {'count': 350, 'price': 20, 'state_code': 'TX'},
    {'count': 1, 'price': 100, 'state_code': 'AL'},
    {'count': 223, 'price': 12.45, 'state_code': 'CA'},
])
def test_calculate_tax(params):
    response = client.get("/get_order_cost", params=params)
    assert response.status_code == 200
    assert list(response.json().keys()) == ['subtotal', 'tax', 'total']
    subtotal, tax = response.json()['subtotal'], response.json()['tax']
    tax_value = round(1 - (subtotal - tax) / subtotal, 4)
    assert tax_value == TAXES[params['state_code']]
