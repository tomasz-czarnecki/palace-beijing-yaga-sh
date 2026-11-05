import sys, glob, os
from PIL import Image
for out in sys.argv[1:]:
    parts = sorted(glob.glob(out.replace('.png', '.part*.png')))
    if not parts: continue
    ims = [Image.open(p) for p in parts]
    W, H = ims[0].width, sum(i.height for i in ims)
    canvas = Image.new('RGB', (W, H))
    y = 0
    for i in ims:
        canvas.paste(i, (0, y)); y += i.height
    canvas.save(out)
    for p in parts: os.remove(p)
    print(out, W, H)
