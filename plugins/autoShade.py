#!/usr/bin/env python

import inspect
import math
import random
import array
from gimpfu import *

RADIANS = math.pi / 180.;

def pprint(*messages):
  if(len(messages) > 1):
    pdb.gimp_message(messages)
  elif(len(messages) > 0):
    pdb.gimp_message(messages[0])
  else:
    pdb.gimp_message('!')
    
def basicGaus(x, sigma):
  normX = x/sigma
  if(normX < 4.):
    return math.exp( -normX**2 / 2. )
  else:
    return 0.
  
def eddy_autoShade(timg, tdrawable, layerTop=None, angle=270., amount=5., smallNoise=0.1, bigNoise=1.5, bigNoiseScale=50., bigNoiseLambda=80.):
  try:
    pprint("Starting")
    pdb.gimp_image_undo_group_start(timg)
    
    (isSelection, xMin, yMin, xMax, yMax) = pdb.gimp_selection_bounds(timg)
    if not isSelection:
      xMin = 0
      yMin = 0
      xMax = tdrawable.width
      yMax = tdrawable.height
    
    dX = math.cos(angle * RADIANS)
    dY = -math.sin(angle * RADIANS)
    
    pprint('Get big noises')
    size = math.hypot(xMax-xMin, yMax-yMin)
    accum = random.uniform(0., bigNoiseLambda*2.)
    bigNoises = []
    while(accum < size):
      accum += random.uniform(0., bigNoiseLambda*2.)
      bigNoises.append( (
          random.uniform(xMin, xMax),
          random.uniform(yMin, yMax),
          random.uniform(-bigNoise, bigNoise),
          random.uniform(1., bigNoiseScale*2.)
        )
      )
    
    pprint('Main loop')
    i = 0
    iMax = (xMax-xMin) * (yMax-yMin)
    for x in range(xMin, xMax):
      for y in range(yMin, yMax):
        pixel = layerTop.get_pixel(x, y)
        if(pixel == (0, 0, 0, 255)):
          noiseVal = random.uniform(-smallNoise, smallNoise)
          for bigNoise in bigNoises:
            diff = math.hypot(x - bigNoise[0], y - bigNoise[1])
            noiseVal += bigNoise[2] * basicGaus(diff, bigNoise[3])
        
          dXFull = int((amount + noiseVal) * dX)
          dYFull = int((amount + noiseVal) * dY)
          
          pdb.gimp_pencil(tdrawable, 4, [x, y, x+dXFull, y+dYFull])
          
        i += 1
        if i % 100 == 0:
          pdb.gimp_progress_update(float(i)/float(iMax))
            
    pdb.gimp_image_undo_group_end(timg)      
    pprint("Done!")
  except Exception as e:
    pprint("Error: {0}".format(e))

register(
        "python_fu_autoshade",
        "Automatically apply shading to specified layer",
        "Automatically apply shading to specified layer",
        "Eddy Larkin",
        "Eddy Larkin",
        "2023",
        "<Image>/Filters/Eddy/_AutoShade...",
        "RGB*, GRAY*",
        [
                (PF_LAYER, "layerTop", "Top Layer", None),
                (PF_SLIDER, "angle", "Angle", 270., (0., 360., 1.)),
                (PF_FLOAT, "amount", "Amount", 5.),
                (PF_FLOAT, "smallNoise", "Small Noise", .1),
                (PF_FLOAT, "bigNoise", "Big Noise", 1.5),
                (PF_FLOAT, "bigNoiseScale", "Big Noise Scale", 50.),
                (PF_FLOAT, "bigNoiseLambda", "Big Noise Wavelength", 80.),
        ],
        [],
        eddy_autoShade)

main()
