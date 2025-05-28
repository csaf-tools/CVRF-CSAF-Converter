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


@define
class Validator:
    endpoint: str = field(default='http://localhost:8082/api/v1/validate')
    mode: str = field(default='secvisogram')
    _headers: dict[str, str] = field(factory=dict, kw_only=True, alias="headers")
    _timeout: Optional[Timeout] = field(default=None, kw_only=True, alias="timeout")
    _verify_ssl: Union[str, bool, SSLContext] = field(default=True, kw_only=True, alias="verify_ssl")
    _follow_redirects: bool = field(default=False, kw_only=True, alias="follow_redirects")
    _httpx_args: dict[str, Any] = field(factory=dict, kw_only=True, alias="httpx_args")
    _cookies: Optional[dict] = field(default=None, init=False)

    @property
    def client(self):
        return Client(
                cookies=self._cookies,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
                follow_redirects=self._follow_redirects,
                **self._httpx_args,
            )

    def validate(self, document: dict) -> Tuple[bool, dict]:
        if self.mode == 'secvisogram':
            result = self.client.post(self.endpoint, json=SECVISOGRAM_TEMPLATE | {'document': document}).json()
            errors = [test for test in result['tests'] if test['errors']]
            return result['isValid'], errors
        else:
            return NotImplementedError()
