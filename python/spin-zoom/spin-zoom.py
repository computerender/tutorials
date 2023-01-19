import math
from io import BytesIO
import asyncio
from computerender import Computerender
from tqdm import tqdm
from PIL import Image
import numpy as np
from mediapy import VideoWriter

input_file = "IMG_4839.jpeg" # <-- Starting image
output_file = "sd-zoom-output.mp4"
prompt = "beautiful lush forest, national geographic"
frames = 100 # Length of video
strength = 0.4 # How strong the styling effect should be (range 0.1-1.0)
scale_speed = 0.98 # How fast to zoom
angle_speed = 0.9 * 2 * math.pi / 360 # How fast to rotate
iterations = 60
guidance = 11.0
output_res = (512, 512)
out_r = (output_res[1], output_res[0])
parallel_jobs = 4

# using the cropping method from here:
# https://note.nkmk.me/en/python-pillow-square-circle-thumbnail/
def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

# PIL doesn't have a great way for building 
# affine transformations so we're doing it manually
def create_transform(angle, scale, dimensions):
  # center of image
  x = dimensions[0] // 2
  y = dimensions[1] // 2

  # translation matrix to center of image
  trans_a = np.array([[1, 0, x],
                      [0, 1, y],
                      [0, 0, 1]])
  # rotation matrix
  rot =     np.array([[math.cos(angle), math.sin(angle), 0],
                      [-math.sin(angle), math.cos(angle), 0],
                      [0, 0, 1]])
  # scale matrix
  scale = np.array([[scale_speed, 0,  0],
                    [0, scale_speed, 0],
                      [0, 0, 1]])
  # translate back to original position
  trans_b = np.array([[1, 0, -x],
                      [0, 1, -y],
                      [0, 0, 1]])
  # compose transformations into a single matrix
  return trans_a @ rot @ scale @ trans_b

cr = Computerender()

async def img2img(img, strength_mul, seed):
  img_bytes = BytesIO()
  img.save(img_bytes, format="jpeg")
  img_out = await cr.generate(
    prompt, iterations=iterations, seed=seed, strength=strength*strength_mul,
    guidance=guidance, img=img_bytes.getvalue()
  )
  return Image.open(BytesIO(img_out))

async def main():

  # load base image 
  cur_img = crop_max_square(
      Image.open(input_file)
    ).resize(output_res, Image.Resampling.NEAREST)

  with VideoWriter(output_file, shape=output_res, fps=30) as w:
    
    w.add_image(np.array(cur_img))
    
    # for each frame
    for idx in tqdm(range(frames)):

        # run img2img
        cur_img = await img2img(cur_img, 1.0, idx)

        w.add_image(np.array(cur_img))

        t = create_transform(angle_speed, scale_speed, out_r)
        # transform image
        cur_img = cur_img.transform(
          out_r,
          Image.Transform.AFFINE,
          (t[0][0], t[0][1], t[0][2], t[1][0], t[1][1], t[1][2]),
          resample=Image.Resampling.BILINEAR)

asyncio.run(main())