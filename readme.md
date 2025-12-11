# Car Counter - Image Labeling Tool

## Overview
Machine Learning model using a CNN that counts the number of cars in a traffic camera image. The dataset is manually gathered and manually labeled.

## Project Structure
- `label_server.py` - Main Flask web application server to label the pictures for training  
- `desk_capture.py` - Desktop screenshot capture script to gather the pictures from the New York Department of Transportation  
- `pictures.json` - Metadata file containing information about all captured images  
- `picture/` - Directory containing traffic camera images organized by camera location  
- `labels/` - Directory where labeling data is stored as JSON files  
- `machine_model_training.ipynb` - Main Jupyter notebook (renamed from `main2.ipynb`) used to train and evaluate the CNN model  
- `main.ipynb` - Jupyter notebook (legacy)  
- `models/` - Directory where trained PyTorch model checkpoints are saved (e.g., `car_count_resnet18.pth`)  

## Camera Locations
- 2nd_Ave_49_st  
- Queens_Midtown_Tunnel  
- Queens_Plaza_North  
- E_63_St  
- S_Conduit_Ave_150  

## Technical Details
- **Frameworks**: Flask (labeling UI), PyTorch + Torchvision (model training)  
- **Language**: Python 3.11  
- **Port**: 5000 (bound to `0.0.0.0` for the Flask labeling app)  
- **Model**: ResNet18-based CNN trained as a regression model to predict car counts  
- **Metrics**: MSE, MAE, R², and ROC/AUC for heavy-traffic detection (e.g., cars ≥ 4)  
- **Data Storage**: JSON files for labels and picture metadata; PNG images stored under `picture/`  

## Startup – Model Training Notebook

- **Step 1 – Prepare files**  
  Place your `picture/` folder (with subfolders like `2nd_Ave_49_st`, `Queens_Midtown_Tunnel`, etc.) and your `labels/` folder (with files like `2nd_Ave_49_st_labels.json`) in the project root.  
  Rename `main2.ipynb` to `machine_model_training.ipynb` and keep it in the project root.

- **Step 3 – Install dependencies**  
  Make sure Python 3.11 is installed.  
  From the project root, install the core packages with `pip install torch torchvision numpy pandas pillow scikit-learn matplotlib jupyter`.

- **Step 4 – Run the Jupyter notebook**  
  Start Jupyter Notebook from the project root using `jupyter notebook`.  
  Open `machine_model_training.ipynb`, verify `BASE_PICTURE_DIR = "picture"` and `LABELS_DIR = "labels"`, then run all cells from top to bottom to train the model.

- **Step 5 – Use the trained model**  
  After training, the best model weights are saved to `models/car_count_resnet18.pth`.  
  Inside the notebook, call `predict_cars(image_path)` (for example, `predict_cars("picture/2nd_Ave_49_st/2nd_Ave_49_st_1.png")`) to get the predicted number of cars for any image.
