import urllib.parse
from typing import Dict

UTF8_TO_CP1251_MAP: Dict[str, str] = {
    "%D0%B0": "%E0", "%D0%B1": "%E1",
    "%D0%B2": "%E2", "%D0%B3": "%E3", "%D0%B4": "%E4",
    "%D0%B5": "%E5", "%D1%91": "%B8",
    "%D0%B6": "%E6", "%D0%B7": "%E7", "%D0%B8": "%E8",
    "%D0%B9": "%E9", "%D0%BA": "%EA",
    "%D0%BB": "%EB", "%D0%BC": "%EC", "%D0%BD": "%ED",
    "%D0%BE": "%EE", "%D0%BF": "%EF",
    "%D1%80": "%F0", "%D1%81": "%F1", "%D1%82": "%F2",
    "%D1%83": "%F3", "%D1%84": "%F4",
    "%D1%85": "%F5", "%D1%86": "%F6", "%D1%87": "%F7",
    "%D1%88": "%F8", "%D1%89": "%F9",
    "%D1%8C": "%FC", "%D1%8B": "%FB", "%D1%8A": "%FA",
    "%D1%8D": "%FD", "%D1%8E": "%FE",
    "%D1%8F": "%FF", "%D0%90": "%C0", "%D0%91": "%C1",
    "%D0%92": "%C2", "%D0%93": "%C3",
    "%D0%94": "%C4", "%D0%95": "%C5", "%D0%81": "%A8",
    "%D0%96": "%C6", "%D0%97": "%C7",
    "%D0%98": "%C8", "%D0%99": "%C9", "%D0%9A": "%CA",
    "%D0%9B": "%CB", "%D0%9C": "%CC",
    "%D0%9D": "%CD", "%D0%9E": "%CE", "%D0%9F": "%CF",
    "%D0%A0": "%D0", "%D0%A1": "%D1",
    "%D0%A2": "%D2", "%D0%A3": "%D3", "%D0%A4": "%D4",
    "%D0%A5": "%D5", "%D0%A6": "%D6",
    "%D0%A7": "%D7", "%D0%A8": "%D8", "%D0%A9": "%D9",
    "%D0%AC": "%DC", "%D0%AB": "%DB",
    "%D0%AA": "%DA", "%D0%AD": "%DD", "%D0%AE": "%DE",
    "%D0%AF": "%DF"
}


def urlencode_rus(text: str) -> str:
    encoded = urllib.parse.quote(text, safe="!*'()")
    return encoded.replace("%20", "+")


def convert_utf8_url_to_cp1251_url(encoded_str: str) -> str:
    result = []
    i = 0
    length = len(encoded_str)

    while i < length:
        if i + 6 <= length:
            chunk = encoded_str[i:i+6]
            if chunk in UTF8_TO_CP1251_MAP:
                result.append(UTF8_TO_CP1251_MAP[chunk])
                i += 6
                continue
        result.append(encoded_str[i])
        i += 1

    return "".join(result)


def encode_win1251_url(text: str) -> str:
    utf8_encoded = urlencode_rus(text)
    cp1251_encoded = convert_utf8_url_to_cp1251_url(utf8_encoded)
    return cp1251_encoded
