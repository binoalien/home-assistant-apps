ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache \
    python3 \
    py3-yaml \
    tzdata

COPY run.sh /run.sh
COPY export_bundle.py /opt/export_bundle.py
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
