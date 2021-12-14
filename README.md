# betterCam

Turn web cam into a black / white board:

![betterCamera](./doc_images/all.gif)

Improved version of
[cam_board](https://github.com/kacpertopol/cam_board). 

## installation

### pip

You can install **betterCamera** using [pip](https://en.wikipedia.org/wiki/Pip_(package_manager)).
Information on the installation and usage of **pip**, on different operating systems, is available [here](https://pip.pypa.io/en/stable/installation/).
and [here](https://pip.pypa.io/en/stable/) respectively.
Many additional resources are available online, see for example [this informative article](https://www.makeuseof.com/tag/install-pip-for-python/).

If you're on *linux* or *mac* open a terminal and run:
```sh
TODO
```
If you're on *windows* open the command line and run:
```sh
TODO
```


### git

If you are familiar with `git` and `python 3` then 
make sure you have the `numpy`, `opencv-python` and `opencv-contrib-python`
libraries installed before cloning the [repository](https://github.com/kacpertopol/betterCamera).
The main script is `betterCamera`.

## usage

The program can be launched from the  terminal:

```
$ betterCamera
```

Control is via keyboard shortcuts. A list of special keys
is available by pressing `h`. To quit the program hit `q`:

![keys](./bcam/info.png)

### quitting

This is important 😀 Just hit `q`.

### getting help

The `h` key activates the help screen:
![betterCamera](./doc_images/0001.png)
with a description of all the special keys.

### displaying the camera picture directly

Hitting `w` just displays the camera picure directly:
![betterCamera](./doc_images/0001.png)

## configuration

The path to a directory containing the configuration file `betterCam_config` is 
displayed at the very bottom of the window
after pressing the `h` key:
![betterCamera](./doc_images/0001_.png)
All configuration is done by modifying this file. 
Don't be afraid to tinker with the settings, if you mess up, just replace `betterCam_config`
with the [default configuration file](./bcam/betterCam_config).

Configuration settings are entered using a simple `key = value` syntax. For example, the
number of buffered perspective matrices, `buffer` can be decreased from the default 20
to 10 by changing:
```
buffer = 20
```
to 
```
buffer=10
```
Each configuration
option is paired with a comment describing the setting.
Comments are lines starting with `#`.
Additionally, 
sections are marked using square brackets, for example `[perspectiveMatrix]`. 
