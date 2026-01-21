import cv2
import numpy as np
import easyocr
import os
from typing import List, Dict, Any, Tuple

class Layer:
    def __init__(self, type: str, content: Any, bbox: List[int], style: Dict[str, Any]):
        self.type = type # "text" or "object"
        self.content = content
        self.bbox = bbox # [x, y, w, h]
        self.style = style

class DecomposedAsset:
    def __init__(self, background_path: str, layers: List[Layer]):
        self.background_path = background_path
        self.layers = layers
    
    def to_dict(self):
        return {
            "background_path": self.background_path,
            "layers": [{
                "type": l.type,
                "content": l.content,
                "bbox": l.bbox,
                "style": l.style
            } for l in self.layers]
        }

class ImageDecomposer:
    """
    Intelligent layer separation service.
    Uses EasyOCR for text detection and MobileSAM for generic segmentation.
    """
    def __init__(self):
        print("DEBUG: Initializing ImageDecomposer...")
        print("DEBUG: Initializing EasyOCR Reader...")
        self.reader = easyocr.Reader(['en']) 
        print("DEBUG: Initializing MobileSAM...")
        try:
            # Lazy import to avoid OpenCV conflicts
            from ultralytics import SAM
            # Ultralytics SAM wrapper downloads mobile_sam.pt automatically
            self.model = SAM("mobile_sam.pt") 
            print("DEBUG: MobileSAM Model Loaded.")
        except Exception as e:
            print(f"DEBUG: SAM Init Failed: {e}")
            self.model = None

    def decompose(self, image_path: str) -> DecomposedAsset:
        print(f"DEBUG: Decomposing {image_path}...")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # 1. Read Image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not decode image")
            
        layers: List[Layer] = []
        mask_accumulator = np.zeros(img.shape[:2], dtype=np.uint8)
        
        # 2. Extract Text First (Text is usually top layer)
        print("DEBUG: Step 1 - Extract Text")
        # capture the specific mask of text areas
        text_structure_mask = np.zeros(img.shape[:2], dtype=np.uint8)
        img_no_text = self._extract_text(img, image_path, layers, mask_accumulator, text_structure_mask)
        
        # 3. Extract Objects (from image with text removed)
        if self.model:
            print("DEBUG: Step 2 - Extract Objects (MobileSAM)")
            # Pass the text mask so we can ignore objects that are actually text
            img_clean_bg = self._extract_objects(img_no_text, image_path, layers, mask_accumulator, text_structure_mask)
        else:
            img_clean_bg = img_no_text

        # 4. Save Final Background
        dir_name = os.path.dirname(image_path)
        base_name = os.path.basename(image_path)
        bg_filename = f"bg_{base_name}"
        bg_path = os.path.join(dir_name, bg_filename)
        cv2.imwrite(bg_path, img_clean_bg)

        print(f"DEBUG: Decomposition Complete. Layers: {len(layers)}")
        return DecomposedAsset(bg_filename, layers)

    def _extract_text(self, img, image_path, layers, mask_accumulator, text_structure_mask):
        """Finds text, creates layers, and returns image with text removed."""
        try:
            # Pass GRAYSCALE numpy array to avoid shape unpacking errors (3 dims vs 2 dims)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            results = self.reader.readtext(gray)
            print(f"DEBUG: Found {len(results)} text blocks.")
        except Exception as e:
            print(f"DEBUG: EasyOCR Failed: {e}")
            return img.copy()

        inpainting_mask = np.zeros(img.shape[:2], dtype=np.uint8)
        
        for (bbox, text, prob) in results:
            top_left = bbox[0]
            bottom_right = bbox[2]
            x = int(top_left[0])
            y = int(top_left[1])
            w = int(bottom_right[0] - x)
            h = int(bottom_right[1] - y)
            
            # Color detection
            roi = img[y:y+h, x:x+w]
            if roi.size > 0:
                avg_2d = np.average(roi, axis=0)
                avg = np.average(avg_2d, axis=0)
                color_hex = "#{:02x}{:02x}{:02x}".format(int(avg[2]), int(avg[1]), int(avg[0]))
            else:
                color_hex = "#ffffff"

            layers.append(Layer(
                type="text",
                content=text,
                bbox=[x, y, w, h],
                style={"color": color_hex, "fontSize": int(h * 0.8)}
            ))
            
            cv2.rectangle(inpainting_mask, (x, y), (x+w, y+h), 255, -1)
            cv2.rectangle(mask_accumulator, (x, y), (x+w, y+h), 255, -1)
            # Track EXACT text area for filtering later
            cv2.rectangle(text_structure_mask, (x, y), (x+w, y+h), 255, -1)
            
        if layers:
             kernel = np.ones((3,3), np.uint8)
             dilated_mask = cv2.dilate(inpainting_mask, kernel, iterations=2)
             return cv2.inpaint(img, dilated_mask, 3, cv2.INPAINT_NS)
        return img.copy()

    def _extract_objects(self, img, image_path, layers, mask_accumulator, text_structure_mask):
        """Use MobileSAM to segment generic objects."""
        print("DEBUG: Running MobileSAM Inference...")
        try:
            # Check image
            print(f"DEBUG: Image shape: {img.shape}, dtype: {img.dtype}")
            
            # Run inference
            print("DEBUG: Calling self.model()...")
            results = self.model(img, verbose=False)
            print("DEBUG: Inference returned.")
            
            result = results[0]
            print("DEBUG: Got result object.")
        except Exception as e:
             print(f"DEBUG: SAM Inference Failed: {e}")
             import traceback
             traceback.print_exc()
             return img.copy()

        dir_name = os.path.dirname(image_path)
        base_name = os.path.basename(image_path)
        
        inpainting_mask = np.zeros(img.shape[:2], dtype=np.uint8)
        
        try:
            if result.masks:
                print(f"DEBUG: Found {len(result.masks)} masks.")
                # Iterate through masks. Note: SAM can return A LOT of small masks.
                # We might want to filter by size or confidence if needed.
                for i, mask in enumerate(result.masks.data):
                    # Mask might be bool or float. Ensure uint8 for OpenCV.
                    mask_np = mask.cpu().numpy()
                    if mask_np.dtype == bool:
                        mask_np = mask_np.astype(np.uint8) * 255
                    
                    mask_resized = cv2.resize(mask_np, (img.shape[1], img.shape[0]))
                    binary_mask = (mask_resized > 127).astype(np.uint8) * 255

                    # --- OVERLAP CHECK ---
                    # Calculate overlapping pixels with known text
                    overlap = cv2.bitwise_and(binary_mask, text_structure_mask)
                    overlap_pixels = cv2.countNonZero(overlap)
                    mask_pixels = cv2.countNonZero(binary_mask)
                    
                    if mask_pixels > 0:
                        overlap_ratio = overlap_pixels / mask_pixels
                        if overlap_ratio > 0.15: # If >15% matches text, assume it IS the text
                            print(f"DEBUG: Skipping Object {i} (Overlap {overlap_ratio:.2f}) - likely text.")
                            continue

                    
                    # Get BBox using robust findContours
                    try:
                        cnts = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        contours = cnts[0] if len(cnts) == 2 else cnts[1]
                    except Exception as e:
                        print(f"DEBUG: findContours error: {e}")
                        continue
                    
                    if not contours: continue
                    x, y, w, h = cv2.boundingRect(contours[0])
                    
                    # Filter tiny noise masks
                    if w < 10 or h < 10: continue

                    # Cut Object (BGRA)
                    obj_roi = img[y:y+h, x:x+w]
                    mask_roi = binary_mask[y:y+h, x:x+w]
                    
                    # Add Alpha channel
                    b, g, r = cv2.split(obj_roi)
                    rgba = [b, g, r, mask_roi]
                    obj_rgba = cv2.merge(rgba, 4)
                    
                    # Save Object Layer
                    obj_filename = f"sam_obj_{i}_{base_name}.png"
                    obj_path = os.path.join(dir_name, obj_filename)
                    
                    cv2.imwrite(obj_path, obj_rgba)
                    
                    # SAM doesn't give class names, just "Segment"
                    label = f"Object {i+1}"
                    
                    layers.append(Layer(
                        type="object",
                        content=obj_filename,
                        bbox=[x, y, w, h],
                        style={"label": label}
                    ))
                    
                    inpainting_mask = cv2.bitwise_or(inpainting_mask, binary_mask)
            else:
                print("DEBUG: No masks found by SAM.")
        except Exception as e:
            print(f"DEBUG: Error processing masks: {e}")
            import traceback
            traceback.print_exc()
        
        # Inpaint Objects
        if len(layers) > 0:
             print("DEBUG: Inpainting objects...")
             kernel = np.ones((5,5), np.uint8)
             dilated_mask = cv2.dilate(inpainting_mask, kernel, iterations=3)
             return cv2.inpaint(img, dilated_mask, 3, cv2.INPAINT_NS)
        
        return img.copy()
