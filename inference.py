# inference.py
import torch
import numpy as np
from PIL import Image
from torchvision import models, transforms
from ultralytics import YOLO

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------- LOAD MODELS ----------------
def load_models():
    # Fog model (ResNet50 weights → must match training)
    fog_model = models.resnet50(weights=None)
    fog_model.fc = torch.nn.Linear(fog_model.fc.in_features, 2)
    fog_model.load_state_dict(
        torch.load("models/fog_classifier_resnet50.pth", map_location=DEVICE)
    )
    fog_model.eval().to(DEVICE)

    # Accident model (ResNet18)
    accident_model = models.resnet18(weights=None)
    accident_model.fc = torch.nn.Linear(accident_model.fc.in_features, 2)
    accident_model.load_state_dict(
        torch.load("models/accident_classifier_resnet18.pth", map_location=DEVICE)
    )
    accident_model.eval().to(DEVICE)

    # YOLOv8 traffic model
    yolo_model = YOLO("models/Traffic-detection-yolov11.pt")

    return fog_model, accident_model, yolo_model


# ---------------- TRANSFORMS ----------------
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ---------------- PREDICTION FUNCTIONS ----------------
def predict_fog(model, img_pil):
    x = _transform(img_pil).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        pred = model(x).argmax(1).item()
    return ["Clear", "Foggy"][pred]


def predict_accident(model, img_pil):
    x = _transform(img_pil).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        pred = model(x).argmax(1).item()
    return ["Accident", "No Accident"][pred]


def detect_vehicles(yolo_model, img_np):
    results = yolo_model(img_np, conf=0.25, verbose=False)[0]

    counts = {}
    if results.boxes is not None:
        for cls in results.boxes.cls.tolist():
            name = results.names[int(cls)]
            counts[name] = counts.get(name, 0) + 1

    return results, counts
