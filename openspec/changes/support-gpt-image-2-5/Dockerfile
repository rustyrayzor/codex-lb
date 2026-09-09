FROM ghcr.io/soju06/codex-lb@sha256:3010b3c5567522fbb6e7225bdbe963fa1038c2584641fcec69094875e40e36e5 AS base

FROM alpine:3.22 AS patcher
RUN apk add --no-cache patch
WORKDIR /app
COPY --from=base /app/app/core/clients/proxy.py app/core/clients/proxy.py
COPY --from=base /app/app/core/openai/images.py app/core/openai/images.py
COPY --from=base /app/app/core/openai/requests.py app/core/openai/requests.py
COPY --from=base /app/app/modules/proxy/images_service.py app/modules/proxy/images_service.py
COPY deployed-source.sha256 deployed-1.22.patch /tmp/
RUN sha256sum -c /tmp/deployed-source.sha256 && patch --batch --fuzz=0 -p1 < /tmp/deployed-1.22.patch

FROM base
COPY --from=patcher --chown=app:app /app/app /app/app
RUN python -c "from app.core.openai.native_images import native_image_response_events; from app.modules.proxy.images_service import images_generation_to_responses_request"
LABEL org.opencontainers.image.description="CodexLB 1.22.0 with scoped native Images transport"
