import ultralytics
import cv2
import easyocr
import numpy as np

print(f"OpenCV Version: {cv2.__version__}")
try:
    reader = easyocr.Reader(['en'], verbose=False)
    print("EasyOCR initialized.")
    # Create dummy image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.putText(img, "Test", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imwrite("test_gen.png", img)
    
    print("Running readtext...")
    result = reader.readtext("test_gen.png")
    print(f"Result: {result}")
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
