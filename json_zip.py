import zipfile
import os

def create_test_submissions_zip():
    # Define the directory containing your real or dummy JSON files
    json_dir = "data/raw/submissions/"

    # Define the output zip file name (created in current working directory)
    zip_path = "test_submissions.zip"

    # Create the zip archive
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name in os.listdir(json_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(json_dir, file_name)
                # Important: flatten the structure inside the ZIP
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname=arcname)

    print(f"✅ Successfully created {zip_path} with contents from {json_dir}")

if __name__ == "__main__":
    create_test_submissions_zip()
