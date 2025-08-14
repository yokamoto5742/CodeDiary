import subprocess


def build_executable():
    subprocess.run([
        "pyinstaller",
        "--name=googledocscopy",
        "--windowed",
        "google_docs_copy.py"
    ])
    print("Executable built successfully.")


if __name__ == "__main__":
    build_executable()
