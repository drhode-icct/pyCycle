import os


def old_files_cleaning():
    current_dir = os.getcwd()

    # Remove old view output files
    for file_name in os.listdir(current_dir):
        try:

            if file_name.endswith('.out'):
                file_path = os.path.join(current_dir, file_name)
                os.remove(file_path)
        except OSError as e:
            print(f'Error removing file {file_name}: {e.strerror}')


