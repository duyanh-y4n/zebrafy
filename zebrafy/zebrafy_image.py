########################################################################################
#
#    Author: Miika Nissi
#    Copyright 2023-2023 Miika Nissi (https://miikanissi.com)
#
#    This file is part of zebrafy
#    (see https://github.com/miikanissi/zebrafy).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
########################################################################################

# 1. Standard library imports:
from io import BytesIO

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from .graphic_field import GraphicField


class ZebrafyImage:
    """
    Provides a method for converting PIL Image or image bytes to Zebra Programming \
    Language (ZPL).

    :param Union[bytes,Image] image: Image as a PIL Image or bytes object.
    :param str compression_type: ZPL compression type parameter that accepts the \
    following values:
        - "A": ASCII hexadecimal - most compatible
        - "B": Base64 binary
        - "C": LZ77 / Zlib compressed base64 binary - best compression
    (Default: ``"A"``)
    :param bool inverse: Invert the black and white in resulting image
    (Default: ``False``)
    :param bool dither: Dither the pixels instead of hard limit on black and white
    (Default: ``True``)
    :param int threshold: Black pixel threshold for undithered image (0-255)
    (Default: ``128``)
    :param bool complete_zpl: Return a complete ZPL with header and footer included. \
    Otherwise return only the graphic field.
    (Default: ``True``)
    """

    def __init__(
        self,
        image,
        compression_type=None,
        inverse=None,
        dither=None,
        threshold=None,
        complete_zpl=None,
    ):
        self._image = image
        if compression_type is None:
            compression_type = "a"
        self._compression_type = compression_type.upper()
        if inverse is None:
            inverse = False
        self._inverse = inverse
        if dither is None:
            dither = True
        self._dither = dither
        if threshold is None:
            threshold = 128
        self._threshold = threshold
        if complete_zpl is None:
            complete_zpl = True
        self._complete_zpl = complete_zpl

    def to_zpl(self):
        """
        Converts PIL Image or image bytes to Zebra Programming Language (ZPL).

        :returns str: A complete ZPL file string which can be sent to a ZPL compatible \
        printer or a ZPL graphic field if complete_zpl is not set.
        """
        if isinstance(self._image, Image.Image):
            pil_image = self._image
        elif isinstance(self._image, bytes):
            pil_image = Image.open(BytesIO(self._image))
        else:
            raise ValueError(
                (
                    "Cannot load image from {source} - not a PIL Image or bytes object."
                ).format(source=self._image)
            )

        if self._dither:
            pil_image = pil_image.convert("1")
            if self._inverse:
                pil_image = pil_image.point(lambda x: 255 - x)
        else:
            pil_image = pil_image.convert("L")
            pil_image = pil_image.point(
                lambda x: (
                    (0 if self._inverse else 255)
                    if x > self._threshold
                    else (255 if self._inverse else 0)
                ),
                mode="1",
            )

        graphic_field = GraphicField(pil_image, compression_type=self._compression_type)

        if self._complete_zpl:
            return "^XA\n" + graphic_field.get_graphic_field() + "\n^XZ\n"

        return graphic_field.get_graphic_field()