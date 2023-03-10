import os
import json
import time

MASKS = None
FILE_PATH = ""
FOLDER_PATH = ""
IMPORT_FOLDER_PATH = "import_nrrd"
EXPORT_FOLDER_PATH = "export_data"
CASE_NAMES = []


def check_file_exist(directory, filename):
    cwd = os.getcwd()
    filepath = os.path.join(cwd, 'import_nrrd', directory, filename)
    if os.path.exists(filepath):
        return True
    else:
        return False


# not use
def get_real_path(directory, subdirectory, filename):
    cwd = os.getcwd()
    filepath = os.path.join(cwd, directory, subdirectory, filename)
    if os.path.exists(filepath):
        return filepath
    else:
        return ''


def get_all_folder_names(directory, subdirectory=""):
    cwd = os.getcwd()
    folder_path = os.path.join(cwd, directory, subdirectory)
    folder_names = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]
    return folder_names


def get_all_file_names(directory, subdirectory=""):
    cwd = os.getcwd()
    folder_path = os.path.join(cwd, directory, subdirectory)
    items = os.listdir(folder_path)
    for item in items:
        if ('.nrrd' not in item) and ('.json' not in item):
            items.remove(item)

    file_names = [item for item in items if os.path.isfile(os.path.join(folder_path, item))]
    sorted_files_names = sorted(file_names)
    return sorted_files_names


def check_mask_json_file(directory, subdirectory, filename):
    cwd = os.getcwd()
    folder_path = os.path.join(cwd, directory, subdirectory)
    # check the folder is exist or not
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        return False
    else:
        # check the mask json file is exist or not
        file_path = os.path.join(cwd, directory, subdirectory, filename)
        if not os.path.exists(file_path):
            return False
        else:
            return True

def find_frist_nrrd(folder):
    file_list = os.listdir(folder)
    nrrd_list = [filename for filename in file_list if filename.endswith(".nrrd")]
    if len(nrrd_list)>0:
        nrrd_path = os.path.join(folder,nrrd_list[0])
        return nrrd_path
    else:
        return ""


def write_data_to_json(directory, subdirectory, masks):
    global MASKS
    global FILE_PATH
    global FOLDER_PATH
    start_time = time.time()
    cwd = os.getcwd()
    FOLDER_PATH = os.path.join(cwd, directory, subdirectory)
    file_path = os.path.join(FOLDER_PATH,"mask.json")
    # for mask in masks:
    #     base = mask["width"]*mask["height"]*4
    #     mask["data"] = [0] * base
    # with open(file_path, "w") as file:
    #     json.dump(masks, file)
    FILE_PATH = file_path
    MASKS = masks
    saveMaskData()
    end_time = time.time()
    run_time = end_time - start_time
    # print("代码运行时间为：{:.2f}秒".format(run_time))


def replace_data_to_json(directory, subdirectory, slice):
    cwd = os.getcwd()
    file_path = os.path.join(cwd, directory, subdirectory, "mask.json")
    index = slice.sliceId
    if os.path.isfile(file_path):
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