
import json
import time
from pathlib import Path

MASKS = None
FILE_PATH = ""
FOLDER_PATH = ""
IMPORT_FOLDER_PATH = "import_nrrd"
EXPORT_FOLDER_PATH = "export_data"
CASE_NAMES = []


def check_file_exist(directory, filename):
    cwd = Path.cwd()
    filepath = cwd / 'import_nrrd'/ directory/ filename
    if filepath.exists:
        return True
    else:
        return False


def get_all_folder_names(directory, subdirectory=""):
    cwd = Path.cwd()
    folder_path = cwd / directory / subdirectory
    folder_names = []
    for subfolder in folder_path.glob("*"):
        if subfolder.is_dir():
            folder_names.append(subfolder.name)  
    return folder_names


def get_all_file_names(directory, subdirectory=""):
    cwd = Path.cwd()
    folder_path = cwd / directory / subdirectory
    file_names = []
    for file_path in folder_path.glob("*.nrrd"):
        if file_path.is_file():
            file_names.append(file_path.name)
    sorted_files_names = sorted(file_names)
    return sorted_files_names


def check_mask_json_file(directory, subdirectory, filename):
    cwd = Path.cwd()
    folder_path = cwd / directory / subdirectory
    # check the folder is exist or not
    if not folder_path.exists():
        folder_path.mkdir(parents=True)
        return False
    else:
        # check the mask json file is exist or not
        file_path = cwd / directory / subdirectory / filename
        if not file_path.exists():
            return False
        else:
            return True

def find_frist_nrrd(folder):
    """
    :param folder:
    :return: the first nrrd file path
    """
    first_file = next(Path(folder).glob("*.nrrd"), None)
    if first_file is not None:
        return first_file
    else:
        return ""


def write_data_to_json(directory, subdirectory, masks):
    global MASKS
    global FILE_PATH
    global FOLDER_PATH
    cwd = Path.cwd()
    FOLDER_PATH = cwd / directory / subdirectory
    file_path = FOLDER_PATH / "mask.json"
    FILE_PATH = file_path
    MASKS = masks
    saveMaskData()



def replace_data_to_json(directory, subdirectory, slice):
    cwd = Path.cwd()
    file_path = cwd / directory / subdirectory / "mask.json"
    index = slice.sliceId
    if file_path.exists():
        # Open the JSON file in read mode
        # with open(file_path, 'r') as f:
        #     # Load the JSON data from the file into a Python object
        #     masks = json.load(f)
        masks = getMaskData(file_path)
        masks[index]["data"] = slice.mask
        # with open(file_path, "w") as file:
        #     json.dump(masks, file)


def getMaskData(path):
    global MASKS
    global FILE_PATH
    FILE_PATH = path
    if MASKS is None:
        with open(path, 'rb') as file:
            # Load the JSON data from the file into a Python object
            # MASKS = json.load(file)
            MASKS = json.loads(file.read().decode('utf-8'))
    return MASKS


def saveMaskData():
    global MASKS
    global FILE_PATH
    with open(FILE_PATH, "wb") as file:
        # json.dump(MASKS, file)
        file.write(json.dumps(MASKS).encode('utf-8'))
    MASKS = None

def save():
    global MASKS

    start_time = time.time()
    if MASKS is not None:
        saveMaskData()
    end_time = time.time()
    run_time = end_time - start_time
    print("save json cost：{:.2f}s".format(run_time))