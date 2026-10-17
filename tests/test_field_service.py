from src.field_service import DispatchRequest, WorkOrder, dispatch_technician


def test_dispatch_changes_work_order_state_and_is_repeatable():
    order = WorkOrder("WO-1", "Depot", "Loose conduit near the motor")
    orders = {order.order_id: order}
    request = DispatchRequest("WO-1", "Mina", "Photo shows a safety hazard")

    first = dispatch_technician(request, orders)
    second = dispatch_technician(request, orders)

    assert first == {"ok": True, "status": "dispatched", "technician": "Mina"}
    assert second == first
    assert order.updates == ["Photo shows a safety hazard"]
