import sys
sys.path.insert(0, ".")
from core.calibrator import save_calibration
save_calibration({"mode": "none", "scale": 1.0, "offset": 0})
print("Calibration reset to NONE")
