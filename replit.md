# Car Counter - Image Labeling Tool

## Overview
A Flask-based web application for labeling traffic camera images to count cars. This tool allows users to view images captured from different traffic cameras and label the number of cars visible in each image.

## Project Structure
- `label_server.py` - Main Flask web application server
- `desk_capture.py` - Desktop screenshot capture script (for local use, captures from screen regions)
- `pictures.json` - Metadata file containing information about all captured images
- `picture/` - Directory containing traffic camera images organized by camera location
- `labels/` - Directory where labeling data is stored as JSON files
- `movefiles.py` - Utility script for organizing files
- `main.ipynb` - Jupyter notebook (legacy)

## Camera Locations
- 2nd_Ave_49_st
- Queens_Midtown_Tunnel
- Queens_Plaza_North
- E_63_St
- S_Conduit_Ave_150

## Running the Application
The Flask server runs on port 5000. Access the web interface to:
1. Select a camera/description to label
2. View images and enter car counts
3. Mark images with issues if unreadable

## Technical Details
- **Framework**: Flask
- **Language**: Python 3.11
- **Port**: 5000 (bound to 0.0.0.0)
- **Data Storage**: JSON files for labels and picture metadata
