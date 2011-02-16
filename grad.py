from __future__ import division
import struct
import math
from collections import defaultdict


class Bitmap(file):
    """Write only class for creating bitmaps"""

    def __init__(self, fname, width, height):
        file.__init__(self, fname, 'w+b')
        self.height = height
        self.width = width

        self.pixels = defaultdict(lambda: defaultdict(int))
    
    @property
    def bmp_size(self):
        """Size in bytes of the pixel data"""
        row_size = self.width * 3
        return (row_size + (row_size % 4)) * self.height

    def _bmp_header(self):
        """bitmap header"""
        return struct.pack('=2si4xi',
                           "BM",                # Magic Number (unsigned integer 66, 77)
                           self.bmp_size + 34,  # Size of the BMP file
                           54                   # The offset where the bitmap data (pixels) can be found.
                          )

    def _dib_header(self):
        """device independent header"""
        return struct.pack('=3i2h6i',
                           40,                # The number of bytes in the header (from this point).
                           self.width,       # The width of the bitmap in pixels
                           self.height,      # The height of the bitmap in pixels
                           1,                # Number of color planes being used.
                           24,               # The number of bits/pixel.
                           0,                # No compression used
                           self.bmp_size,    # The size of the raw BMP data (after this header)
                           2835, 2835,       # The horizontal/vertical resolution of the image
                           0,                # Number of colors in the palette
                           0                 # Means all colors are important
                          )

    def _bmp(self):
        """bitmap data"""
        b = ''
        for y in xrange(self.height):
            for x in xrange(self.width):
                b += struct.pack('3B',
                                 self.pixels[x][y][2],
                                 self.pixels[x][y][1],
                                 self.pixels[x][y][0])
            b += struct.pack("%sx" % ((3 * self.width) % 4))

        assert len(b) == self.bmp_size
        return b

    def set_pixel(self, x, y, rgb):
        """ Set a pixel in the bitmap to the given color

            x: pos along the x axis [0, width)
            y: height along the y axis
            rgb: 3-tuple in the form (red, green, blue)
                where red green and blue are in the range [0, 255]
        """
        self.pixels[x][y] = rgb

    def flush(self):
        """Flush image to disk"""
        self.write(self._bmp_header())
        self.write(self._dib_header())
        self.write(self._bmp())
        file.flush(self)


def blend(*args):
    """Blends *args by averaging values. Boosts the result by removing 0s"""
    
    #boost colors for brilliance
    args = filter(lambda x: x > 0, args)
    if not len(args):
        return 0

    return int(sum(args) / len(args))

if __name__ == '__main__':
    width, height = 500, 250
    b = Bitmap("result.bmp", width, height)

    ul = (255, 0, 0)
    ur = (0, 255, 0)
    ll = (0, 0, 255)
    lr = (255, 255, 255)

    cur = lambda x, y: math.sqrt(x/width * y/height)
    cul = lambda x, y: math.sqrt(abs(width-x)/width * y/height)
    clr = lambda x, y: math.sqrt(x/width * abs(height-y)/height)
    cll = lambda x, y: math.sqrt(abs(width-x)/width * abs(height-y)/height)

    for x in xrange(width):
        for y in xrange(height):
            b.set_pixel(x, y, (
                blend(cul(x, y)*ul[0],
                      cur(x,y)*ur[0],
                      clr(x,y)*lr[0],
                      cll(x,y)*ll[0]
                     ),
                blend(cul(x, y)*ul[1],
                      cur(x,y)*ur[1],
                      clr(x,y)*lr[1],
                      cll(x,y)*ll[1]
                     ),
                blend(cul(x, y)*ul[2],
                      cur(x,y)*ur[2],
                      clr(x,y)*lr[2],
                      cll(x,y)*ll[2]
                     )
              ))

    b.flush()
    b.close()
