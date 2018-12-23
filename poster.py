#!/bin/env python3
import subprocess
import os
from os import listdir
from os.path import isfile, join
import cv2 # or PIL?
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dryrun", type=bool, default=False, help="execute a dry run to test (doesn't actually post)")
parser.add_argument("--effect", type=str, default='white', help='pick the padding effect for images: white or blur')
args = parser.parse_args()


USER=os.environ.get('USER')
PASS=os.environ.get('PASS')
IMAGES_DIR='images'
topost_dir = f'{IMAGES_DIR}/to-post'
posted_dir = f'{IMAGES_DIR}/posted'


def ensure_dir(path):
  if not os.path.exists(path):
    os.makedirs(path)

def list_files(path):
  files = [f for f in listdir(path) if isfile(join(path, f))]
  return files

def post_image(img_path, caption=''):
  ## returns True for success false otherwise
  print(f'posting {img_path} with caption {caption}')
  if (args.dryrun):
    return True
  o = subprocess.run(['instapy', '-u', USER, '-p', PASS, '-f', img_path, '-t', caption], stdout=subprocess.PIPE)
  return (o.returncode == 0)

def square_image(img_path, size=None, pad=True, out_path=None, effect='white'):
  desired_size = size
  im_pth = img_path

  im = cv2.imread(im_pth)
  old_size = im.shape[:2] # old_size is in (height, width) format

  ratio = float(desired_size)/max(old_size)
  new_size = tuple([int(x*ratio) for x in old_size])

  im = cv2.resize(im, (new_size[1], new_size[0]))

  delta_w = desired_size - new_size[1]
  delta_h = desired_size - new_size[0]
  top, bottom = delta_h//2, delta_h-(delta_h//2)
  left, right = delta_w//2, delta_w-(delta_w//2)

  print('sides', top, right, bottom, left)
  # TODO apply the desired effect
  if (effect == 'white'):
    color = [255, 255, 255]
    new_im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT,
        value=color)

    if (out_path):
      cv2.imwrite(out_path, new_im)
    else:
      cv2.imshow("image", new_im)
      cv2.waitKey(0)
      cv2.destroyAllWindows()
  elif (effect == 'blur'):
    assert out_path != None, 'blur effect requires outpath'
    cv2.imwrite(out_path, im)
    o = subprocess.run(['gmic', 'blurBorder.gmic', out_path, '-blurborder',
                        f'{right},{top},6', '-o', out_path],
                       stdout=subprocess.PIPE)
  else:
    raise Exception('unknown effect')

def pick_image():
  ## picks an unposted image with the highest value name
  ensure_dir(topost_dir)
  ensure_dir(posted_dir)
  unposted_images = list_files(topost_dir)
  unposted_images = sorted(unposted_images, reverse=True)
  if (len(unposted_images) == 0): return None
  return unposted_images[0]

def send_one(caption=None):
  caption = caption if caption != None else '#flashback'
  img_name = pick_image();
  if (not img_name): raise Exception('No images left to post')
  img_path = f'{topost_dir}/{img_name}'
  optimg_name = f'opt-{img_name}'
  optimg_path = f'{posted_dir}/{optimg_name}'
  square_image(img_path, size=640, out_path=optimg_path, effect=args.effect)
  if (post_image(optimg_path, caption=caption)):
    os.rename(img_path, f'{posted_dir}/{img_name}')
    print('posted image')
  else:
    print('failed to post image')


if __name__ == '__main__':
  print('ran directly')
  send_one()
  # square_image('IMG_20180415_132440.jpg', size=100)
