#!/usr/bin/env python

import inspect
import math
import random
import array
from gimpfu import *

RADIANS = math.pi / 180.
MODE_STANDARD = 0
MODE_SYMMETRIC = 1
MODE_ASYMMETRIC = 2

def pprint(*messages):
  if(len(messages) > 1):
    pdb.gimp_message(messages)
  elif(len(messages) > 0):
    pdb.gimp_message(messages[0])
  else:
    pdb.gimp_message('!')

def getIndex(drawable, size, x, y):
    return (x + y*drawable.width) * size

def getPixel(drawable, pixels, size, x, y):
    i = getIndex(drawable, size, x, y)
    if (i < 0 or (i+size) >= len(pixels)):
        return [0, 0, 0, 0]
    else:
        return pixels[i:i+size]

def setPixel(drawable, pixels, size, x, y, r, g, b, a):
    i = getIndex(drawable, size, x, y)
    if (size > 0):
        pixels[i] = r
    if (size > 1):
        pixels[i+1] = g
    if (size > 2):
        pixels[i+2] = b
    if (size > 3):
        pixels[i+3] = a

def eddy_separate(timg, tdrawable, greyscale=False, mode=MODE_STANDARD):
  try:
    pprint("Starting")
    pdb.gimp_image_undo_group_start(timg)
    
    (isSelection, xMin, yMin, xMax, yMax) = pdb.gimp_selection_bounds(timg)
    if not isSelection:
      xMin = 0
      yMin = 0
      xMax = tdrawable.width
      yMax = tdrawable.height
    
    sourcePixelRegion = tdrawable.get_pixel_rgn(0, 0, tdrawable.width, tdrawable.height, False, False)
    destPixelRegion = tdrawable.get_pixel_rgn(0, 0, tdrawable.width, tdrawable.height, True, False)

    pixelSize = len(sourcePixelRegion[0,0])
    sourcePixels = array.array("B", sourcePixelRegion[0:tdrawable.width, 0:tdrawable.height])
    destPixels = array.array("B", sourcePixels)

    pprint('Separating {0} x {1} area'.format(xMax-xMin, yMax-yMin))

    i = 0
    iMax = (xMax-yMin) * (yMax-yMin)
    for x in range(xMin, xMax):
        for y in range(yMin, yMax):
            x2 = xMax - (x - xMin) - 1
            #y2 = yMax - (y - yMin) - 1
            y2 = y # EDDY TODO: add option for axes to separate over
            
            pixel1 = getPixel(tdrawable, sourcePixels, pixelSize, x, y)
            pixel2 = getPixel(tdrawable, sourcePixels, pixelSize, x2, y2)
            
            newR = 0
            newG = 0
            newB = 0
            newA = 0
            if (mode == MODE_SYMMETRIC):
                newR = (pixel1[0] + pixel2[0]) / 2
                newG = (pixel1[1] + pixel2[1]) / 2
                newB = (pixel1[2] + pixel2[2]) / 2
            elif (mode == MODE_ASYMMETRIC):
                newR = ((pixel1[0] - pixel2[0]) + 0xFF) / 2
                newG = ((pixel1[1] - pixel2[1]) + 0xFF) / 2
                newB = ((pixel1[2] - pixel2[2]) + 0xFF) / 2
            else:
                newR = pixel1[0]
                newG = pixel1[1]
                newB = pixel1[2]
            
            if (len(pixel1) > 3):
                newA = pixel1[3]
            
            if (greyscale):
                newX = (newR + newG + newB) / 3
                newR = newX
                newG = newX
                newB = newX

            setPixel(tdrawable, destPixels, pixelSize, x, y, newR, newG, newB, newA)
            
            if i % 100 == 0:
                pdb.gimp_progress_update(float(i)/float(iMax))
            i += 1

    pprint("Finalizing")
    
    sourcePixelRegion[0:tdrawable.width, 0:tdrawable.height] = destPixels.tostring()
    tdrawable.flush()
    tdrawable.update(0, 0, tdrawable.width, tdrawable.height)

    pdb.gimp_image_undo_group_end(timg)
    pprint("Done!")

  except Exception as e:
    pprint("Error: {0}".format(e))

register(
    "python_fu_separate",
    "Separate out components of specified layer",
    "Separate out components of specified layer",
    "Eddy Larkin",
    "Eddy Larkin",
    "2023",
    "<Image>/Filters/Eddy/_Separate...",
    "RGB*, GRAY*",
    [
        (PF_BOOL, "greyscale", "Greyscale", False),
        (PF_RADIO, "mode", "Set extraction mode: ", MODE_STANDARD,
            (
                 ("Standard", MODE_STANDARD),
                 ("Symmetric", MODE_SYMMETRIC),
                 ("Asymmetric", MODE_ASYMMETRIC)
            )
        )
    ],
    [],
    eddy_separate
)

main()
