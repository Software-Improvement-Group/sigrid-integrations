#  Copyright Software Improvement Group
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Union

from report_generator.generator.report import Report, ReportType
from report_generator.generator.sigrid_api import SigridAPIRequestFailed

Parameter = Union[str, int, Enum]
ParameterList = Iterable[Parameter]

CAMEL_TO_SNAKE_PATTERN = re.compile(r'(?<!^)(?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])')


def class_name_to_placeholder_key(class_name: str):
    return CAMEL_TO_SNAKE_PATTERN.sub('_', class_name).upper()


def function_name_to_placeholder_key(function_name: str):
    return function_name.upper()


class PlaceholderDocType(Enum):
    TEXT = 'Text'
    CHART = 'Chart'
    TABLE = 'Table'
    IMAGE = 'Image'
    OTHER = 'Other'


@dataclass
class Placeholder(ABC):
    """
    Abstract base class representing a dynamic element (placeholder) in a report.

    A Placeholder maps a specific key (string identifier) in a document template
    to a dynamically calculated value. It handles the logic of resolving that value
    into specific document formats (e.g., PowerPoint, Word) based on the ReportType.

    Attributes:
        key (str): The identifier string found in the report template (e.g., 'PROJECT_NAME').
        __doc_type__ (PlaceholderDocType): The type of content this placeholder produces.
                                           Defaults to PlaceholderDocType.OTHER.
    """
    key: str
    __doc_type__: PlaceholderDocType = PlaceholderDocType.OTHER
    __placeholder__ = True

    @classmethod
    @abstractmethod
    def value(cls, parameter: Parameter = None):
        pass

    @classmethod
    def resolve(cls, report: Report) -> None:
        resolve_method_name = cls._determine_resolve_method(report.type)

        if not resolve_method_name:
            return

        try:
            getattr(cls, resolve_method_name)(report, cls.key, cls.value)
        except SigridAPIRequestFailed as e:
            logging.info(f'Failed to resolve {cls.key}: {e}')
        except (KeyError, AttributeError, ValueError) as e:
            logging.warning(f'Failed to resolve {cls.key}: Value not found ({type(e).__name__}: {e})')

    @classmethod
    def _determine_resolve_method(cls, report_type: ReportType):
        if report_type == ReportType.PRESENTATION and hasattr(cls, 'resolve_pptx'):
            return 'resolve_pptx'
        elif report_type == ReportType.DOCUMENT and hasattr(cls, 'resolve_docx'):
            return 'resolve_docx'
        else:
            return None

    @classmethod
    def supports(cls, report_type: ReportType) -> bool:
        return cls._determine_resolve_method(report_type) is not None

    @classmethod
    def is_parameterized(cls):
        return getattr(cls, '__parameterized_placeholder__', False)


class ParameterizedPlaceholder(Placeholder, ABC):
    """
    A specialized Placeholder that expands into multiple values based on a list of parameters.

    Instead of a single key, this class iterates over `allowed_parameters` to generate
    multiple dynamic keys. It expects the `key` attribute to contain a formatting marker
    (specifically `{parameter}`) which is replaced during resolution.

    For multi-dimensional placeholders (e.g., `{metric}` and `{parameter}`), set both
    `allowed_metrics` and `allowed_parameters` to generate all combinations.

    Attributes:
        allowed_parameters (ParameterList): A list of values (str, int, or Enum) used to
                                            generate unique keys and calculate values.
        allowed_metrics (ParameterList): Optional second dimension of parameters. If set,
                                         creates combinations with allowed_parameters.
    """
    __parameterized_placeholder__ = True
    allowed_parameters: ParameterList
    allowed_metrics: ParameterList = None

    @classmethod
    def resolve(cls, report: Report) -> None:
        """
        Iterates through allowed parameters to resolve multiple instances of this placeholder.

        For single-parameter placeholders:
        1. Generates a specific key by replacing '{parameter}' in `cls.key`.
        2. Creates a lambda function to pass the specific parameter to `cls.value`.
        3. Calls the report-specific resolution method (e.g., `resolve_pptx`).

        For multi-parameter placeholders (when `allowed_metrics` is set):
        1. Iterates through all combinations of metrics and parameters.
        2. Replaces both '{metric}' and '{parameter}' in the key.
        3. Passes both metric and parameter to `cls.value`.

        The constructed value callable accepts an `optional_parameter`. This allows the
        underlying report generator (e.g., the PowerPoint resolver) to pass additional
        context or configuration—such as chart filters or formatting options—back into
        `cls.value` during execution.
        
        Args:
            report (Report): The report instance where the placeholders should be resolved.
        """
        resolve_method_name = cls._determine_resolve_method(report.type)
        if not resolve_method_name:
            return

        # Treat single-parameter as multi-parameter with one dimension
        metrics = cls.allowed_metrics if cls.allowed_metrics is not None else [None]

        for metric in metrics:
            for parameter in cls.allowed_parameters:
                key_p = cls.key.replace('{parameter}', str(parameter))
                if metric is not None:
                    key_p = key_p.replace('{metric}', str(metric))
                    value_p = lambda optional_parameter=None, m=metric, p=parameter: cls.value(m, p, optional_parameter)
                else:
                    value_p = lambda optional_parameter=None, p=parameter: cls.value(p, optional_parameter)
                
                try:
                    getattr(cls, resolve_method_name)(report, key_p, value_p)
                except SigridAPIRequestFailed as e:
                    logging.info(f'Failed to resolve {key_p}: {e}')
                except (KeyError, AttributeError, ValueError) as e:
                    logging.warning(f'Failed to resolve {key_p}: Value not found ({type(e).__name__}: {e})')
