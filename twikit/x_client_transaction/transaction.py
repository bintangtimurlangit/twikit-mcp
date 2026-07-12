import re
import bs4
import math
import time
import random
import base64
import hashlib
from typing import Union, List
from functools import reduce
from .cubic_curve import Cubic
from .interpolate import interpolate
from .rotation import convert_rotation_to_matrix
from .utils import float_to_hex, is_odd, base64_encode, handle_x_migration

# X historically shipped the ondemand file hash directly as
#   "ondemand.s":"<hash>"
# but since ~March 2026 the web manifest references it by numeric index first
#   ,<N>:"ondemand.s"   ...   ,<N>:"<hash>"
# We try the new (index) form first and fall back to the legacy (direct) form so
# the library keeps working across manifest format changes instead of hard-crashing.
ON_DEMAND_FILE_INDEX_REGEX = re.compile(
    r""",(\d+):["']ondemand\.s["']""", flags=(re.VERBOSE | re.MULTILINE))
ON_DEMAND_FILE_LEGACY_REGEX = re.compile(
    r"""['|\"]{1}ondemand\.s['|\"]{1}:\s*['|\"]{1}([\w]*)['|\"]{1}""", flags=(re.VERBOSE | re.MULTILINE))
ON_DEMAND_HASH_PATTERN = r',{}:"([0-9a-f]+)"'
# Kept as an alias for backwards compatibility with code importing the old name.
ON_DEMAND_FILE_REGEX = ON_DEMAND_FILE_LEGACY_REGEX
INDICES_REGEX = re.compile(
    r"""(\(\w{1}\[(\d{1,2})\],\s*16\))+""", flags=(re.VERBOSE | re.MULTILINE))


class ClientTransaction:
    ADDITIONAL_RANDOM_NUMBER = 3
    DEFAULT_KEYWORD = "obfiowerehiring"
    DEFAULT_ROW_INDEX = None
    DEFAULT_KEY_BYTES_INDICES = None

    def __init__(self):
        self.home_page_response = None
        # Populated by init(); kept as None so that a failed/partial init leaves a
        # clean, detectable state instead of raising AttributeError later on
        # (see issue #408: "'ClientTransaction' object has no attribute 'key'").
        self.key = None
        self.key_bytes = None
        self.animation_key = None

    async def init(self, session, headers):
        home_page_response = await handle_x_migration(session, headers)
        home_page_response = self.validate_response(home_page_response)

        row_index, key_bytes_indices = await self.get_indices(
            home_page_response, session, headers)
        # get_animation_key() reads DEFAULT_ROW_INDEX / DEFAULT_KEY_BYTES_INDICES
        # off ``self``, so these must be committed before it runs. They are pure
        # derived values; leaving them set on a later failure is harmless because
        # the request path gates the header on ``self.key is not None``.
        self.DEFAULT_ROW_INDEX = row_index
        self.DEFAULT_KEY_BYTES_INDICES = key_bytes_indices
        key = self.get_key(response=home_page_response)
        key_bytes = self.get_key_bytes(key=key)
        animation_key = self.get_animation_key(
            key_bytes=key_bytes, response=home_page_response)

        # Only commit the rest once every step has succeeded, so a partially
        # completed init (e.g. X changed its JS) never leaves the object with a
        # usable-looking ``key`` that crashes on the next request.
        self.key = key
        self.key_bytes = key_bytes
        self.animation_key = animation_key
        self.home_page_response = home_page_response

    def _resolve_on_demand_file_url(self, response) -> str | None:
        page_source = str(response)
        # New format: locate the ondemand.s entry by its numeric manifest index,
        # then resolve that index to its file hash.
        index_match = ON_DEMAND_FILE_INDEX_REGEX.search(page_source)
        if index_match:
            hash_regex = re.compile(
                ON_DEMAND_HASH_PATTERN.format(index_match.group(1)))
            hash_match = hash_regex.search(page_source)
            if hash_match:
                return (
                    "https://abs.twimg.com/responsive-web/client-web/"
                    f"ondemand.s.{hash_match.group(1)}a.js"
                )
        # Legacy format: the hash is embedded directly next to "ondemand.s".
        legacy_match = ON_DEMAND_FILE_LEGACY_REGEX.search(page_source)
        if legacy_match:
            return (
                "https://abs.twimg.com/responsive-web/client-web/"
                f"ondemand.s.{legacy_match.group(1)}a.js"
            )
        return None

    async def get_indices(self, home_page_response, session, headers):
        key_byte_indices = []
        response = self.validate_response(
            home_page_response) or self.home_page_response
        on_demand_file_url = self._resolve_on_demand_file_url(response)
        if on_demand_file_url:
            on_demand_file_response = await session.request(
                method="GET", url=on_demand_file_url, headers=headers)
            key_byte_indices_match = INDICES_REGEX.finditer(
                str(on_demand_file_response.text))
            for item in key_byte_indices_match:
                key_byte_indices.append(item.group(2))
        if not key_byte_indices:
            raise Exception(
                "Couldn't get KEY_BYTE indices. X likely changed its web client; "
                "the request will proceed without an x-client-transaction-id header."
            )
        key_byte_indices = list(map(int, key_byte_indices))
        return key_byte_indices[0], key_byte_indices[1:]

    def validate_response(self, response: bs4.BeautifulSoup):
        if not isinstance(response, bs4.BeautifulSoup):
            raise Exception("invalid response")
        return response

    def get_key(self, response=None):
        response = self.validate_response(response) or self.home_page_response
        # <meta name="twitter-site-verification" content="mentU...+1yPz..../IcNS+......./RaF...R+b"/>
        element = response.select_one("[name='twitter-site-verification']")
        if not element:
            raise Exception("Couldn't get key from the page source")
        return element.get("content")

    def get_key_bytes(self, key: str):
        return list(base64.b64decode(bytes(key, 'utf-8')))

    def get_frames(self, response=None):
        # loading-x-anim-0...loading-x-anim-3
        response = self.validate_response(response) or self.home_page_response
        return response.select("[id^='loading-x-anim']")

    def get_2d_array(self, key_bytes: List[Union[float, int]], response, frames: bs4.ResultSet = None):
        if not frames:
            frames = self.get_frames(response)
        # return list(list(frames[key[5] % 4].children)[0].children)[1].get("d")[9:].split("C")
        return [[int(x) for x in re.sub(r"[^\d]+", " ", item).strip().split()] for item in list(list(frames[key_bytes[5] % 4].children)[0].children)[1].get("d")[9:].split("C")]

    def solve(self, value, min_val, max_val, rounding: bool):
        result = value * (max_val-min_val) / 255 + min_val
        return math.floor(result) if rounding else round(result, 2)

    def animate(self, frames, target_time):
        # from_color = f"#{''.join(['{:x}'.format(digit) for digit in frames[:3]])}"
        # to_color = f"#{''.join(['{:x}'.format(digit) for digit in frames[3:6]])}"
        # from_rotation = "rotate(0deg)"
        # to_rotation = f"rotate({solve(frames[6], 60, 360, True)}deg)"
        # easing_values = [solve(value, -1 if count % 2 else 0, 1, False)
        #                  for count, value in enumerate(frames[7:])]
        # easing = f"cubic-bezier({','.join([str(value) for value in easing_values])})"
        # current_time = round(target_time / 10) * 10

        from_color = [float(item) for item in [*frames[:3], 1]]
        to_color = [float(item) for item in [*frames[3:6], 1]]
        from_rotation = [0.0]
        to_rotation = [self.solve(float(frames[6]), 60.0, 360.0, True)]
        frames = frames[7:]
        curves = [self.solve(float(item), is_odd(counter), 1.0, False)
                  for counter, item in enumerate(frames)]
        cubic = Cubic(curves)
        val = cubic.get_value(target_time)
        color = interpolate(from_color, to_color, val)
        color = [value if value > 0 else 0 for value in color]
        rotation = interpolate(from_rotation, to_rotation, val)
        matrix = convert_rotation_to_matrix(rotation[0])
        # str_arr = [format(int(round(color[i])), '02x') for i in range(len(color) - 1)]
        # str_arr = [format(int(round(color[i])), 'x') for i in range(len(color) - 1)]
        str_arr = [format(round(value), 'x') for value in color[:-1]]
        for value in matrix:
            rounded = round(value, 2)
            if rounded < 0:
                rounded = -rounded
            hex_value = float_to_hex(rounded)
            str_arr.append(f"0{hex_value}".lower() if hex_value.startswith(
                ".") else hex_value if hex_value else '0')
        str_arr.extend(["0", "0"])
        animation_key = re.sub(r"[.-]", "", "".join(str_arr))
        return animation_key

    def get_animation_key(self, key_bytes, response):
        total_time = 4096
        # row_index, frame_time = [key_bytes[2] % 16, key_bytes[12] % 16 * (key_bytes[14] % 16) * (key_bytes[7] % 16)]
        # row_index, frame_time = [key_bytes[2] % 16, key_bytes[2] % 16 * (key_bytes[42] % 16) * (key_bytes[45] % 16)]

        row_index = key_bytes[self.DEFAULT_ROW_INDEX] % 16
        frame_time = reduce(lambda num1, num2: num1*num2,
                            [key_bytes[index] % 16 for index in self.DEFAULT_KEY_BYTES_INDICES])
        arr = self.get_2d_array(key_bytes, response)
        frame_row = arr[row_index]

        target_time = float(frame_time) / total_time
        animation_key = self.animate(frame_row, target_time)
        return animation_key

    def generate_transaction_id(self, method: str, path: str, response=None, key=None, animation_key=None, time_now=None):
        time_now = time_now or math.floor(
            (time.time() * 1000 - 1682924400 * 1000) / 1000)
        time_now_bytes = [(time_now >> (i * 8)) & 0xFF for i in range(4)]
        key = key or self.key or self.get_key(response)
        key_bytes = self.get_key_bytes(key)
        animation_key = animation_key or self.animation_key or self.get_animation_key(
            key_bytes, response)
        # hash_val = hashlib.sha256(f"{method}!{path}!{time_now}bird{animation_key}".encode()).digest()
        hash_val = hashlib.sha256(
            f"{method}!{path}!{time_now}{self.DEFAULT_KEYWORD}{animation_key}".encode()).digest()
        # hash_bytes = [int(hash_val[i]) for i in range(len(hash_val))]
        hash_bytes = list(hash_val)
        random_num = random.randint(0, 255)
        bytes_arr = [*key_bytes, *time_now_bytes, *
                     hash_bytes[:16], self.ADDITIONAL_RANDOM_NUMBER]
        out = bytearray(
            [random_num, *[item ^ random_num for item in bytes_arr]])
        return base64_encode(out).strip("=")
