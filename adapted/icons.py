#
# © 2019 Jonathan Anderson
# All rights reserved.
#

import os

from enaml.icon import Icon, IconImage
from enaml.image import Image

dirname = os.path.dirname(__file__)
icons = {}

def load(name):
    if name in icons:
        return icons[name]

    with open(os.path.join(dirname, 'icons', f'{name}.png'), 'rb') as f:
        img = IconImage(image=Image(data=f.read()))

    icon = Icon(images=[img])
    icons[name] = icon
    return icon
