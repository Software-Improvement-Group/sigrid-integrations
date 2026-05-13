FROM python:3.13-alpine

COPY architecture-export/ /integrations/architecture-export
COPY export-portfolio-dependencies/ /integrations/export-portfolio-dependencies
COPY get-scope-file/ /integrations/get-scope-file
COPY issue-tracker-export/ /integrations/issue-tracker-export
COPY ldap-group-sync/ /integrations/ldap-group-sync
COPY objectives-report/ /integrations/objectives-report
COPY osh-findings/ /integrations/osh-findings
COPY polarion-integration/ /integrations/polarion-integration
RUN apk add --no-cache \
        build-base \
        graphviz \
        openldap-dev \
        python3-dev \
    && adduser -S sigrid \
    && pip install --no-cache-dir -r /integrations/objectives-report/requirements.txt \
     -r /integrations/osh-findings/requirements.txt \
     -r /integrations/export-portfolio-dependencies/requirements.txt \
     -r /integrations/ldap-group-sync/requirements.txt \
    && apk del build-base \
               openldap-dev \
               python3-dev

ENV PATH="/integrations/objectives-report:/integrations/get-scope-file:/integrations/export-portfolio-dependencies:/integrations/polarion-integration:/integrations/issue-tracker-export:/integrations/excel-exports:/integrations/osh-findings:${PATH}"
USER sigrid
WORKDIR /home/sigrid
