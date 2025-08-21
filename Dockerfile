FROM python:alpine

COPY export-portfolio-dependencies/ /integrations/export-portfolio-dependencies
COPY get-scope-file/ /integrations/get-scope-file
COPY issue-tracker-export/ /integrations/issue-tracker-export
COPY objectives-report/ /integrations/objectives-report
COPY polarion-integration/ /integrations/polarion-integration
COPY report-generator/ /sources/report-generator

RUN apk add --no-cache \
        py3-lxml=5.3.1-r3 \
    && adduser -S sigrid \
    && pip install --no-cache-dir /sources/report-generator \
    && rm -rf /sources \
    && pip install --no-cache-dir -r /integrations/objectives-report/requirements.txt \
    && pip install --no-cache-dir -r /integrations/export-portfolio-dependencies/requirements.txt

ENV PATH="/integrations/objectives-report:/integrations/get-scope-file:/integrations/export-portfolio-dependencies:/integrations/polarion-integration:/integrations/issue-tracker-export:${PATH}"
USER sigrid
WORKDIR /home/sigrid
