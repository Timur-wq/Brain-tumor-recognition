# CT scans analizator

A Python desktop application for analyzing brain MRI scans. Select an image to send it to a Roboflow model; the app reports whether an object in the `BrainTumor` class was detected and displays the model's confidence.

> This application is for demonstration and research purposes only. Its output is not a medical diagnosis and must not be used to make treatment decisions.

## Requirements

- Python 3.10 or later
- An internet connection
- A Roboflow API key with access to the model project

## Installation and Setup on Windows

Open PowerShell in the project directory and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a `.env` file based on `.env.example` and add your API key:

```env
ROBOFLOW_API_KEY=your_roboflow_api_key
```

Start the application:

```powershell
python main.py
```

If PowerShell blocks virtual environment activation, allow script execution for the current window only, then activate the environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Do not publish `.env` or share your API key. The `.env` file is excluded from Git.

## Usage

1. Wait for the model-ready status.
2. Select **Choose Image** and open a `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tif`, or `.tiff` file.
3. Select **Analyze** and wait for the result.

Roboflow access is required for analysis. The app displays an error if the model or network is unavailable.

## Dataset and Model

The `Brain_tumor_mri-2/` directory contains a local image dataset and annotations, but the current application does not use it for training or inference. Analysis is performed through Roboflow. `NeuroModel.py` is configured to use workspace `tim-xqpez`, project `brain_tumor_mri`, and model version `1`.

Requests use `confidence=40` and `overlap=30`. The app reports a tumor when the response contains a prediction in the `BrainTumor` class.

## Project Structure

- `main.py` — application entry point.
- `app_ui.py` — Tkinter graphical user interface.
- `NeuroModel.py` — Roboflow connection and prediction handling.
- `requirements.txt` — Python dependencies.
- `.env.example` — API key configuration template.
- `Brain_tumor_mri-2/` — local dataset.
