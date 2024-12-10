import pytest
from modules.web_request_converter import request_to_curl, curl_to_requests


@pytest.fixture
def curl_data():
    curl_command = (
        "curl 'https://api.pcexpress.ca/pcx-bff/api/v2/listingPage/27985' --compressed -X POST "
        "-H 'sec-ch-ua-platform: \"Windows\"' -H 'is-helios-account: false' "
        "-H 'sec-ch-ua: \"HeadlessChrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"' "
        "-H 'is-iceberg-enabled: false' -H 'sec-ch-ua-mobile: ?0' -H 'origin_session_header: B' "
        "-H 'x-preview: false' -H 'content-type: application/json' -H 'x-channel: web' "
        "-H 'referer: https://www.loblaws.ca/' -H 'accept-language: en' "
        "-H 'business-user-agent: PCXWEB' -H 'x-application-type: Web' "
        "-H 'x-loblaw-tenant-id: ONLINE_GROCERIES' -H 'x-apikey: TEST_DATA' "
        "-H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "HeadlessChrome/129.0.6668.29 Safari/537.36' "
        "--data-raw '{\"cart\":{\"cartId\":\"TEST_DATA\"},\"fulfillmentInfo\":{\"storeId\":\"1029\",\"pickupType\":\"STORE\",\"offerType\":\"OG\",\"date\":\"09122024\",\"timeSlot\":null},\"listingInfo\":{\"filters\":{},\"sort\":{},\"pagination\":{\"from\":1},\"includeFiltersInResponse\":true},\"banner\":\"loblaw\",\"userData\":{\"domainUserId\":\"TEST_DATA\",\"sessionId\":\"TEST_DATA\"}}'"
    )

    return curl_command


def test_request_to_curl(mocker, curl_data):
    mock_request = mocker.Mock()
    mock_request.url = "https://api.pcexpress.ca/pcx-bff/api/v2/listingPage/27985"
    mock_request.method = "POST"
    mock_request.headers = {
        'sec-ch-ua-platform': '"Windows"',
        'is-helios-account': 'false',
        'sec-ch-ua': '"HeadlessChrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'is-iceberg-enabled': 'false',
        'sec-ch-ua-mobile': '?0',
        'origin_session_header': 'B',
        'x-preview': 'false',
        'content-type': 'application/json',
        'x-channel': 'web',
        'referer': 'https://www.loblaws.ca/',
        'accept-language': 'en',
        'business-user-agent': 'PCXWEB',
        'x-application-type': 'Web',
        'x-loblaw-tenant-id': 'ONLINE_GROCERIES',
        'x-apikey': 'TEST_DATA',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/129.0.6668.29 Safari/537.36'
    }
    mock_request.post_data = '{"cart":{"cartId":"TEST_DATA"},"fulfillmentInfo":{"storeId":"1029","pickupType":"STORE","offerType":"OG","date":"09122024","timeSlot":null},"listingInfo":{"filters":{},"sort":{},"pagination":{"from":1},"includeFiltersInResponse":true},"banner":"loblaw","userData":{"domainUserId":"TEST_DATA","sessionId":"TEST_DATA"}}'

    testing_curl = request_to_curl(mock_request)

    expected_curl = curl_data

    assert testing_curl == expected_curl


def test_curl_to_requests(curl_data):
    testing_curl = curl_data
    testing_domain = "loblaws"
    testing_request = curl_to_requests(testing_curl, testing_domain)

    expected_request = {
        "method": "POST",
        "url": "https://api.pcexpress.ca/pcx-bff/api/v2/listingPage/27985",
        "headers": {
            'sec-ch-ua-platform': '"Windows"',
            'is-helios-account': 'false',
            'sec-ch-ua': '"HeadlessChrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'is-iceberg-enabled': 'false',
            'sec-ch-ua-mobile': '?0',
            'origin_session_header': 'B',
            'x-preview': 'false',
            'content-type': 'application/json',
            'x-channel': 'web',
            'referer': 'https://www.loblaws.ca/',
            'accept-language': 'en',
            'business-user-agent': 'PCXWEB',
            'x-application-type': 'Web',
            'x-loblaw-tenant-id': 'ONLINE_GROCERIES',
            'x-apikey': 'TEST_DATA',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'HeadlessChrome/129.0.6668.29 Safari/537.36'
        },
        "payload": '{"cart":{"cartId":"TEST_DATA"},"fulfillmentInfo":{"storeId":"1029","pickupType":"STORE","offerType":"OG","date":"09122024","timeSlot":null},"listingInfo":{"filters":{},"sort":{},"pagination":{"from":1},"includeFiltersInResponse":true},"banner":"loblaw","userData":{"domainUserId":"TEST_DATA","sessionId":"TEST_DATA"}}',
        "domain": "loblaws"
    }

    assert testing_request == expected_request
