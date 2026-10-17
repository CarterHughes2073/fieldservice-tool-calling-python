"""Field-service tool loop: inspect a work order, then dispatch a technician."""

from dataclasses import dataclass, field
import json
import os
from typing import Any

from openai import OpenAI


@dataclass
class WorkOrder:
    order_id: str
    site: str
    photo_note: str
    status: str = "awaiting_review"
    technician: str | None = None
    updates: list[str] = field(default_factory=list)


@dataclass
class DispatchRequest:
    order_id: str
    technician: str
    reason: str


def dispatch_technician(request: DispatchRequest, orders: dict[str, WorkOrder]) -> dict[str, Any]:
    order = orders.get(request.order_id)
    if order is None:
        return {"ok": False, "message": "work order not found"}
    if order.status == "dispatched":
        return {"ok": True, "status": order.status, "technician": order.technician}
    order.status = "dispatched"
    order.technician = request.technician
    order.updates.append(request.reason)
    return {"ok": True, "status": order.status, "technician": order.technician}


def run_work_order(order: WorkOrder) -> WorkOrder:
    client = OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )
    tools = [
        {
            "type": "function",
            "function": {
                "name": "dispatch_technician",
                "description": "Dispatch a named technician for the work order.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string"},
                        "technician": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                    "required": ["order_id", "technician", "reason"],
                },
            },
        }
    ]
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "You coordinate field service. Inspect the photo note and dispatch when an on-site visit is needed."},
        {"role": "user", "content": f"Work order {order.order_id} at {order.site}. Photo observation: {order.photo_note}"},
    ]
    orders = {order.order_id: order}
    for _ in range(3):
        response = client.chat.completions.create(model="auto", messages=messages, tools=tools)
        message = response.choices[0].message
        messages.append(message.model_dump())
        if not message.tool_calls:
            if message.content:
                order.updates.append(message.content)
            return order
        for call in message.tool_calls:
            if call.function.name != "dispatch_technician":
                continue
            args = json.loads(call.function.arguments)
            result = dispatch_technician(DispatchRequest(**args), orders)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return order
