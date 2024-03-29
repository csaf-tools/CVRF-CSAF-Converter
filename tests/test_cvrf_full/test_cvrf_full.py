"""File containing full CVRF test."""
import json
from contextlib import suppress


with open('./test_cvrf_full.json', encoding='utf-8') as f:
    csaf = json.loads(f.read())


# pylint: disable=missing-function-docstring
def assert_object(path, length=None):
    parts = path.split('/')

    try:
        next_ = csaf
        for part in parts:
            with suppress(ValueError):
                part = int(part)

            next_ = next_[part]

    except KeyError as err:
        print(f'FAILED. Missing CSAF path: /{path}')
        raise AssertionError from err

    if length:
        assert len(next_) == length

# pylint: disable=too-many-statements
def test_full_input_cvrf():
    """
    Tests that all expected objects are present in the input.
    Full input means that all possible (mandatory and optional) CVRF elements are
     present in the input and are asserted in the output.
    """
    assert_object('document')
    assert_object('document/title')
    assert_object('document/publisher')
    assert_object('document/publisher/contact_details')
    assert_object('document/publisher/issuing_authority')
    assert_object('document/tracking')
    assert_object('document/tracking/id')
    assert_object('document/tracking/aliases', 2)
    assert_object('document/tracking/status')
    assert_object('document/tracking/version')
    assert_object('document/tracking/revision_history', 2)
    assert_object('document/tracking/revision_history/0/date')
    assert_object('document/tracking/revision_history/0/number')
    assert_object('document/tracking/revision_history/0/summary')
    assert_object('document/tracking/revision_history/1/date')
    assert_object('document/tracking/revision_history/1/number')
    assert_object('document/tracking/revision_history/1/summary')
    assert_object('document/tracking/initial_release_date')
    assert_object('document/tracking/current_release_date')
    assert_object('document/tracking/generator')
    assert_object('document/tracking/generator/date')
    assert_object('document/tracking/generator/engine')
    assert_object('document/tracking/generator/engine/name')
    assert_object('document/tracking/generator/engine/version')
    assert_object('document/notes', 2)
    assert_object('document/notes/0/text')
    assert_object('document/notes/0/category')
    assert_object('document/notes/0/audience')
    assert_object('document/notes/0/title')
    assert_object('document/notes/1/text')
    assert_object('document/notes/1/category')
    assert_object('document/notes/1/audience')
    assert_object('document/notes/1/title')
    assert_object('document/distribution')
    assert_object('document/distribution/text')
    assert_object('document/aggregate_severity')
    assert_object('document/aggregate_severity/text')
    assert_object('document/aggregate_severity/namespace')
    assert_object('document/references', 2)
    assert_object('document/references/0/summary')
    assert_object('document/references/0/category')
    assert_object('document/references/0/url')
    assert_object('document/references/1/summary')
    assert_object('document/references/1/category')
    assert_object('document/references/1/url')
    assert_object('document/acknowledgments', 2)
    assert_object('document/acknowledgments/0/summary')
    assert_object('document/acknowledgments/0/organization')
    assert_object('document/acknowledgments/0/names')
    assert_object('document/acknowledgments/0/urls')
    assert_object('document/acknowledgments/1/names', 2)

    assert_object('product_tree')
    assert_object('product_tree/full_product_names', 2)
    assert_object('product_tree/full_product_names/0/product_id')
    assert_object('product_tree/full_product_names/0/name')
    assert_object('product_tree/full_product_names/0/product_identification_helper')
    assert_object('product_tree/full_product_names/0/product_identification_helper/cpe')
    assert_object('product_tree/full_product_names/1/product_id')
    assert_object('product_tree/full_product_names/1/name')
    assert_object('product_tree/relationships', 2)
    assert_object('product_tree/relationships/0/category')
    assert_object('product_tree/relationships/0/product_reference')
    assert_object('product_tree/relationships/0/relates_to_product_reference')
    assert_object('product_tree/relationships/0/full_product_name')
    assert_object('product_tree/relationships/0/full_product_name/product_id')
    assert_object('product_tree/relationships/0/full_product_name/name')
    assert_object('product_tree/relationships/1/category')
    assert_object('product_tree/relationships/1/product_reference')
    assert_object('product_tree/relationships/1/relates_to_product_reference')
    assert_object('product_tree/relationships/1/full_product_name')
    assert_object('product_tree/relationships/1/full_product_name/product_id')
    assert_object('product_tree/relationships/1/full_product_name/name')
    assert_object('product_tree/product_groups', 1)
    assert_object('product_tree/product_groups/0/group_id')
    assert_object('product_tree/product_groups/0/product_ids', 2)
    assert_object('product_tree/branches', 2)
    assert_object('product_tree/branches/0/name')
    assert_object('product_tree/branches/0/category')
    assert_object('product_tree/branches/0/branches', 1)
    assert_object('product_tree/branches/0/branches/0/name')
    assert_object('product_tree/branches/0/branches/0/category')
    assert_object('product_tree/branches/0/branches/0/branches', 2)
    assert_object('product_tree/branches/0/branches/0/branches/0/name')
    assert_object('product_tree/branches/0/branches/0/branches/0/category')
    assert_object('product_tree/branches/0/branches/0/branches/0/product')
    assert_object('product_tree/branches/0/branches/0/branches/0/product/product_id')
    assert_object('product_tree/branches/0/branches/0/branches/0/product/name')
    assert_object('product_tree/branches/0/branches/0/branches/1/name')
    assert_object('product_tree/branches/0/branches/0/branches/1/category')
    assert_object('product_tree/branches/0/branches/0/branches/1/product')
    assert_object('product_tree/branches/0/branches/0/branches/1/product/product_id')
    assert_object('product_tree/branches/0/branches/0/branches/1/product/name')
    assert_object('product_tree/branches/1/name')
    assert_object('product_tree/branches/1/category')
    assert_object('product_tree/branches/1/product')
    assert_object('product_tree/branches/1/product/product_id')
    assert_object('product_tree/branches/1/product/name')
    assert_object('product_tree/branches/1/product/product_identification_helper')
    assert_object('product_tree/branches/1/product/product_identification_helper/cpe')

    assert_object('vulnerabilities', 2)
    assert_object('vulnerabilities/0/cve')
    assert_object('vulnerabilities/0/id')
    assert_object('vulnerabilities/0/id/system_name')
    assert_object('vulnerabilities/0/id/text')
    assert_object('vulnerabilities/0/notes', 2)
    assert_object('vulnerabilities/0/notes/0/text')
    assert_object('vulnerabilities/0/notes/0/category')
    assert_object('vulnerabilities/0/notes/0/title')
    assert_object('vulnerabilities/0/notes/1/text')
    assert_object('vulnerabilities/0/notes/1/category')
    assert_object('vulnerabilities/0/notes/1/title')
    assert_object('vulnerabilities/0/product_status')
    assert_object('vulnerabilities/0/product_status/known_affected', 4)
    assert_object('vulnerabilities/0/references', 1)
    assert_object('vulnerabilities/0/references/0/summary')
    assert_object('vulnerabilities/0/references/0/url')
    assert_object('vulnerabilities/0/references/0/category')
    assert_object('vulnerabilities/0/remediations', 1)
    assert_object('vulnerabilities/0/remediations/0/category')
    assert_object('vulnerabilities/0/remediations/0/details')
    assert_object('vulnerabilities/0/scores', 1)
    assert_object('vulnerabilities/0/scores/0/cvss_v3')
    assert_object('vulnerabilities/0/scores/0/cvss_v3/baseScore')
    assert_object('vulnerabilities/0/scores/0/cvss_v3/vectorString')
    assert_object('vulnerabilities/0/scores/0/cvss_v3/baseSeverity')
    assert_object('vulnerabilities/0/scores/0/cvss_v3/version')
    assert_object('vulnerabilities/0/scores/0/products', 4)
    assert_object('vulnerabilities/0/title')
    assert_object('vulnerabilities/1/acknowledgments', 1)
    assert_object('vulnerabilities/1/acknowledgments/0/names', 1)
    assert_object('vulnerabilities/1/cve')
    assert_object('vulnerabilities/1/cwe')
    assert_object('vulnerabilities/1/cwe/id')
    assert_object('vulnerabilities/1/cwe/name')
    assert_object('vulnerabilities/1/discovery_date')
    assert_object('vulnerabilities/1/id')
    assert_object('vulnerabilities/1/id/system_name')
    assert_object('vulnerabilities/1/id/text')
    assert_object('vulnerabilities/1/involvements', 2)
    assert_object('vulnerabilities/1/involvements/0/party')
    assert_object('vulnerabilities/1/involvements/0/status')
    assert_object('vulnerabilities/1/involvements/0/summary')
    assert_object('vulnerabilities/1/involvements/1/party')
    assert_object('vulnerabilities/1/involvements/1/status')
    assert_object('vulnerabilities/1/notes', 2)
    assert_object('vulnerabilities/1/notes/0/text')
    assert_object('vulnerabilities/1/notes/0/category')
    assert_object('vulnerabilities/1/notes/0/audience')
    assert_object('vulnerabilities/1/notes/0/title')
    assert_object('vulnerabilities/1/notes/1/text')
    assert_object('vulnerabilities/1/notes/1/category')
    assert_object('vulnerabilities/1/notes/1/audience')
    assert_object('vulnerabilities/1/notes/1/title')

    assert_object('vulnerabilities/1/product_status', 2)
    assert_object('vulnerabilities/1/product_status/first_fixed', 2)
    assert_object('vulnerabilities/1/product_status/known_affected', 1)
    assert_object('vulnerabilities/1/references', 1)
    assert_object('vulnerabilities/1/references/0/summary')
    assert_object('vulnerabilities/1/references/0/url')
    assert_object('vulnerabilities/1/references/0/category')
    assert_object('vulnerabilities/1/release_date')
    assert_object('vulnerabilities/1/remediations', 2)
    assert_object('vulnerabilities/1/remediations/0/category')
    assert_object('vulnerabilities/1/remediations/0/details')
    assert_object('vulnerabilities/1/remediations/1/category')
    assert_object('vulnerabilities/1/remediations/1/details')
    assert_object('vulnerabilities/1/remediations/1/entitlements', 1)
    assert_object('vulnerabilities/1/remediations/1/url')
    assert_object('vulnerabilities/1/remediations/1/product_ids', 1)
    assert_object('vulnerabilities/1/remediations/1/group_ids', 1)
    assert_object('vulnerabilities/1/remediations/1/date')

    assert_object('vulnerabilities/1/scores', 3)
    assert_object('vulnerabilities/1/scores/0/cvss_v2/baseScore')
    assert_object('vulnerabilities/1/scores/0/cvss_v2/environmentalScore')
    assert_object('vulnerabilities/1/scores/0/cvss_v2/vectorString')
    assert_object('vulnerabilities/1/scores/0/cvss_v2/version')
    assert_object('vulnerabilities/1/scores/0/products', 1)

    assert_object('vulnerabilities/1/scores/1/cvss_v3/baseScore')
    assert_object('vulnerabilities/1/scores/1/cvss_v3/temporalScore')
    assert_object('vulnerabilities/1/scores/1/cvss_v3/vectorString')
    assert_object('vulnerabilities/1/scores/1/cvss_v3/version')
    assert_object('vulnerabilities/1/scores/1/cvss_v3/baseSeverity')
    assert_object('vulnerabilities/1/scores/1/products', 1)

    assert_object('vulnerabilities/1/scores/2/cvss_v3/baseScore')
    assert_object('vulnerabilities/1/scores/2/cvss_v3/vectorString')
    assert_object('vulnerabilities/1/scores/2/cvss_v3/version')
    assert_object('vulnerabilities/1/scores/2/cvss_v3/baseSeverity')
    assert_object('vulnerabilities/1/scores/2/products', 1)

    assert_object('vulnerabilities/1/threats', 2)
    assert_object('vulnerabilities/1/threats/0/details')
    assert_object('vulnerabilities/1/threats/0/category')
    assert_object('vulnerabilities/1/threats/0/product_ids', 1)
    assert_object('vulnerabilities/1/threats/0/date')
    assert_object('vulnerabilities/1/threats/1/details')
    assert_object('vulnerabilities/1/threats/1/category')
    assert_object('vulnerabilities/1/threats/1/group_ids', 1)
    assert_object('vulnerabilities/1/title')
