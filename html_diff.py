#!/usr/bin/python


import os
import re
import sys
import math
from glob import glob
from PIL import Image
from shutil import rmtree
from selenium import webdriver


# Optionally remove intermediate work results as PNG slices
remove_slices = False

make_visual_diff = True

options = webdriver.ChromeOptions()
options.headless = True

#browser = webdriver.Firefox(options=options)
browser = webdriver.Chrome(options=options)

browser.set_window_size(1280, 960)
#browser.fullscreen_window()

image_magick = 'compare'

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
    browser.set_window_size(sz('Width'), sz('Height')) # May need manual adjustment
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
        count +=1


def make_diff(dir_path):
    slice_height = 1024
    slice_dir = '%s/slices' % dir_path

    make_dir(slice_dir)

    cut_to_slices('%s/old-full.png' % dir_path, 'old', slice_dir,  slice_height)
    cut_to_slices('%s/new-full.png' % dir_path, 'new', slice_dir,  slice_height)

    old_slices = glob('%s/slices/old_*.png' % dir_path)
    new_slices = glob('%s/slices/new_*.png' % dir_path)

    i = 0
    for _elm in new_slices:
        i += 1

        old_slice = '%s/slices/old_%s.png' % (dir_path, str(i).zfill(2))
        new_slice = '%s/slices/new_%s.png' % (dir_path, str(i).zfill(2))
        diff_slice = '%s/slices/diff_%s.png' % (dir_path, str(i).zfill(2))

        if old_slice in old_slices and new_slice in new_slices:
            os.system('%s -dissimilarity-threshold 1 -compose difference %s %s %s' % (image_magick, new_slice, old_slice, diff_slice))

    diff_slices = glob('%s/slices/diff_*.png' % dir_path)
    first_slice = Image.open('%s/slices/diff_01.png' %dir_path)
    diff_image = Image.new('RGB', (first_slice.width, slice_height * len(diff_slices) ))

    i = 0
    cur_hgt = 0

    for _elm in diff_slices:
        i += 1
        diff_slice = Image.open('%s/slices/diff_%s.png' % (dir_path, str(i).zfill(2)))
        diff_image.paste(diff_slice, (0, cur_hgt))
        cur_hgt += slice_height

    diff_image.save('%s/diff-full.png' % dir_path)

    if remove_slices:
        rmtree('%s/slices/' % dir_path)


def compare_html(old_file, new_file):
    _name = os.path.splitext(os.path.basename(old_file))[0]

    out_base_dir = '%s/output' % work_dir
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


old_file = sys.argv[1]
new_file = sys.argv[2]
work_dir = sys.argv[3]

compare_html(old_file, new_file)
