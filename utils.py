from pickle5 import pickle

def save_object_in_local(object, file_path):
    with open(file_path, "wb") as f:
        pickle.dump(object, f)


def load_object_in_local(file_path):
    with open(file_path, "rb") as f:
        return pickle.load(f)
    