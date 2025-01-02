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

