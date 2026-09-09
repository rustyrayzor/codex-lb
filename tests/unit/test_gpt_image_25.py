from __future__ import annotations

import pytest

from app.core.openai.exceptions import ClientPayloadError
from app.core.openai.images import (
    V1ImagesEditsForm,
    V1ImagesGenerationsRequest,
    validate_image_request_parameters,
    validate_image_size,
)
from app.core.openai.native_images import native_image_response_events
from app.core.openai.requests import ResponsesRequest
from app.modules.proxy.images_service import (
    images_edit_to_responses_request,
    images_generation_to_responses_request,
)

MODELS = ["gpt-image-2.5-sunburst", "gpt-image-2.5-flare"]


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("quality", ["auto", "low", "medium", "high", "xhigh", "max"])
@pytest.mark.parametrize("output_format", ["png", "webp"])
@pytest.mark.parametrize("is_edit", [False, True])
def test_native_transparency_validation_and_forwarding(
    model: str, quality: str, output_format: str, is_edit: bool
) -> None:
    validate_image_request_parameters(
        model=model,
        quality=quality,
        size="2560x3072",
        background="transparent",
        output_format=output_format,
        moderation="auto",
        input_fidelity=None,
        is_edit=is_edit,
        n=1,
        partial_images=None,
        output_compression=100,
        images_max_partial_images=3,
    )
    options = {
        "model": model,
        "prompt": "a translucent ribbon",
        "size": "2560x3072",
        "quality": quality,
        "background": "transparent",
        "output_format": output_format,
    }
    if is_edit:
        request = images_edit_to_responses_request(
            V1ImagesEditsForm.model_validate(options),
            host_model="gpt-5.6-sol",
            images=[(b"source", "image/png")],
            mask=None,
        )
    else:
        request = images_generation_to_responses_request(
            V1ImagesGenerationsRequest.model_validate(options),
            host_model="gpt-5.6-sol",
        )
    forwarded = request.to_payload()
    assert forwarded["model"] == "gpt-5.6-sol"
    assert isinstance(forwarded["tools"], list)
    tool = forwarded["tools"][0]
    assert isinstance(tool, dict)
    for key in ("model", "quality", "size", "background", "output_format"):
        assert tool[key] == options[key]
        assert request._native_image_request is not None
        assert request._native_image_request.body[key] == options[key]
    assert request.model_copy()._native_image_request == request._native_image_request
    assert "_native_image_request" not in forwarded
    assert request._native_image_request.operation == ("edits" if is_edit else "generations")
    if is_edit:
        assert request._native_image_request.body["images"] == [{"image_url": "data:image/png;base64,c291cmNl"}]


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("size", ["1023x1024", "512x512", "3856x1024", "3328x1024", "2896x2896"])
def test_new_models_keep_custom_size_limits(model: str, size: str) -> None:
    with pytest.raises(ClientPayloadError) as exc:
        validate_image_size(model, size)
    assert exc.value.param == "size"


@pytest.mark.parametrize("model", MODELS)
def test_transparency_rejects_jpeg(model: str) -> None:
    with pytest.raises(ClientPayloadError) as exc:
        validate_image_request_parameters(
            model=model,
            quality="high",
            size="1024x1024",
            background="transparent",
            output_format="jpeg",
            moderation="auto",
            input_fidelity=None,
            is_edit=False,
            n=1,
            partial_images=None,
            output_compression=100,
            images_max_partial_images=3,
        )
    assert exc.value.param == "output_format"


@pytest.mark.parametrize("data", [[], [{"b64_json": ""}], [{"b64_json": "one"}, {"b64_json": "two"}]])
def test_native_transport_rejects_missing_or_unexpected_image_count(data) -> None:
    with pytest.raises(ValueError):
        native_image_response_events({"created": 1, "data": data}, host_model="gpt-5.6-sol")


def test_public_responses_cannot_enable_native_transport() -> None:
    request = ResponsesRequest.model_validate(
        {
            "model": "gpt-5.6-sol",
            "instructions": "",
            "input": "a circle",
            "_native_image_request": {"operation": "generations", "body": {"model": MODELS[0]}},
        }
    )
    assert request._native_image_request is None


def test_native_edits_reject_explicit_masks() -> None:
    with pytest.raises(ClientPayloadError, match="masks"):
        images_edit_to_responses_request(
            V1ImagesEditsForm(model=MODELS[0], prompt="edit"),
            host_model="gpt-5.6-sol",
            images=[(b"image", "image/png")],
            mask=(b"mask", "image/png"),
        )
