# Git commit skyline

![example skyline](skyline_example.png "example skyline")

# Usage

## Option 1:

Copy `skyline.py` into whatever repo you want to make the skyline out of and run it with

`$ python3 skyline.py <author> <year>`

## Option 2:

Run skyline in a docker with following command:

`$ docker run -v <path-to-repo-you-want-to-skyline>:/workspace $(docker build -q .) <author> <year>`
