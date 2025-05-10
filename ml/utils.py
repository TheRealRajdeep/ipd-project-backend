# ml/utils.py
import cv2
import numpy as np
import base64
import yaml
from ultralytics import YOLO

RIPENESS_SHELF_LIFE = {
    "freshunripe": "8-10 days",
    "unripe":       "6-7 days",
    "freshripe":    "4-6 days",
    "ripe":         "2-4 days",
    "overripe":     "1-2 days",
    "rotten":       "0 days"
}

_model = None

def load_model(weights_path):
    global _model
    if _model is None:
        _model = YOLO(weights_path)
    return _model

def preprocess_image(image_path, target_size=(640,640)):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image at path: {image_path}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)
    return image

def predict(model, image):
    return model(image)

def postprocess_results(results, image):
    predictions = []
    for result in results:
        boxes     = result.boxes.xyxy.cpu().numpy()
        scores    = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy().astype(int)
        for box, score, cid in zip(boxes, scores, class_ids):
            predictions.append({
                "box": box.tolist(),           # list of floats
                "score": float(score),         # Python float
                "class_id": int(cid)           # Python int
            })
            x1,y1,x2,y2 = box
            cv2.rectangle(image, (int(x1),int(y1)), (int(x2),int(y2)), (0,255,0), 2)
            cv2.putText(image, f"{cid}:{score:.2f}",(int(x1),int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0),2)
    return predictions, image

def image_to_base64(image):
    retval, buffer = cv2.imencode('.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    return base64.b64encode(buffer).decode('utf-8')

def load_class_mapping(yaml_path):
    with open(yaml_path,'r') as f:
        data = yaml.safe_load(f)
    names = data.get("names", [])
    return {i:name for i,name in enumerate(names)}

def predict_banana_ripeness(image_path, weights_path, mapping_path):
    model = load_model(weights_path)
    image = preprocess_image(image_path)
    results = predict(model, image)
    preds, vis_image = postprocess_results(results, image)

    ripeness_mapping = load_class_mapping(mapping_path)
    summary = {}
    for p in preds:
        label = ripeness_mapping.get(p["class_id"], "Unknown")
        summary[label] = summary.get(label,0) + 1

    dominant = max(summary.items(), key=lambda x: x[1])[0]
    shelf    = RIPENESS_SHELF_LIFE.get(dominant, "Unknown")
    img_b64  = image_to_base64(vis_image)

    output = {
        "count": len(preds),
        "ripeness": summary,
        "dominant_ripeness": dominant,
        "shelf_life": shelf,
        "predictions": preds
    }
    return output, img_b64

if __name__ == '__main__':
    w = r'C:\Users\AIML\IPD\IPD FINAL\project\best.pt'
    i = r'C:\Users\AIML\IPD\IPD FINAL\project\ban3.jpg'
    m = r'C:\Users\AIML\data.yaml'
    out, b64 = predict_banana_ripeness(i,w,m)
    print(out)