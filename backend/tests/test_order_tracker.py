import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- TODO: add test functions below this line ---
#

def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")
    
    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()

def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

def test_get_order_by_id_returns_existing_order(order_tracker, mock_storage):
    """Tests fetching an existing order by its ID."""
    expected = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.get_order.return_value = expected

    result = order_tracker.get_order_by_id("ORD001")

    assert result == expected
    mock_storage.get_order.assert_called_once_with("ORD001")


def test_get_order_by_id_raises_error_if_not_found(order_tracker, mock_storage):
    """Tests that fetching a non-existent order raises a ValueError."""
    # mock_storage.get_order returns None by default (no order found)
    with pytest.raises(ValueError, match="Order with ID 'ORD_MISSING' not found."):
        order_tracker.get_order_by_id("ORD_MISSING")


def test_update_order_status_successfully(order_tracker, mock_storage):
    """Tests changing an order's status from 'pending' to 'shipped'."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }

    order_tracker.update_order_status("ORD001", "shipped")

    mock_storage.save_order.assert_called_once()
    saved_id, saved_order = mock_storage.save_order.call_args[0]
    assert saved_id == "ORD001"
    assert saved_order["status"] == "shipped"


def test_update_order_status_raises_error_if_not_found(order_tracker, mock_storage):
    """Tests that updating a non-existent order raises a ValueError."""
    # mock_storage.get_order returns None by default (no order found)
    with pytest.raises(ValueError, match="Order with ID 'ORD_MISSING' not found."):
        order_tracker.update_order_status("ORD_MISSING", "shipped")

    mock_storage.save_order.assert_not_called()


def test_list_all_orders_returns_all_orders(order_tracker, mock_storage):
    """Tests listing all current orders."""
    order1 = {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1,
              "customer_id": "CUST001", "status": "pending"}
    order2 = {"order_id": "ORD002", "item_name": "Mouse", "quantity": 2,
              "customer_id": "CUST002", "status": "shipped"}
    mock_storage.get_all_orders.return_value = {"ORD001": order1, "ORD002": order2}

    result = order_tracker.list_all_orders()

    assert len(result) == 2
    assert order1 in result
    assert order2 in result


def test_list_all_orders_returns_empty_list_when_no_orders(order_tracker, mock_storage):
    """Tests that listing orders with an empty storage returns an empty list."""
    # mock_storage.get_all_orders returns {} by default
    assert order_tracker.list_all_orders() == []
