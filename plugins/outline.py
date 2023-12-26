#!/usr/bin/env python
import array
from gimpfu import *

PIXEL_BLACK = (0, 0, 0, 255)

def pprint(*messages):
  if(len(messages) > 1):
    pdb.gimp_message(messages)
  elif(len(messages) > 0):
    pdb.gimp_message(messages[0])
  else:
    pdb.gimp_message('!')

def getIndex(drawable, size, x, y):
    return (x + y*drawable.width) * size

def getPixel(pixels, size, i):
    return pixels[i:i+size]
    
def getPixelFromXY(drawable, pixels, size, x, y):
    i = getIndex(drawable, size, x, y)
    if (i < 0 or (i+size) >= len(pixels)):
        return [0, 0, 0, 0]
    else:
        return pixels[i:i+size]
    
def setPixel(pixels, size, i, r, g, b, a):
    if (size > 0):
        pixels[i] = r
    if (size > 1):
        pixels[i+1] = g
    if (size > 2):
        pixels[i+2] = b
    if (size > 3):
        pixels[i+3] = a
  
def eddy_outline(timg, tdrawable):
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
    
    pprint('Main loop')
    
    for x in range(xMin, xMax):
        for y in range(yMin, yMax):
            i = getIndex(tdrawable, pixelSize, x, y)
            
            if (getPixel(sourcePixels, pixelSize, i)[3] < 10):
                if (
                    getPixelFromXY(tdrawable, sourcePixels, pixelSize, x-1, y)[3] > 200 or
                    getPixelFromXY(tdrawable, sourcePixels, pixelSize, x+1, y)[3] > 200 or
                    getPixelFromXY(tdrawable, sourcePixels, pixelSize, x, y-1)[3] > 200 or
                    getPixelFromXY(tdrawable, sourcePixels, pixelSize, x, y+1)[3] > 200
                ):
                    setPixel(destPixels, pixelSize, i, 0, 0, 0, 255)
    
    pprint("Finalizing")
    
    sourcePixelRegion[0:tdrawable.width, 0:tdrawable.height] = destPixels.tostring()
    tdrawable.flush()
    tdrawable.update(0, 0, tdrawable.width, tdrawable.height)
    
    pdb.gimp_image_undo_group_end(timg)
    pprint("Done!")
    
  except Exception as e:
    pprint("Error: {0}".format(e))

register(
        "python_fu_outline",
        "Automatically apply an outline to the selected region",
        "Automatically apply an outline to the selected region",
        "Eddy Larkin",
        "Eddy Larkin",
        "2023",
        "<Image>/Filters/Eddy/_Outline...",
        "RGB*, GRAY*",
        [],
        [],
        eddy_outline)

main()
