#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np

winname = "Spotta Focussing Program"


def setup():
    cv2.destroyAllWindows()
    cv2.namedWindow(winname)
    cv2.moveWindow(winname, 0, 0)


def draw(raw):
    # We have received (presumably!) jpeg data
    print("Received " + str(len(raw)) + " bytes.")
    barray = bytes([int.from_bytes(x, "big") for x in raw])
    with open("img.jpeg", "wb+") as f:
        f.write(barray)
    img = cv2.imread("img.jpeg")
    if img is None:
        print("SYNC ERROR - SKIPPING FRAME!!")
        return
    else:
        width = img.shape[1]
        height = img.shape[0]

        # Crop the image down to remove background
        # crop_top = int(height/14)
        # crop_left = int(width/8)
        # crop_right = width - crop_left
        # img = img[crop_top:, crop_left:crop_right, :]
        # width = img.shape[1]
        # height = img.shape[0]

        # Split the image into bands
        num_bands = 9
        band_height = int(height/num_bands)
        band_starts = [x*band_height for x in list(range(num_bands))]
        band_ends = [y*band_height for y in list(range(1, num_bands+1))]
        bands = [img[x[0]:x[1], :, :] for x in zip(band_starts, band_ends)]
        # https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
        focus_coefficients = [cv2.Laplacian(cv2.cvtColor(x, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var() for x in bands]
        score = round(sum(focus_coefficients))
        if score > 140000:
            result = "PASSED focusing"
        else:
            result = "------"
        print(score, result)
        max_focus = max(float(3000), float(max(focus_coefficients)))
        focus_scale = [min([1.0, x/max_focus]) for x in focus_coefficients]
        overlay_colors = [(0, int(255*(x)), int(255*(1-x))) for x in focus_scale] # BGR
        # Make a bar chart of the focus position
        barchart_width = width
        barchart = np.zeros((height, barchart_width, 3), np.uint8)
        bar_sizes = [barchart_width*x for x in focus_scale]
        for i in range(num_bands):
            bar = [np.array([[0, band_starts[i]], [bar_sizes[i], band_starts[i]], [bar_sizes[i], band_ends[i]], [0, band_ends[i]]], 'int32')]
            cv2.fillPoly(barchart, bar, overlay_colors[i])
            #cv2.putText(img, str(int(focus_coefficients[i])), (5, 25 + band_starts[i]), cv2.FONT_HERSHEY_SIMPLEX, 0.75, overlay_colors[i], 2)
        # Stitch the two images together
        stitched = np.concatenate((img, barchart), axis=1)
        # Draw a line for the target focus
        cv2.line(stitched, (0, height//2), (width + barchart_width, height//2), (255, 0, 0), 2)
        # Draw the arrow instructions box
        instructions = np.zeros((100, width + barchart_width, 3), np.uint8)
        color0 = (0, 255, 255)
        color1 = (255, 255, 0)
        cv2.ellipse(instructions, (50, 50), (25, 25), 90, 0, 270, color0, 2, cv2.LINE_AA)
        cv2.arrowedLine(instructions, (75, 50), (75, 51), color0, 2, cv2.LINE_AA, tipLength=10)
        cv2.arrowedLine(instructions, (100, 75), (100, 25), color0, 2, cv2.LINE_AA)
        cv2.ellipse(instructions, (250, 50), (25, 25), 90, 90, 360, color1, 2, cv2.LINE_AA)
        cv2.arrowedLine(instructions, (225, 50), (225, 51), color1, 2, cv2.LINE_AA, tipLength=10)
        cv2.arrowedLine(instructions, (300, 25), (300, 75), color1, 2, cv2.LINE_AA)
        # Stitch again
        stitched = np.concatenate((stitched, instructions), axis=0)
        cv2.imshow(winname, stitched)
        cv2.waitKey(25)
