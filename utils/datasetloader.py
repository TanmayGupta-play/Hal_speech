import os
import json
import numpy as np
from torch.utils.data import Dataset

# ----------------------------------
# Configurable Feature Directories
# ----------------------------------
BASE_FEATURE_DIR = "data/features"

# VAD
VAD_TRIGGER_RAW = os.path.join(BASE_FEATURE_DIR, "vad", "trigger", "raw")
VAD_TRIGGER_AUG = os.path.join(BASE_FEATURE_DIR, "vad", "trigger", "augmented")
VAD_NOISE = os.path.join(BASE_FEATURE_DIR, "vad", "noise")

# Trigger
TRIGGER_TRIGGER_RAW = os.path.join(BASE_FEATURE_DIR, "trigger", "trigger", "raw")
TRIGGER_TRIGGER_AUG = os.path.join(BASE_FEATURE_DIR, "trigger", "trigger", "augmented")
TRIGGER_COMMAND_RAW = os.path.join(BASE_FEATURE_DIR, "trigger", "command", "raw")
TRIGGER_COMMAND_AUG = os.path.join(BASE_FEATURE_DIR, "trigger", "command", "augmented")

# ASR
ASR_COMMAND_RAW = os.path.join(BASE_FEATURE_DIR, "asr", "raw")
ASR_COMMAND_AUG = os.path.join(BASE_FEATURE_DIR, "asr", "augmented")


# ----------------------------------
# Voice Activity Detection Dataset
# ----------------------------------
class VADDataset(Dataset):
    def __init__(self):
        self.data = []

        # Speech = trigger (positive class)
        for path in [VAD_TRIGGER_RAW, VAD_TRIGGER_AUG]:
            for file in os.listdir(path):
                if file.endswith(".npy"):
                    self.data.append((os.path.join(path, file), 1))

        # Non-speech = noise (negative class)
        for file in os.listdir(VAD_NOISE):
            if file.endswith(".npy"):
                self.data.append((os.path.join(VAD_NOISE, file), 0))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        feature_path, label = self.data[idx]
        features = np.load(feature_path)
        return features.astype(np.float32), label


# ----------------------------------
# Trigger Word Detection Dataset
# ----------------------------------
class TriggerDataset(Dataset):
    def __init__(self):
        self.data = []

        # Positive: Trigger audio
        for path in [TRIGGER_TRIGGER_RAW, TRIGGER_TRIGGER_AUG]:
            for file in os.listdir(path):
                if file.endswith(".npy"):
                    self.data.append((os.path.join(path, file), 1))

        # Negative: Command audio (non-trigger)
        for path in [TRIGGER_COMMAND_RAW, TRIGGER_COMMAND_AUG]:
            for file in os.listdir(path):
                if file.endswith(".npy"):
                    self.data.append((os.path.join(path, file), 0))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        feature_path, label = self.data[idx]
        features = np.load(feature_path)
        return features.astype(np.float32), label


# ----------------------------------
# Automatic Speech Recognition Dataset
# ----------------------------------
class ASRDataset(Dataset):
    def __init__(self, raw=True):
        self.data = []
        data_dir = ASR_COMMAND_RAW if raw else ASR_COMMAND_AUG

        for file in os.listdir(data_dir):
            if file.endswith(".npy"):
                npy_path = os.path.join(data_dir, file)
                txt_path = os.path.join(data_dir, file.replace(".npy", ".txt"))

                if os.path.exists(txt_path):
                    self.data.append((npy_path, txt_path))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        feature_path, label_path = self.data[idx]
        features = np.load(feature_path).astype(np.float32)

        with open(label_path, 'r') as f:
            transcript = f.read().strip()

        return features, transcript