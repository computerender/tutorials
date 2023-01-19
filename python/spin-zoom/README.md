# vid2vid 
  
Spinning zoom effect using stable diffusion via [computerender](https://computerender.com).  

<img src="/python/spin-zoom/spin-zoom.gif?raw=true" width="384px">

## 1. Setup
You can install the python dependencies by running:

```bash
pip install -r requirements.txt
```

To install install ffmpeg:
Linux
```bash
apt install ffmpeg
```
Macos:
```bash
brew install ffmpeg
```
Windows:  
https://ffmpeg.org/download.html

## 2. API Key
You can get an API key by making an account at https://computerender.com/account.html
To make your key visible to the python client, you can add it as an environment variable:
```bash
export CR_KEY=sk_your_key_here
```
Or alternatively provide it when initializing the client in the python script:
```python
cr = Computerender("sk_your_key_here")
```

## 3. Running the script 
It is a good idea to first create a short, trimmed version of your video that's just a few frames.
This will be helpful for tuning parameters to get the right amount of modification to your video.
Most importantly, the "strength" parameter will determine how much influence the effect has.
The angle and zoom parameters control the speed of the zooming effect.

Run the script:
```bash
python spin-zoom.py
```

## 4. Post processing
To produce the final output, the video was imported into adobe premiere and slowed using "optical flow" as the frame interpolation. It may be possible to achieve the same effect using opencv, but that is not covered in this tutorial.
