#!/usr/bin/env python

# python
import math

# gimp
import gimpfu

MAX_WIDTH = 1000

def gError(text):
    gimpfu.pdb.gimp_message(text)
    return

def python_spriteSheet(timg, tdrawable, subLayers=2, guides=1, shading=20):
    inWidth = tdrawable.width
    inHeight = tdrawable.height

    layers = timg.layers

    nOutLayers = (len(layers) - guides) / subLayers

    outCols = int( (float(MAX_WIDTH)/float(inWidth)) )
    if outCols == 0:
        outCols = 1

    if nOutLayers % outCols:
        outRows = int( nOutLayers/outCols + 1. )
    else:
        outRows = int( nOutLayers/outCols )

    outWidth = outCols * inWidth
    outHeight = outRows * inHeight

    img = gimpfu.gimp.Image(outWidth, outHeight, gimpfu.RGB)
    img.disable_undo()

    for i in range(len(layers)-1 - guides, -1, -1):
        layer = layers[i]
        iOut = (i+1 - guides) / subLayers

        iCol = iOut % outCols
        iRow = ((iOut - iCol) / outCols)

        iPosX = iCol*inWidth
        iPosY = iRow*inHeight

        layerNew = gimpfu.pdb.gimp_layer_new_from_drawable(layer, img) 
        img.add_layer(layerNew, -1)
        layerNew.set_offsets(iPosX, iPosY)

        opacity = 100.
        if (i % subLayers) != subLayers-1:
            opacity *= shading/100.

        layerNew.opacity = opacity

    #img.flatten()
    img.merge_visible_layers(0)

    #gimpfu.gimp.Display(img)
    #gimpfu.gimp.displays_flush()

    fileName = timg.filename
    fileName = "/sheet/".join(fileName.split("/xcf/"))
    fileName = "\\sheet\\".join(fileName.split("\\xcf\\"))
    fileName = fileName[:-4] + ".png"

    gimpfu.pdb.gimp_file_save(img, img.layers[0], fileName, fileName)

    return

gimpfu.register(
        "python_fu_spriteSheet",
        "Create a sprite sheet from the specified layers",
        "Create a sprite sheet from the specified layers",
        "Eddy Larkin",
        "Eddy Larkin",
        "2023",
        "<Image>/Filters/Eddy/_SpriteSheet...",
        "*",
        [   
            (gimpfu.PF_INT, "subLayers", "Layers per frame", 2),
            (gimpfu.PF_INT, "guides", "Number of guide layers at bottom", 1),
            (gimpfu.PF_INT, "shading", "Amount of shading on each layer", 20)
        ],
        [],
        python_spriteSheet)

gimpfu.main()
