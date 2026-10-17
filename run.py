import json

from src.field_service import WorkOrder, run_work_order


if __name__ == "__main__":
    work_order = WorkOrder(
        order_id="WO-1042",
        site="North pump station",
        photo_note="Water is pooling below a cracked intake flange; the pump is offline.",
    )
    result = run_work_order(work_order)
    print(json.dumps(result.__dict__, indent=2))
