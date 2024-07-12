#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np

winname = "Spotta Focussing Program"
threshold = 21000


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

        # Split the image into bands
        num_bands = 9
        band_height = int(height/num_bands)
        band_starts = [x*band_height for x in list(range(num_bands))]
        band_ends = [y*band_height for y in list(range(1, num_bands+1))]
        bands = [img[x[0]:x[1], :, :] for x in zip(band_starts, band_ends)]
        # https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
        focus_coefficients = [cv2.Laplacian(cv2.cvtColor(x, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var() for x in bands]
        score = round(sum(focus_coefficients))
        passed = score >= threshold
        result = "PASSED" if passed else "FAIL"
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
        footer = np.zeros((100, width + barchart_width, 3), np.uint8)
        red = (0, 0, 255)  # BGR
        green = (0, 255, 0)  # BGR
        cv2.putText(
            img=footer,
            text=f"{score:6} / {threshold} is required. {result}",
            org=(10, 60),
            fontFace=cv2.FONT_HERSHEY_DUPLEX,
            fontScale=0.75,
            color=green if passed else red,
            thickness=1
        )
        # Stitch again
        stitched = np.concatenate((stitched, footer), axis=0)
        cv2.imshow(winname, stitched)
        cv2.waitKey(25)
