# betterCam

Turn web cam into a black / white board. Improved version of
[cam_board](https://github.com/kacpertopol/cam_board). The code
was restructured to make adding further features and improvements 
easier.

## dependencied

Requires the python `cv2` library with the ARUCO module. This is available from pip, 
the package name is `opencv-contrib-python`.

## usage

The setup is similar to [cam_board](https://github.com/kacpertopol/cam_board)

![](https://github.com/kacpertopol/cam_board/raw/master/demo.gif)

First print the page with the ARUCO markers. The file `to_print/a4_16_by_9_tiny_inside.pdf`
is prepared for a 16x9 camera aspect ratio. The files in `to_print/symbols/` contain
aruco symbols (made using [this](https://chev.me/arucogen/) link) 
that can be used to prepare printouts for cameras with different aspect ratios.

Next edit the configuration file `betterCam_config`. 
The example provided in the repository contains comments
with the description of configuration variables.

Next run:

```
./betterCam
```

to use the default camera `webcam` or:

```
./betterCam -c externalcam
```

to use the camera with the name `externalcam` (this camera should have a corresponding
section in the configuration file).

Help information is printed out by running:

```
./betterCam -h
```

## keyboard shortcuts

`q` - quit

`s` - save frame to png file

`p` - pause image

`w` - display camera picture directly

`i` - using averaged camera frames, zoom to the inside of ARUCO markers, denoise and invert colors

`d` - using averaged camera frames, zoom to the inside of ARUCO markers, denoise

`o` - using regular camera frames, zoom to the inside of ARUCO markers, denoise and invert colors

`f` - using regular camera frames, zoom to the inside of ARUCO markers, denoise

`+` - increase threshold for denoising

`-` - decrease threshold for denoising


