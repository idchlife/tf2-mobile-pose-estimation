import os
import sys
from pathlib import Path
from common import load_env_file, is_debug
from logging import log_error


load_env_file()

def is_path_accessible(path_str):
  path = Path(path_str)

  if not path.exists():
    if is_debug():
      log_error(f"Path {path_str} does not exist!")
    return False

  filepath = os.path.join(path_str, ".access_checker")

  # Creating simple file, then removing it
  try:
    Path(filepath).touch(exist_ok=True)

    Path(filepath).unlink()

    return True
  except Exception as e:
    if is_debug():
      log_error(e)
    return False

DATASETS_PATH = os.getenv("DATASETS_PATH", None)
OUTPUT_PATH = os.getenv("OUTPUT_PATH", None)

TRAIN_IMAGES_DIR_PATH = os.path.join(DATASETS_PATH, "train2017")
TRAIN_ANNOTATIONS_JSON_FILEPATH = os.path.join(DATASETS_PATH, "annotations_trainval2017/person_keypoints_train2017.json")

VALID_IMAGES_DIR_PATH = os.path.join(DATASETS_PATH, "val2017")
VALID_ANNOTATIONS_JSON_FILEPATH = os.path.join(DATASETS_PATH, "annotations_trainval2017/person_keypoints_val2017.json")

def stop_execution_if_paths_not_configured():
  to_check = [
    DATASETS_PATH,
    OUTPUT_PATH
  ]

  if not all(to_check):
    raise Exception(
      "PATHS NOT CONFIGURED! Please, configure paths with .env file in the root of the project. You can see example in .env.dist file"
    )

def stop_execution_if_paths_not_accessible():
  to_check = {
    'DATASETS_PATH': DATASETS_PATH,
    'OUTPUT_PATH': OUTPUT_PATH
  }

  for k, v in to_check.items():
    if not is_path_accessible(v):
      raise Exception(f"PATH {k} IS NOT ACCESSIBLE! ( {v} ) Please check whether your user has rights or that path even exists")


def stop_execution_if_datasets_not_downloaded():
  to_check = {
    'TRAIN_IMAGES_DIR_PATH': TRAIN_IMAGES_DIR_PATH,
    'TRAIN_ANNOTATIONS_JSON_FILEPATH': TRAIN_ANNOTATIONS_JSON_FILEPATH,
    'VALID_IMAGES_DIR_PATH': VALID_IMAGES_DIR_PATH,
    'VALID_ANNOTATIONS_JSON_FILEPATH': VALID_ANNOTATIONS_JSON_FILEPATH
  }

  for k, v in to_check.items():
    if not Path(v).exists():
      raise Exception(f"DATASETS PATH DOES NOT EXIST! ( {v} ). Please check, whether your path configured or datasets available there.")


