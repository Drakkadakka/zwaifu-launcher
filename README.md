# Z-Waifu Launcher

A powerful Python GUI launcher for managing Oobabooga, Z-Waifu, Ooba-LLaMA, and RVC processes with advanced features, dark/light mode, and system tray support.

---

## Features
- Multi-tab GUI for process management
- Real-time output and logging
- System tray integration
- Dark mode and light mode toggle
- Batch file auto-detection and configuration
- Custom arguments and settings
- Robust error handling

---

## Requirements
- **Windows 10/11**
- **Python 3.8+** (https://www.python.org/downloads/)
- (Optional) Oobabooga, Z-Waifu, Ooba-LLaMA, and RVC batch files

---

## Quick Start

1. **Clone or Download this Repository**
   - Download as ZIP and extract, or use:
     ```
     git clone https://github.com/Drakkadakka/zwaifu-launcher.git
     ```

2. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation.

3. **Run the Setup Script**
   - Double-click `setup_venv_and_run_launcher.bat` in the project folder.
   - This will:
     - Create a virtual environment (`venv`)
     - Install all required dependencies
     - Launch the GUI

4. **Configure Batch Files**
   - Use the GUI to browse and select your Oobabooga, Z-Waifu, Ooba-LLaMA, and RVC batch files.
   - Save your configuration for future launches.

5. **Switch Themes**
   - Go to the Settings tab and use the Dark Mode or Light Mode buttons.

---

## Troubleshooting
- If you see errors about missing modules, make sure you ran the setup batch file and have Python 3.8+ installed.
- If the launcher doesn't start, check for error messages in the console or `launcher_error.log`.
- Make sure your batch files exist and are correctly selected in the GUI.
- For tray icon issues, ensure `launcher_icon.png` is present, or a blank icon will be used.

---

## Updating
- To update dependencies, run:
  ```
  venv\Scripts\pip install -r requirements.txt
  ```
- To update the launcher, pull the latest code and re-run the setup batch file.

---

## About the Author

**Drakkadakka**  
[GitHub: Drakkadakka](https://github.com/Drakkadakka)  
Email: Drakkadakka@users.noreply.github.com  

I strim and dabble with development in C#, F#, TypeScript, HTML, and Python. 

- [Twitch: youtubbi](https://www.twitch.tv/youtubbi)
- [GitHub Profile](https://github.com/Drakkadakka)

If you have questions, feature requests, or want to contribute, open an issue or pull request on GitHub!

---

## License
MIT (see LICENSE file) 
