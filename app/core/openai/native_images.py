"""Convert native Codex Images results to the proxy's internal event contract."""

from uuid import uuid4

from app.core.openai.images import V1ImageResponse
from app.core.types import JsonValue
from app.core.utils.sse import format_sse_event


def native_image_response_events(value: JsonValue, *, host_model: str) -> list[str]:
    result = V1ImageResponse.model_validate(value)
    if len(result.data) != 1 or not result.data[0].b64_json:
        raise ValueError("Native image endpoint must return exactly one non-empty image")
    response_id = f"resp_{uuid4().hex}"
    item: dict[str, JsonValue] = {
        "id": f"ig_{uuid4().hex}",
        "type": "image_generation_call",
        "status": "completed",
        "result": result.data[0].b64_json,
    }
    if isinstance(value, dict):
        for key in ("background", "output_format", "quality", "size"):
            if key in value:
                item[key] = value[key]
    response: dict[str, JsonValue] = {
        "id": response_id,
        "object": "response",
        "created_at": result.created,
        "model": host_model,
        "status": "completed",
        "output": [item],
    }
    if result.usage is not None:
        response["tool_usage"] = {"image_gen": result.usage.model_dump(mode="json", exclude_none=True)}
    events: list[dict[str, JsonValue]] = [
        {"type": "response.output_item.done", "output_index": 0, "item": item},
        {"type": "response.completed", "response": response},
    ]
    return [format_sse_event(event) for event in events]
