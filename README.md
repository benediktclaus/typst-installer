# Typst Local Package Installer

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/DEIN-USERNAME/DEIN-REPO?style=for-the-badge)](https://github.com/DEIN-USERNAME/DEIN-REPO/releases/latest)
[![GitHub license](https://img.shields.io/github/license/DEIN-USERNAME/DEIN-REPO?style=for-the-badge)](https://github.com/DEIN-USERNAME/DEIN-REPO/blob/main/LICENSE)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge)

A simple Windows utility to automatically download and install the latest release of a Typst package from GitHub.


## 🚀 Download & Installation

The easiest way to use this tool is to download the latest `.exe` file from the **Releases** page.

**[Go to Latest Release](https://github.com/DEIN-USERNAME/DEIN-REPO/releases/latest)**

No installation is needed. Just download and run the file.

## 🖥️ How to Use

1.  Run the downloaded `Typst-Installer.exe`.
2.  Go to the GitHub repository of the Typst package you want to install (e.g., `https://github.com/benediktclaus/letter`).
3.  Copy the URL from your browser's address bar.
4.  Paste the URL into the application's input field.
5.  Click the "Download & Install" button.
6.  Done! The package is now installed in your Typst local package directory and ready to be used.

## 🤔 Why This Tool Exists

Installing a local Typst package from GitHub manually requires several steps:

1.  Find the GitHub repository.
2.  Go to the "Releases" tab.
3.  Download the "Source code (zip)" file.
4.  Unzip the file.
5.  Inside, you'll find a folder with a name like `username-reponame-commit_hash`.
6.  You must **rename** this inner folder to just `reponame`.
7.  You must find your Typst package directory, which is hidden at `%APPDATA%\typst\packages\local`.
8.  You must move the renamed folder into that directory.

This tool automates all 8 steps into two: **Copy-Paste** and **Click**.


## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.