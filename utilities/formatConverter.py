import numpy as np
import cv2
from model.detection import Box

def yxyx_to_xywhn(bbox, image_width, image_height):
    """
    Converts a bounding box from yxyx format to xywhn format.

    Parameters:
    bbox (tuple or list): Bounding box in yxyx format (y1, x1, y2, x2).
    image_width (int): Width of the image.
    image_height (int): Height of the image.

    Returns:
    tuple: Bounding box in xywhn format (cx, cy, w, h), normalized to [0, 1].
    """
    y1, x1, y2, x2 = bbox

    # Calculate center, width, and height in absolute coordinates
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    w = x2 - x1
    h = y2 - y1

    # Normalize to [0, 1]
    cx /= image_width
    cy /= image_height
    w /= image_width
    h /= image_height

    return (cx, cy, w, h)


def yxyxn_to_xywhn(y0, x0, y1, x1):
    width = x1 - x0
    height = y1 - y0
    cx = x0 + width / 2
    cy = y0 + height / 2
    return (cx, cy, width, height)

def convert_xywh_to_xywhn(xywh, frame_width, frame_height):
    x_left, y_top, width, height = xywh
    
    x_center = x_left + (width / 2)
    y_center = y_top + (height / 2)

    x_center_norm = x_center / frame_width
    y_center_norm = y_center / frame_height
    width_norm = width / frame_width
    height_norm = height / frame_height

    return [x_center_norm, y_center_norm, width_norm, height_norm]



def letterbox(img: np.ndarray, new_shape=(640, 640), color=(114, 114, 114)):
    # Keep aspect ratio
    h0, w0 = img.shape[:2]
    w, h = new_shape
    r = min(w / w0, h / h0)
    nw, nh = int(round(w0 * r)), int(round(h0 * r))
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
    dw, dh = w - nw, h - nh
    top, bottom = dh // 2, dh - dh // 2
    left, right = dw // 2, dw - dw // 2
    return cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color), r, (left, top)


def crop(box: Box, frame: np.ndarray) -> np.ndarray:

    height, width = frame.shape[:2]
    x_center, y_center, w, h = box.xywhn

    # Convert normalized coordinates to pixel coordinates
    x1 = int((x_center - w / 2) * width)
    y1 = int((y_center - h / 2) * height)
    x2 = int((x_center + w / 2) * width)
    y2 = int((y_center + h / 2) * height)

    # Clip coordinates to image boundaries
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(width, x2), min(height, y2)

    # Crop the image region
    cropped_image = frame[y1:y2, x1:x2]

    return cropped_image



