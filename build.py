import subprocess


def build_executable():
    subprocess.run([
        "pyinstaller",
        "--name=CodeDiary",
        "--windowed",
        "--icon=assets/CodeDiary.ico",
        "--add-data", ".env:.",
        "--add-data", "utils/prompt_template.md:utils",
        "--add-data", "utils/config.ini:.",
        "main.py"
    ])

    print(f"Executable built successfully.")
    return new_version


if __name__ == "__main__":
    build_executable()
