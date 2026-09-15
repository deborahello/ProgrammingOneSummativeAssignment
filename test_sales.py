import pytest
import pandas as pd
from decimal import Decimal
from sales import Sales

# We inject 'mocker' directly into our fixtures
@pytest.fixture
def mock_product(mocker):
    """Creates a fake product to use in tests."""
    mock = mocker.MagicMock()
    mock.product_id = 1
    mock.product_name = "Test Item"
    mock.price = Decimal("10.00")
    return mock

@pytest.fixture
def mock_inventory(mocker, mock_product):
    """Creates a fake inventory that always has our mock product."""
    inventory = mocker.MagicMock()
    inventory.find_product.return_value = mock_product
    inventory.check_stock.return_value = True  # Always in stock by default
    return inventory

@pytest.fixture
def sales_app(mocker, mock_inventory):
    """Initializes the Sales class with the mocked inventory and product."""
    # mocker.patch handles the cleanup automatically after the test finishes
    mock_product_class = mocker.patch('sales.Product')
    mock_product_class.validate_quantity.side_effect = lambda q: q  
    
    return Sales(inventory=mock_inventory)

# --- The tests below remain exactly the same! ---

def test_add_item_success(sales_app, mock_product):
    item = sales_app.add_item(product_id=1, quantity=2)

    assert len(sales_app.current_sale) == 1
    assert item["product_id"] == mock_product.product_id
    assert item["quantity"] == 2
    assert item["subtotal"] == Decimal("20.00")

def test_calculate_total(sales_app):
    sales_app.add_item(product_id=1, quantity=2) 
    sales_app.add_item(product_id=1, quantity=3) 
    
    total = sales_app.calculate_total()
    assert total == Decimal("50.00")

def test_complete_sale_success(sales_app, mock_inventory):
    sales_app.add_item(product_id=1, quantity=2)
    summary = sales_app.complete_sale()

    assert summary["total"] == Decimal("20.00")
    assert summary["sale_id"] == 1
    assert len(sales_app.current_sale) == 0  
    assert not sales_app.sales_df.empty      
    
    mock_inventory.reduce_stock.assert_called_once_with(1, 2)

def test_add_item_invalid_quantity(sales_app):
    with pytest.raises(ValueError, match="Quantity must be greater than zero."):
        sales_app.add_item(product_id=1, quantity=0)

def test_add_item_not_found(sales_app, mock_inventory):
    mock_inventory.find_product.return_value = None
    
    with pytest.raises(ValueError, match="Product not found."):
        sales_app.add_item(product_id=999, quantity=1)

def test_add_item_insufficient_stock(sales_app, mock_inventory):
    mock_inventory.check_stock.return_value = False
    
    with pytest.raises(ValueError, match="Insufficient stock available."):
        sales_app.add_item(product_id=1, quantity=500)

def test_complete_empty_sale(sales_app):
    with pytest.raises(ValueError, match="There are no items in the current sale."):
        sales_app.complete_sale()

