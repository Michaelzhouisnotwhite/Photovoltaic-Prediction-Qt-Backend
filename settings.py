import os
SETTING_DIR = os.path.abspath(os.path.dirname(__file__))
WORKSPACE_DIR = SETTING_DIR

__DB_DIR__ = os.path.join(SETTING_DIR, "./db")

__USER_DATASET_DIR__ = os.path.join(SETTING_DIR, "./db/user_dataset")

__USER_CONFIG_FILE_NAME__ = "config.json"

__RESULT_DIR__ = os.path.join(__DB_DIR__, "./results")

__CHECKPOINTS_DIR__ = os.path.join(__DB_DIR__, "./checkpoints")

class __DEV_ENV__:
    namespace_ignored = ["dataset01", "michael", "test01" ,"Michael"]
