from io import BytesIO
import asyncio
from computerender import Computerender
from tqdm import tqdm
from PIL import Image
import numpy as np
from mediapy import VideoReader, VideoWriter

input_file = "IMG_0068.MOV" # <-- put your video here
output_file = "sd-output.mp4"
prompt = "a royal prince playing the guitar in magnificent room, victorian painting, highly detailed"
strength = 0.5 # How strong the styling effect should be (range 0.1-1.0)
seed = 200 # Change this to get a different generation using the same parameters
guidance = 13.0 # How much the model should try to stick to the prompt (range 0-20)
iterations = 50
output_res = (512,512)
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

cr = Computerender()

async def img2img(arr, out_r):
  pil_image = crop_max_square(Image.fromarray(arr)).resize(out_r)
  img_bytes = BytesIO()
  pil_image.save(img_bytes, format="jpeg")
  img_out = await cr.generate(
    prompt, iterations=iterations, strength=strength,
    seed=seed, guidance=guidance, img=img_bytes.getvalue()
  )
  return Image.open(BytesIO(img_out))

async def main():
  with VideoReader(input_file) as r:
    with VideoWriter(output_file, shape=output_res, fps=r.fps, bps=r.bps) as w:
      cur_frames = []
      for image in tqdm(r, total=r.num_images):
        cur_frames.append(image)
        if len(cur_frames) == parallel_jobs:
          imgs = await asyncio.gather(*[img2img(frame, out_r) for frame in cur_frames])
          for sd_image in imgs:
            w.add_image(np.array(sd_image))
          cur_frames = []

asyncio.run(main())