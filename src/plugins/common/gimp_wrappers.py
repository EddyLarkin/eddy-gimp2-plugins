#!/usr/bin/env python
"""Wrappers for the GIMP module

GIMP doesn't play nicely with other modules, so here's some wrappers to avoid having to
directly import it when debugging plugins from the command line
"""
import os

# need wildcard import so it's easy to merge everything into the
# single files required by GIMP plugins
from common.gimp_base import * # pylint: disable=wildcard-import,relative-import

class GimpWrapper(object):
    """Wrapper functionality in the gimpfu module

    Note:
        gimpfu doesn't seem to play nicely with other modules so here's a wrapper
        to insulte unit tests from having to import it directly
    """

    def __init__(self, gimpfu_module):
        # type: (GimpWrapper, any) -> None
        """Initialise the wrapper with the gimp and pdb modules

        Args:
            gimpfu: Gimpfu module to wrap
        """
        assert gimpfu_module
        self._gimpfu = gimpfu_module

    def start_progress_bar(self, steps_max=1):
        # type: (GimpWrapper, int) -> None
        """Start the progress bar from zero

        Args:
            steps_max: Maximum number of steps to expect
        """
        assert steps_max > 0
        self._steps_max = steps_max
        self._steps_current = 0
        self.increment_progress_bar(0)

    def increment_progress_bar(self, steps=1):
        # type: (GimpWrapper, int) -> None
        """Start the progress bar from zero

        Args:
            steps: Number of steps to increment by
        """
        assert steps >= 0
        self._steps_current = min(self._steps_max, self._steps_current + steps)
        self._gimpfu.gimp.progress_update(float(self._steps_current) / self._steps_max)

    def get_image(self, size, colour_channels=None):
        # type: (GimpWrapper, PixelSize, any) -> any
        """Create a new image from scratch at the given size

        Args:
            size:            Size of the image to create
            colour_channels: Colour channels of the image to create
        """
        assert size
        if not colour_channels:
            colour_channels = self.rgb

        return self._gimpfu.gimp.Image(size.width, size.height, colour_channels)

    def new_layer_from_drawable(self, old_layer, new_image):
        # type: (GimpImage, any, any) -> any
        """Copies a layer to a new one and returns it

        Args:
            old_layer: Old layer to copy
            new_image: Image to contain the copy
        """
        new_layer = self._gimpfu.pdb.gimp_layer_new_from_drawable(old_layer, new_image)
        new_layer.opacity = old_layer.opacity
        return new_layer

    def flatten_and_export_image(self, image, file_name, clipping=None):
        # type: (GimpWrapper, any, str, any) -> None
        """Flatten visible layers in an image and save it as a png

        Args:
            image:     GIMP image to flatten and export
            file_name: File name to write to
            clipping:  Option for clipping merged layers
        """
        assert image
        assert file_name
        if not clipping:
            clipping = self.clip_to_image

        out_layer = self._gimpfu.pdb.gimp_image_merge_visible_layers(
            image, clipping)
        self._gimpfu.pdb.gimp_file_save(
            image, out_layer, file_name, file_name)

    @property
    def rgb(self):
        # type: (None) -> any
        """Specifier for RGB color channels on an image"""
        return self._gimpfu.RGB

    @property
    def clip_to_image(self):
        # type: (None) -> any
        """Specifier for clipping to an image when merging layers"""
        return self._gimpfu.CLIP_TO_IMAGE

    _steps_max = 1
    _steps_current = 0

class GimpLayer(object): #pylint: disable=too-few-public-methods
    """Wrapper for a GIMPFU layer

    Note:
        gimpfu doesn't seem to play nicely with other modules so here's a wrapper
        to insulte unit tests from having to import it directly
    """

    def __init__(self, gimp_wrapper, image, layer):
        # type: (GimpLayer, GimpWrapper, any, any) -> None
        """Initialise the wrapper with the gimp and pdb modules

        Args:
            gimp_wrapper: Wrapper for gimpfu module
            image:         Gimp image to wrap
            file_name:    Defult file name to save to
        """
        assert gimp_wrapper
        assert image
        assert layer

        self._gimp_wrapper = gimp_wrapper
        self._image = image
        self._layer = layer

    def set_offset(self, offset):
        # type: (GimpLayer, PixelPosition) -> None
        """Add an offset to this layer on its parent image

        Args:
            offset: Offset from (0, 0)
        """
        self._layer.set_offsets(offset.pos_x, offset.pos_y)

class GimpImage(object):
    """Wrapper for a GIMPFU image

    Note:
        gimpfu doesn't seem to play nicely with other modules so here's a wrapper
        to insulte unit tests from having to import it directly
    """

    def __init__(self, gimp_wrapper, image, file_name=None):
        # type: (GimpImage, GimpWrapper, any, str) -> None
        """Initialise the wrapper with the gimp and pdb modules

        Args:
            gimp_wrapper: Wrapper for gimpfu module
            image:         Gimp image to wrap
            file_name:    Defult file name to save to
        """
        assert gimp_wrapper
        assert image
        if not file_name:
            file_name = image.filename

        self._gimp_wrapper = gimp_wrapper
        self._image = image
        self._file_name = file_name

        self._layers = []
        for layer in image.layers:
            self._layers.append(
                GimpLayer(gimp_wrapper, image, layer))

    def __nonzero__(self):
        # type: (GimpImage) -> bool
        return self._image and bool(self._image.layers)

    @staticmethod
    def new_image(gimp_wrapper, size, file_name=None, colour_channels=None):
        # type: (GimpWrapper, PixelSize, str, any) -> GimpImage
        """Create a new image from scratch at the given size

        Args:
            gimp_wrapper:    Wrapper for GIMP module
            size:            Size of the image to create
            file_name:       Default file name of the image to create
            colour_channels: Colour channels of the image to create
        """
        assert size
        image = gimp_wrapper.get_image(size, colour_channels)
        return GimpImage(gimp_wrapper, image, file_name)

    def add_layer(self, layer):
        # type: (GimpImage, GimpLayer) -> None
        """Pushes a new layer onto the image

        Args:
            layer: Layer to add
        """
        self._image.add_layer(layer._layer, -1)  # pylint: disable=protected-access
        self._layers.append(layer)

    def new_layer_from_drawable(self, old_layer):
        # type: (GimpImage, any) -> GimpLayer
        """Copies a layer to a new one in this image and returns it

        Args:
            old_layer: Old layer to copy
        """
        internal_layer = self._gimp_wrapper.new_layer_from_drawable(old_layer, self._image)
        return GimpLayer(self._gimp_wrapper, self._image, internal_layer)

    @property
    def exported_file_name(self):
        # type: (GimpImage) -> str
        """Get an output file name from the image
        """
        file_name = os.path.splitext(self._file_name)[0]
        return "{}.png".format(file_name)

    def export_to_file(self, exported_file_name=None):
        # type: (GimpImage) -> None
        """Get an output file name from the image

        Args:
            exported_file_name: File name to use;
                                defaults to image name with .png instead of .xcf
        """
        if not exported_file_name:
            exported_file_name = self.exported_file_name

        self._gimp_wrapper.flatten_and_export_image(self._image, exported_file_name)