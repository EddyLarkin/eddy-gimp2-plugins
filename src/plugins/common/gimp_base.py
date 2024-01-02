#!/usr/bin/env python
"""Base classes to use when developing GIMP plugins
"""

class PixelSize(object): #pylint: disable=too-few-public-methods
    """Width and height in pixels used when drawing with GIMP plugins

    Attributes:
        width:  Width of a pixel region
        height: Height of a pixel region
    """

    def __init__(self, width, height):
        # type: (PixelSize, int, int) -> None
        """Initialise the wrapper with the gimp and pdb modules

        Args:
            width:  Width of a pixel region
            height: Height of a pixel region
        """
        self.width = width
        self.height = height

    def __nonzero__(self):
        # type: (PixelSize) -> bool
        return self.width.__nonzero__() and self.height.__nonzero__()

class PixelPosition(object): #pylint: disable=too-few-public-methods
    """Co-ordinates of a pixel position used when drawing with GIMP plugins

    Attributes:
        x: x co-ordinate of a position
        y: y co-ordinate of a position
    """

    def __init__(self, pos_x, pos_y):
        # type: (PixelSize, int, int) -> None
        """Initialise the wrapper with the gimp and pdb modules

        Args:
            x: x co-ordinate of a position
            y: y co-ordinate of a position
        """
        self.pos_x = pos_x
        self.pos_y = pos_y