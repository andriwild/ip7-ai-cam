# Source: https://github.com/hailo-ai/Hailo-Application-Code-Examples

#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path
import numpy as np
import queue
import threading
from PIL import Image
from typing import List
import time

from inference.hailo.object_detection_utils import ObjectDetectionUtils

# Add the parent directory to the system path to access utils module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from hailo.utils import HailoAsyncInference, load_input_images, validate_images, divide_list_to_batches


def enqueue_images(
    images: List[Image.Image], 
    batch_size: int, 
    input_queue: queue.Queue, 
    width: int, 
    height: int, 
    utils: ObjectDetectionUtils
) -> None:
    """
    Preprocess and enqueue images into the input queue as they are ready.

    Args:
        images (List[Image.Image]): List of PIL.Image.Image objects.
        input_queue (queue.Queue): Queue for input images.
        width (int): Model input width.
        height (int): Model input height.
        utils (ObjectDetectionUtils): Utility class for object detection preprocessing.
    """
    for batch in divide_list_to_batches(images, batch_size):
        processed_batch = []
        batch_array = []
        
        for image in batch:
            processed_image = utils.preprocess(image, width, height)
            processed_batch.append(processed_image)
            batch_array.append(np.array(processed_image))
        
        input_queue.put(processed_batch)

    input_queue.put(None)  # Add sentinel value to signal end of input


def process_output(
    output_queue: queue.Queue, 
    output_path: Path, 
    width: int, 
    height: int, 
    utils: ObjectDetectionUtils
) -> None:
    """
    Process and visualize the output results.

    Args:
        output_queue (queue.Queue): Queue for output results.
        output_path (Path): Path to save the output images.
        width (int): Image width.
        height (int): Image height.
        utils (ObjectDetectionUtils): Utility class for object detection visualization.
    """
    image_id = 0
    while True:
        result = output_queue.get()
        if result is None:
            break  # Exit the loop if sentinel value is received
        
        processed_image, infer_results = result
        detections = utils.extract_detections(infer_results[0])
        utils.visualize(
            detections, processed_image, image_id, 
           output_path.as_posix(), width, height
        )
        image_id += 1
    
    output_queue.task_done()  # Indicate that processing is complete


def infer(
    images: List[Image.Image], 
    net_path: str, 
    labels_path: str, 
    batch_size: int, 
    output_path: Path,
    postprecessing: bool = True
):
    """
    Initialize queues, HailoAsyncInference instance, and run the inference.

    Args:
        images (List[Image.Image]): List of images to process.
        net_path (str): Path to the HEF model file.
        labels_path (str): Path to a text file containing labels.
        batch_size (int): Number of images per batch.
        output_path (Path): Path to save the output images.
    """
    utils = ObjectDetectionUtils(labels_path)
    
    input_queue = queue.Queue()
    output_queue = queue.Queue()

    
    hailo_inference = HailoAsyncInference(
        net_path, input_queue, output_queue, batch_size
    )
    height, width, _ = hailo_inference.get_input_shape()

    enqueue_thread = threading.Thread(
        target=enqueue_images, 
        args=(images, batch_size, input_queue, width, height, utils)
    )
    process_thread = threading.Thread(
        target=process_output, 
        args=(output_queue, output_path, width, height, utils)
    )
    
    enqueue_thread.start()
    if postprecessing:
        process_thread.start()
    
    start = time.perf_counter()
    hailo_inference.run()
    end = time.perf_counter()

    enqueue_thread.join()
    output_queue.put(None)  # Signal process thread to exit
    if postprecessing:
        process_thread.join()

    return end - start
