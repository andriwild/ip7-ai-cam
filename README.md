
# IP7 ML Cam

IP7 ML Cam is a modular and extensible application designed for processing video streams using machine learning. The application allows integration of various video sources, application of processing pipelines, and output of results to different sinks.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Directory Structure](#directory-structure)
- [Extensibility](#extensibility)
- [Configuration Example](#configuration-example)
- [Web-Based Configuration Interface](#web-based-configuration-interface)

## Installation

1. **Clone the Repository**:

```bash
git clone https://github.com/andriwild/ip7-ai-cam.git
cd ip7-ai-cam
```

2. **Create and Activate a Virtual Environment**:

```bash
python3 -m venv .venv
source .venv/bin/activate
```
3. Install Dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The application is controlled via a YAML configuration file. An example of such a file can be found in the Configuration Example section. Adjust the configuration according to your hardware and requirements.

## Running the Application
Directory Structure
The application is modular and follows a clear directory structure:

source: Contains the base class for sources and implementations for various video sources.
operation: Contains the base class for processing operations and specific implementations.
sink: Contains the base class for sinks and various output implementations.
resources: Contains models, images, and other resources.
Ensure that the configuration file is set up correctly, then start the application with the following command:
```bash
python3 app.py -config config.yml
```

## Directory Structure

The application is modular and follows a clear directory structure:

- **source**: Contains the base class for sources and implementations for various video sources.
- **operation**: Contains the base class for processing operation and specific implementations.
- **sink**: Contains the base class for sinks and various output implementations.
- **resources**: Contains models, images, and other resources.
- **static**: Contains files for the servers (html, css, js).




## Extensibility
The application is designed for easy extensibility. To add a new source, pipeline, or sink, create a new implementation that inherits from the appropriate base class and place it in the respective impl subdirectory. Ensure that the new implementation is referenced in the configuration file.

## Configuration Example

Below is an example of a configuration file (config.yml):
```yaml
sources:
  - name: webcam
    file_path: ./source/impl/webcam.py
    class_name: Webcam
    parameters:
      device: "/dev/video0"
      width: 640
      height: 640

operations:
  - name: Mitwelten Pipeline (NCNN)
    class_name: Mitwelten
    file_path: ./operation/impl/mitwelten_ncnn.py
    parameters:
      flower_params:
        confidence_threshold: 0.6
        label_path: ./resources/labels/flower.txt
        param_file: ./resources/ml_models/flower_n_sim.ncnn.param
        bin_file: ./resources/ml_models/flower_n_sim.ncnn.bin
        use_gpu: False
        num_threads: 4
      pollinator_params:
        model_path: ./resources/ml_models/yolov8n_pollinator_ep50_v1_ncnn_model
        label_path: ./resources/labels/pollinator.txt
        confidence_threshold: 0.2

sinks:
  - name: console
    class_name: Console
    file_path: ./sink/impl/console.py
```
In this configuration, parameters are passed to the respective classes. Adjust the parameters according to the specific requirements of each implementation.

## Web-Based Configuration Interface

The application offers a web-based configuration interface, which runs by default on port `8001`. You can access it by navigating to `http://localhost:8001` in your browser. Ensure that the port is open in your firewall and that no other services are using this port.
