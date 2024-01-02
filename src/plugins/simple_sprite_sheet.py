#!/usr/bin/env python
"""Simple sprite sheet GIMP plugin

Provides a GIMP plugin for naively separating layers into multiple frames on a sprite sheet
"""
import gimpfu

# need wildcard import so it's easy to merge everything into the
# single files required by GIMP plugins
from common.gimp_base import * # pylint: disable=wildcard-import,unused-wildcard-import,relative-import
from common.gimp_wrappers import * # pylint: disable=wildcard-import,unused-wildcard-import,relative-import

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
        offset = PixelPosition(
            column_index * source_size.width,
            row_index * source_size.height
        )

        for layer in reversed(layer_group):
            layer_new = image.new_layer_from_drawable(layer)
            layer_new.set_offset(offset)
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
