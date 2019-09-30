#!/usr/bin/python

import os
import re
import sys
import math
from glob import glob
from PIL import Image
from shutil import rmtree
from selenium import webdriver


# imagemagik binary
imagemagick = 'compare'

# Optionally remove intermediate work results as PNG slices
remove_slices = False

make_visual_diff = True

options = webdriver.ChromeOptions()
options.headless = True

# browser = webdriver.Firefox(options=options)
browser = webdriver.Chrome(options=options)

window_width = 1280
window_height = 960

# default background color (RGBA):
background_color = (255, 255, 255, 0)

browser.set_window_size(window_width, window_height)
# browser.fullscreen_window()

html_file = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>Visual compare</title>
    <style type="text/css">
        body, div {
            margin:0;
            padding:0;
            border:0;
            outline: 0;
            background: #fff;
            color: #000;
        }

        #new,
        #old,
        #diff {
            width: 100%;
        }

        #old {
            z-index: 1;
        }

        #new {
            z-index: 2;
        }

        #diff {
            z-index: 3;
        }

        #tools {
            background-color: rgba(0, 0, 0, 0.5);
            padding: 5px;
            text-align: center;
            border-bottom: 1px solid darkgrey;
            z-index: 5;
            position: fixed;
            width: 100%;
            font-size: 14px;
            font-weight: 600;
            color: #fff;
        }

        #new_opac,
        #diff_opac {
            width: 4em;
        }

        .image {
            position: absolute;
            top:0;
            left:0;
        }
    </style>
  </head>
  <body>
    <div id="tools">
        <input type="checkbox" id="show_old" checked="checked" /><label for="show_old">Old</label> &nbsp; &nbsp;
        <input type="checkbox" id="show_new" value="New" /><label for="show_new">New</label> <input type="number" id="new_opac" value="100" min="1" max="100" title="Layer opacity" /> &nbsp; &nbsp;
        <input type="checkbox" id="show_diff" value="Diff" /><label for="show_diff">Diff</label> <input type="number" id="diff_opac" value="100"  min="1" max="100" title="Layer opacity" />
    </div>
    <div id="old">
        <img src="old-full.png" alt="Old version" class="image" />
    </div>
    <div id="new">
        <img src="new-full.png" alt="New version" class="image" />
    </div>
    <div id="diff">
        <img src="diff-full.png" alt="Diff" class="image" />
    </div>
    <script type="text/javascript">
        var layerNew = document.getElementById('new');
        var layerOld = document.getElementById('old');
        var layerDiff = document.getElementById('diff');

        var btnNew = document.getElementById('show_new');
        var btnOld = document.getElementById('show_old');
        var btnDiff = document.getElementById('show_diff');

        var opacityNew = document.getElementById('new_opac');
        var opacityDiff = document.getElementById('diff_opac');

        btnNew.onchange = function () {
            if (this.checked) {
                layerNew.style.display = 'block';
            } else {
                layerNew.style.display = 'none';
            };
        };

        btnOld.onchange = function () {
            if (this.checked){
                layerOld.style.display = 'block';
            } else {
                layerOld.style.display = 'none';
            };
        };

        btnDiff.onchange = function () {
            if (this.checked) {
                layerDiff.style.display = 'block';
            } else {
                layerDiff.style.display = 'none';
            };
        };

        opacityNew.onchange = function () {
            layerNew.style.opacity = parseInt(this.value, 10) / 100;
        };

        opacityDiff.onchange = function () {
            layerDiff.style.opacity = parseInt(this.value, 10) / 100;
        };

        var init = function() {
            if (btnOld.checked) {
                layerOld.style.display = 'block';
            } else {
                layerOld.style.display = 'none';
            };

            if (btnNew.checked) {
                layerNew.style.display = 'block';
            } else {
                layerNew.style.display = 'none';
            };

            if (btnDiff.checked) {
                layerDiff.style.display = 'block';
            } else {
                layerDiff.style.display = 'none';
            };

            layerNew.style.opacity = parseInt(opacityNew.value, 10) / 100;
            layerDiff.style.opacity = parseInt(opacityDiff.value, 10) / 100;
        }

        init();
    </script>
  </body>
</html>
"""


def fullpage_screenshot(filename):
    # use in headless mode:
    sz = lambda x: browser.execute_script('return document.body.parentNode.scroll' + x)
    # may need manual adjustment:
    browser.set_window_size(sz('Width'), sz('Height'))
    browser.find_element_by_tag_name('body').screenshot(filename)


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def cut_to_slices(image_path, out_name, out_dir, slice_size):
    """slice an image into parts slice_size tall"""
    img = Image.open(image_path)
    width, height = img.size
    upper = 0
    left = 0
    slices = int(math.ceil(height/slice_size))

    count = 1
    for slice in range(slices):
        # if we are at the end, set the lower bound to be the bottom of the image
        if count == slices:
            lower = height
        else:
            lower = int(count * slice_size)

        bbox = (left, upper, width, lower)
        working_slice = img.crop(bbox)
        upper += slice_size
        slice_name = '%s_%s.png' % (out_name, str(count).zfill(2))
        working_slice.save(os.path.join(out_dir, slice_name))
        count += 1


def equalize_heights(output_dir):
    old_file = '%s/old-full.png' % output_dir
    new_file = '%s/new-full.png' % output_dir
    diff_file = '%s/diff-full.png' % output_dir

    new_image = Image.open(new_file).convert('RGBA')
    old_image = Image.open(old_file).convert('RGBA')

    if (old_image.height > new_image.height):
        temp_image = Image.new('RGBA', (old_image.width, old_image.height), color=background_color)
        temp_image.paste(new_image, (0, 0))
        temp_image.save(new_file, 'PNG')
        max_height = temp_image.height

    elif (old_image.height < new_image.height):
        temp_image = Image.new('RGBA', (new_image.width, new_image.height), color=background_color)
        temp_image.paste(old_image, (0, 0))
        temp_image.save(old_file, 'PNG')
        max_height = temp_image.height

    else:
        max_height = new_image.height

    return max_height


def make_diff(output_dir):
    slice_height = 1024
    slice_dir = '%s/slices' % output_dir

    make_dir(slice_dir)

    max_height = equalize_heights(output_dir)

    cut_to_slices('%s/old-full.png' % output_dir, 'old', slice_dir,  slice_height)
    cut_to_slices('%s/new-full.png' % output_dir, 'new', slice_dir,  slice_height)

    old_slices = glob('%s/slices/old_*.png' % output_dir)
    new_slices = glob('%s/slices/new_*.png' % output_dir)

    i = 0
    for _elm in new_slices:
        i += 1

        old_slice = '%s/slices/old_%s.png' % (output_dir, str(i).zfill(2))
        new_slice = '%s/slices/new_%s.png' % (output_dir, str(i).zfill(2))
        diff_slice = '%s/slices/diff_%s.png' % (output_dir, str(i).zfill(2))

        if old_slice in old_slices and new_slice in new_slices:
            os.system('%s -dissimilarity-threshold 1 -compose difference %s %s %s' % (imagemagick, new_slice, old_slice, diff_slice))

    diff_slices = glob('%s/slices/diff_*.png' % output_dir)
    first_slice = Image.open('%s/slices/diff_01.png' % output_dir)
    diff_image = Image.new('RGB', (first_slice.width, max_height))

    i = 0
    cur_hgt = 0

    for _elm in diff_slices:
        i += 1
        diff_slice = Image.open('%s/slices/diff_%s.png' % (output_dir, str(i).zfill(2)))
        diff_image.paste(diff_slice, (0, cur_hgt))
        cur_hgt += diff_slice.height

    diff_image.save('%s/diff-full.png' % output_dir)

    if remove_slices:
        rmtree('%s/slices/' % output_dir)


def compare_html(old_file, new_file, output_dir):
    _name = os.path.splitext(os.path.basename(old_file))[0]

    out_base_dir = '%s/output' % output_dir
    make_dir(out_base_dir)

    out_dir = '%s/%s' % (out_base_dir, _name)
    make_dir(out_dir)

    browser.get('file://%s' % old_file)

    old_png = '%s/old-full.png' % out_dir
    new_png = '%s/new-full.png' % out_dir

    fullpage_screenshot(old_png)

    browser.get('file://%s' % new_file)

    fullpage_screenshot(new_png)

    index_html = open('%s/index.html' % out_dir, 'w')
    index_html.write(html_file)
    index_html.close()

    if make_visual_diff:
        make_diff(out_dir)


def main():
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    output_dir = sys.argv[3]

    compare_html(old_file, new_file, output_dir)


if __name__ == '__main__':
    main()
