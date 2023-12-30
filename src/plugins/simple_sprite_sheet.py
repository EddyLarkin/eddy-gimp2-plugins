#!/usr/bin/env python
"""Simple sprite sheet GIMP plugin

Provides a GIMP plugin for naively separating layers into multiple frames on a sprite sheet
"""
import os
import gimpfu

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

def _get_out_dimensions(source_width, source_height, number_layers, number_columns):
    # type: (int, int, int, int) -> tuple[int, int]
    assert 0 < number_columns <= number_layers
    number_rows = (number_layers / number_columns) + int(bool(number_layers % number_columns))

    width = source_width * number_columns
    height = source_height * number_rows
    return (width, height)

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

def _get_image_from_layers( # pylint: disable=too-many-locals
        source_width, source_height, number_layers, number_columns, layer_groups):
    # type: (int, int, int, int, list[list]) -> gimpfu.gimp.Image
    # TODO split up into shorter functions # pylint: disable=fixme
    assert layer_groups
    assert layer_groups[0]

    out_width, out_height = _get_out_dimensions(
        source_width, source_height, number_layers, number_columns)

    image = gimpfu.gimp.Image(out_width, out_height, gimpfu.RGB)

    layer_groups_total = len(layer_groups)

    layer_group_index = 0
    column_index = 0
    row_index = 0
    for layer_group in layer_groups:
        offset_x = column_index * source_width
        offset_y = row_index * source_height

        for layer in reversed(layer_group):
            layer_new = gimpfu.pdb.gimp_layer_new_from_drawable(layer, image)
            layer_new.opacity = layer.opacity
            layer_new.set_offsets(offset_x, offset_y)
            image.add_layer(layer_new, -1)

        column_index += 1
        if column_index >= number_columns:
            column_index = 0
            row_index += 1

        layer_group_index += 1
        progress = layer_group_index / float(layer_groups_total)
        gimpfu.gimp.progress_update(progress)

    assert image.layers
    return image

def _get_file_name(timg):
    # type: (any) -> str
    file_name = os.path.splitext(timg.filename)[0]
    return "{}.png".format(file_name)

def simple_sprite_sheet( # pylint: disable=too-many-arguments
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

    :param timg            : Root GIMP object
    :param tdrawable       : GIMP object to draw to and from
    :param sub_layers      : Number of sublayers to combine together for each sprite sheet layer
    :param guides_per_layer: Number of guide layers to ignore per each sprite sheet layer
    :param guides_bottom   : Number of guide layers to ignore for the whole sprite sheet
    :param max_columns     : Maximum allowed number of columns for the sheet
    :param max_width       : Maximum total width allowed for the sheet (overrides max_columns)

    :raises ValueError: If sub_layers is less than 1
    :raises ValueError: If max_columns is less than 1
    :raises ValueError: If max_width is less than image width
    :raises ValueError: If there are no layers left after subrtracting
                            the values of guides_per_layer and guides_bottom
    """
    layer_start_end_indices = _get_layer_start_end_indices(
        len(timg.layers), sub_layers, guides_per_layer, guides_bottom)

    number_layers = len(layer_start_end_indices)
    number_columns = _get_number_columns(
        number_layers, tdrawable.width, max_columns, max_width)

    layer_groups = _get_layers_to_draw(
        timg.layers, layer_start_end_indices)

    out_image = _get_image_from_layers(
        tdrawable.width, tdrawable.height, number_layers, number_columns, layer_groups)

    file_name = _get_file_name(timg)
    out_layer = gimpfu.pdb.gimp_image_merge_visible_layers(out_image, gimpfu.CLIP_TO_IMAGE)
    gimpfu.pdb.gimp_file_save(out_image, out_layer, file_name, file_name)

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
