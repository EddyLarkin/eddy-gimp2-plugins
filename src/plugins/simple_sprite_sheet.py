#!/usr/bin/env python
"""Simple sprite sheet GIMP plugin

Provides a GIMP plugin for naively separating layers into multiple frames on a sprite sheet
"""
import gimpfu

# set up like this to allow separate modules when developing and testing
# but to merge into a single file when exporting the plugin
from common.simple_sprite_sheet_impl import * # pylint: disable=wildcard-import,unused-wildcard-import,relative-import

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
    simple_sprite_sheet_impl(
        gimpfu,
        timg,
        tdrawable,
        sub_layers,
        guides_per_layer,
        guides_bottom,
        max_columns,
        max_width
    )

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
