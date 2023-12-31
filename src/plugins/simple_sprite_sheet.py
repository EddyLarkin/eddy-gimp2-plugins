#!/usr/bin/env python
"""Simple sprite sheet GIMP plugin

Provides a GIMP plugin for naively separating layers into multiple frames on a sprite sheet
"""
import os
import gimpfu

class PixelSize(object): #pylint: disable=too-few-public-methods
    """Width and height in pixels used when drawing with GIMP plugins

    Attributes:
        width:  Width of a pixel region
        height: Height of a pixel region
    """

    def __init__(self, width, height):
        # type: (PixelSize, any, any) -> None
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
        # type: (GimpWrapper, PixelSize, any) -> GimpImage
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
        return self._gimpfu.pdb.gimp_layer_new_from_drawable(old_layer, new_image)

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

class GimpImage(object):
    """Wrapper for a GIMPFU image

    Note:
        gimpfu doesn't seem to play nicely with other modules so here's a wrapper
        to insulte unit tests from having to import it directly

    Attributes:
        image: Gimp image being wrapped
    """

    def __init__(self, gimp_wrapper, image, file_name=None):
        # type: (GimpImage, GimpWrapper, any, str) -> None
        """Initialise the wrapper with the gimp and pdb modules

        Args:
            image: Gimp image to wrap
        """
        assert gimp_wrapper
        assert image
        if not file_name:
            file_name = image.filename

        self._gimp_wrapper = gimp_wrapper
        self._image = image
        self._file_name = file_name

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
        # type: (GimpImage, any) -> None
        """Pushes a new layer onto the image

        Args:
            layer: Layer to add
        """
        self._image.add_layer(layer, -1)

    def new_layer_from_drawable(self, old_layer):
        # type: (GimpImage, any) -> any
        """Copies a layer to a new one in this image and returns it

        Args:
            old_layer: Old layer to copy
        """
        return self._gimp_wrapper.new_layer_from_drawable(old_layer, self._image)

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

def _get_layer_start_end_indices(layers, sub_layers, guides_per_layer, guides_bottom):
    # type: (int, int, int, int) -> list[tuple[int, int]]
    assert sub_layers > 0
    number_layers = layers - guides_bottom
    assert number_layers > 0

    layer_size = sub_layers + guides_per_layer
    assert number_layers > layer_size
    assert number_layers % layer_size == 0

    return list((i, i + sub_layers - 1) for i in range(0, number_layers, layer_size))

def _get_number_columns(number_frames, source_width, max_columns, max_width):
    # type: (int, int, int, int) -> int
    assert source_width > 0
    assert max_columns > 0

    max_columns_from_width = max_width / source_width
    assert max_columns_from_width > 0

    return min(number_frames, max_columns, max_columns_from_width)

def _get_out_dimensions(source_size, number_layers, number_columns):
    # type: (PixelSize, int, int) -> PixelSize
    assert 0 < number_columns <= number_layers
    number_rows = (number_layers / number_columns) + int(bool(number_layers % number_columns))

    width = source_size.width * number_columns
    height = source_size.height * number_rows
    return PixelSize(width, height)

def _get_layers_to_draw(all_layers, layer_start_end_indices):
    # type: (list, list[tuple[int, int]]) -> list[list]
    assert all_layers
    assert layer_start_end_indices
    assert layer_start_end_indices[0]
    layers_to_draw = []
    for start_index, end_index in layer_start_end_indices:
        assert start_index <= end_index

        sub_layers_to_draw = list(all_layers[i] for i in range(start_index, end_index + 1))
        layers_to_draw.append(sub_layers_to_draw)

    return layers_to_draw

def _get_image_from_layers(
        gimp, source_size, number_layers, number_columns, layer_groups):
    # type: (GimpWrapper, PixelSize, int, int, list[list]) -> GimpImage
    # TODO split up into shorter functions # pylint: disable=fixme
    assert layer_groups
    assert layer_groups[0]

    out_size = _get_out_dimensions(
        source_size, number_layers, number_columns)

    image = GimpImage.new_image(gimp, out_size)
    gimp.start_progress_bar(len(layer_groups))

    column_index = 0
    row_index = 0
    for layer_group in layer_groups:
        offset_x = column_index * source_size.width
        offset_y = row_index * source_size.height

        for layer in reversed(layer_group):
            layer_new = image.new_layer_from_drawable(layer)
            layer_new.opacity = layer.opacity
            layer_new.set_offsets(offset_x, offset_y)
            image.add_layer(layer_new)

        column_index += 1
        if column_index >= number_columns:
            column_index = 0
            row_index += 1

        gimp.increment_progress_bar()

    assert image
    return image

def simple_sprite_sheet( # pylint: disable=too-many-arguments,too-many-locals
        timg,
        tdrawable,
        sub_layers=2,
        guides_per_layer=0,
        guides_bottom=1,
        max_columns=16,
        max_width=1024
):
    # type: (any, any, int, int, int, int, int) -> None
    """
    Automatically add shading to a pixel drawing

    Args:
        timg:             Root GIMP object
        tdrawable:        GIMP object to draw to and from
        sub_layers:       Number of sublayers to combine together for each sprite sheet layer
        guides_per_layer: Number of guide layers to ignore per each sprite sheet layer
        guides_bottom:    Number of guide layers to ignore for the whole sprite sheet
        max_columns:      Maximum allowed number of columns for the sheet
        max_width:        Maximum total width allowed for the sheet (overrides max_columns)

    Raises:
        ValueError: If sub_layers is less than 1
        ValueError: If max_columns is less than 1
        ValueError: If max_width is less than image width
        ValueError: If there are no layers left after subrtracting
                    the values of guides_per_layer and guides_bottom
    """
    gimp = GimpWrapper(gimpfu)
    in_image = GimpImage(gimp, timg)
    layer_start_end_indices = _get_layer_start_end_indices(
        len(timg.layers), sub_layers, guides_per_layer, guides_bottom)

    number_layers = len(layer_start_end_indices)
    number_columns = _get_number_columns(
        number_layers, tdrawable.width, max_columns, max_width)

    layer_groups = _get_layers_to_draw(
        timg.layers, layer_start_end_indices)

    source_size = PixelSize(tdrawable.width, tdrawable.height)
    out_image = _get_image_from_layers(
        gimp, source_size, number_layers, number_columns, layer_groups)

    out_image.export_to_file(in_image.exported_file_name)

gimpfu.register(
    "python_fu_simple_sprite_sheet",
    "Create a sprite sheet from the specified layers",
    "Create a sprite sheet from the specified layers",
    "Eddy Larkin",
    "Eddy Larkin",
    "2023",
    "<Image>/Filters/Eddy/_SimpleSpriteSheet...",
    "RGB*",
    [
        (gimpfu.PF_INT, "sub_layers", "Layers per frame", 2),
        (gimpfu.PF_INT, "guides_per_layer", "Number of guide layers under each sub layer", 0),
        (gimpfu.PF_INT, "guides_bottom", "Number of guide layers under the document", 1),
        (gimpfu.PF_INT, "max_columns", "Maximum number of columns", 16),
        (gimpfu.PF_INT, "max_width", "Maximum width in pixels", 1024),
    ],
    [],
    simple_sprite_sheet
)

gimpfu.main()
