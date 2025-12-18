import os
import shutil

def clear_pvc_dataset():
    """Clear all files inside pvc_dataset directory"""
    dataset_path = "pvc_dataset"
    
    if os.path.exists(dataset_path):
        for filename in os.listdir(dataset_path):
            file_path = os.path.join(dataset_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        print(f"Cleared all files in {dataset_path}")
    else:
        print(f"{dataset_path} directory not found")

if __name__ == "__main__":
    clear_pvc_dataset()