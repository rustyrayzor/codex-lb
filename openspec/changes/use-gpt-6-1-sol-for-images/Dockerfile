ARG BASE_IMAGE=codexlb-native-images:1.22.0-20260908
FROM ${BASE_IMAGE}

USER root
COPY patch_image_host.py /tmp/patch_image_host.py
RUN python /tmp/patch_image_host.py /app/app/modules/proxy/api.py \
    && rm /tmp/patch_image_host.py
USER app
RUN python -c "from app.modules.proxy.api import _IMAGES_HOST_MODEL; assert _IMAGES_HOST_MODEL == 'gpt-6.1-sol'"
LABEL org.opencontainers.image.description="CodexLB 1.22.0 native Images with GPT 6.1 Sol account routing"
