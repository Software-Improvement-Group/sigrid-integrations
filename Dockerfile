FROM python:3.13-alpine

COPY architecture-export/ /integrations/architecture-export
COPY export-portfolio-dependencies/ /integrations/export-portfolio-dependencies
COPY get-scope-file/ /integrations/get-scope-file
COPY issue-tracker-export/ /integrations/issue-tracker-export
COPY ldap-group-sync/ /integrations/ldap-group-sync
COPY objectives-report/ /integrations/objectives-report
COPY osh-findings/ /integrations/osh-findings
COPY polarion-integration/ /integrations/polarion-integration
COPY report-generator/ /sources/report-generator

RUN apk add --no-cache \
        build-base \
        git \
        graphviz \
        openldap-dev \
        python3-dev \
    && adduser -S sigrid \
    && pip install --no-cache-dir --upgrade pip setuptools wheel lxml==6.0.2 \
    && pip install --no-cache-dir /sources/report-generator \
    && rm -rf /sources \
    && pip install --no-cache-dir -r /integrations/objectives-report/requirements.txt \
    && pip install --no-cache-dir -r /integrations/osh-findings/requirements.txt \
    && pip install --no-cache-dir -r /integrations/export-portfolio-dependencies/requirements.txt \
    && pip install --no-cache-dir -r /integrations/ldap-group-sync/requirements.txt

ENV PATH="/integrations/objectives-report:/integrations/get-scope-file:/integrations/export-portfolio-dependencies:/integrations/polarion-integration:/integrations/issue-tracker-export:/integrations/excel-exports:${PATH}"
USER sigrid
WORKDIR /home/sigrid
