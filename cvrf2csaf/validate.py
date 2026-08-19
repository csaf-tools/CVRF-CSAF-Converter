"""
The module provides validation functionality
"""
from ssl import SSLContext
from typing import Any, Optional, Union, Tuple, List
from logging import getLogger

from attrs import define, field
from httpx import Client, Timeout, RequestError

DEFAULT_MODE = 'secvisogram'
DEFAULT_ENDPOINT = 'http://localhost:8082/api/v1/validate'
SUPPORTED_MODES = [DEFAULT_MODE]
DEFAULT_PRESETS = ['basic']

# Don't show debug and info logs from httpx
getLogger('httpx').setLevel('WARNING')


@define
class HttpConfig:
    """HTTP client configuration passed through to httpx."""
    headers: dict[str, str] = field(factory=dict)
    timeout: Optional[Timeout] = field(default=None)
    verify_ssl: Union[str, bool, SSLContext] = field(default=True)
    httpx_args: dict[str, Any] = field(factory=dict)
    cookies: Optional[dict] = field(default=None, init=False)


@define  # creates a constructor
class Validator:
    """
    Calling the validation services.
    Also accepts parameters for authentication (headers, cookies).
    """
    endpoint: str = field(default=DEFAULT_ENDPOINT)
    mode: str = field(default=DEFAULT_MODE)
    presets: List = field(default=DEFAULT_PRESETS)
    _http: HttpConfig = field(factory=HttpConfig)

    @property
    def client(self):
        """
        Create an httpx Client object
        """
        return Client(
                cookies=self._http.cookies,
                headers=self._http.headers,
                timeout=self._http.timeout,
                verify=self._http.verify_ssl,
                **self._http.httpx_args,
            )

    def validate(self, document: dict) -> Tuple[bool, dict]:
        """
        Call the validation enpoint and return the result

        Return values:
            validity: True, if the document is valid, False if it's not
            errors: List of errors
        """
        if self.mode == 'secvisogram':
            try:
                result = self.client.post(self.endpoint,
                                          json={
                                                  'tests': [{"name": preset,
                                                             "type": "preset"}
                                                            for preset in self.presets],
                                                  'document': document}).json()
            except RequestError as e:
                return False, str(e)

            errors = [test for test in result['tests'] if test['errors']]
            return result['isValid'], errors

        raise NotImplementedError(f"Mode {self.mode} is not supported.")

    def log_result(self, validation_result: List, logger: "logging.Logger"):
        """
        Logs the results of a validation to the given logger.

        Parameters:
            validation_result
            logger
        """
        for test in validation_result:
            if isinstance(validation_result, str):  # handling exceptions
                logger.error('Validation service error: %r', (validation_result, ))
                return
            for log_t in ('info', 'warning', 'error'):
                for message in test[f"{log_t}s"]:
                    getattr(logger, log_t)(f"Test {test['name']!r}: "
                                           f"{message['message']!r} in {message['instancePath']!r}")
