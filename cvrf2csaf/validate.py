"""
The module providing validation functionality
"""
from ssl import SSLContext
from typing import Any, Optional, Union, Tuple

from attrs import define, field
from httpx import Client, Timeout

SECVISOGRAM_TEMPLATE = {
  "tests": [
    {
      "name": "csaf_2_0",
      "type": "test"
    },
    {
      "name": "schema",
      "type": "preset"
    }
  ],
  "document": {
  }
}

DEFAULT_MODE = 'secvisogram'
DEFAULT_ENDPOINT = 'http://localhost:8082/api/v1/validate'
SUPPORTED_MODES = [DEFAULT_MODE]


@define
class Validator:
    """
    Calling the validation services.
    Also accepts parameters for authentication (headers, cookies).
    """
    endpoint: str = field(default=DEFAULT_ENDPOINT)
    mode: str = field(default=DEFAULT_MODE)
    _headers: dict[str, str] = field(factory=dict, kw_only=True, alias="headers")
    _timeout: Optional[Timeout] = field(default=None, kw_only=True, alias="timeout")
    _verify_ssl: Union[str, bool, SSLContext] = field(default=True, kw_only=True,
                                                      alias="verify_ssl")
    _httpx_args: dict[str, Any] = field(factory=dict, kw_only=True, alias="httpx_args")
    _cookies: Optional[dict] = field(default=None, init=False)

    @property
    def client(self):
        """
        Create a httpx Client object
        """
        return Client(
                cookies=self._cookies,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
                **self._httpx_args,
            )

    def validate(self, document: dict) -> Tuple[bool, dict]:
        """
        Call the validation enpoint and return the result

        Return values:
            validity: True, if the document is valid, False if it's not
            errors: List of errors
        """
        if self.mode == 'secvisogram':
            result = self.client.post(self.endpoint,
                                      json=SECVISOGRAM_TEMPLATE | {'document': document}).json()
            errors = [test for test in result['tests'] if test['errors']]
            return result['isValid'], errors

        raise NotImplementedError(f"Mode {self.mode} is not supported.")
