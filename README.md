# Experimental Platform - Multimodal LLM in Road Safety

# Table of Contents
- [Project Description](#project-description)
- [Features](#features)
- [Configuration and Installation](#configuration-and-installation)
- [Usage](#usage)
- [Testing](#testing)
- [Contributors](#contributors)
- [License](#licence)
- [Acknowledgements](#acknowledgements)


# Project Description
This project aims to implement red teaming techniques on large language models (LLMs) to evaluate their response accuracy and decision-making capabilities in road safety-related scenarios. The focus is to process both images and videos, apply filters and overlays, and assess LLM performance.

This document provides a brief overview of how to use the program for various use cases. The script supports different commands and options for various LLMs (ChatGPT, Gemini, Claude) to process and analyse supported input files

# Features
- Command Line Interface (CLI) for image and video processing.
- Supports multiple LLM models including ChatGPT, Gemini and Claude.
- Applies image processing techniques such as overlays (fog, graffiti) and filters (blur, brightness).
- Batch processing of images and videos.
- JSON and CSV output formats for LLM responses.
- Automatic cleanup of generated files to manage storage.
- User-defined prompts for flexible data extraction and testing.

# Configuration and Installation

### Requirements
- Operating System: Windows, MacOS, Ubuntu - Ubuntu Recommended 
- GitHub Account
- Python Version 3.8 and above

### Steps
1. Clone the Github repository:
    ```
    git clone https://github.com/23348918/CITS3200-Group37
    ```
2. From root of directory, create virtual environment and activate it. For more information on Virtual Environment setup see [VenvSetup.md](VenvSetup.md)
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Once inside virtual environment, run the following commands to install required dependencies
    ```
    pip install requirements.txt
    ```
4. To run the program, user must add their key details for API used in this program. Run the following commands.
    ```
    mkdir -p Private/ClientKeys
    echo "Enter ChatGPT Key here" > Private/ClientKeys/chatgpt-api.txt
    echo "Enter Claude Key here" > Private/ClientKeys/claude-api.txt
    echo "Enter Gemini Key here" > Private/ClientKeys/gemini-api.txt
    ```
    **`NOTE:`** Please enter the keys for the respective LLM into the placeholder. 



# Usage
To start using the program, locate the python script `main.py` under `Scripts/api/main.py` or from the root of the repository, run the following:
```
cd Scripts/api
python3 main.py
```

To start the assisting interference program program, locate the python script `main.py` under `Scripts/image_manipulation/main.py` or from the root of the repository, run the following:
```
cd Scripts/image_manipulation
python3 main.py
```


## Use Cases

### 1: Processing an image, video or folder with LLM model

**Command:**

```bash
python3 main.py [model] --process [path]
```
**Description:**
- Give the program a model (chatgpt, claude, gemini) and path for quick and easy processing.
- Versatile for single images and videos or folders, works for all models

**Examples:**
#### Basic
```bash
python3 main.py chatgpt --process path/to/file
```

#### Short-hand verbose
```bash
python3 main.py gemini -p path/to/file -v
```

#### Custom prompt
```bash
python3 main.py gemini -p path/to/file -c path/to/custom.txt
```

### 2: Comparing model functionality for an image, video or folder

#### Comparing Models
```bash
python3 main.py all -p path/to/file
```
Using ```all``` in place of an LLM will run all LLMs and output to the same spreadsheet for easy comparison.

### 3: Batch processing with ChatGPT

**Command:**

```bash
python3 main.py chatgpt --batch [path]
```

**Description:**

- To be used for cheaper processing on large folders and supports up to 100MB in size. 
- Supports the automatic option
- **`NOTE:`** This is only available for the ChatGPT model

**Examples:**

#### Basic automatic processing
```bash
python3 main.py chatgpt --batch path/to/folder --auto
```

#### Short-hand
```bash
python3 main.py chatgpt -b path/to/folder -a
```

#### Checking a batch progress (only for non-auto processing)
```bash
python3 main.py chatgpt -ch batch_no
```

#### Export a batch file (only for non-auto processing)
```bash
python3 main.py chatgpt -e batch_no
```

#### List all batch processes
```bash
python3 main.py chatgpt -l
```

### 4: Interference Program
```bash
python3 main.py -s [strength] [path] [filter]
```

**Description:**

- For use to alter images for the purpose of red teaming
- Example filters include rain, fog, graffiti, brightness and more


# Testing
To ensure that the installation is successful and working correctly, you can run the testing modules provided.

Firstly, ensure pytest is installed:
```bash
pip install pytest
```

Move to the test directory:
```bash
cd Tests
```

To test all at once:
```bash
python3 -m unittest discover -s . -p "test_*.py"
```

To test individually:
```bash
python3 -m unittest test_[name].py -v

```


# Contributors
We would like to thank the individuals that have contributed to this project:
### Team
**Cohen Rafiq**
- **Role:** Project Manager, Developer
- **Contributions:** Gemini API functionality, image manipulation, formatting, CSV output, red teaming
- **Contact:** 23348918@student.uwa.edu.au

**Joel Cornfield**
- **Role:** Developer, Tester
- **Contributions:** Image manipulation, claude API functionality, red teaming, testing
- **Contact:** 23749925@student.uwa.edu.au

**Feiyue Zhang**
- **Role:** Developer, Tester
- **Contributions:** CSV output, testing and red teaming
- **Contact:** 23734789@student.uwa.edu.au

**Lance Basa**
- **Role:** Developer, Tester
- **Contributions:** ChatGPT API functionality, ChatGPT batch processing, primary tester and red teaming
- **Contact:** 23420659@student.uwa.edu.au

**Jack Langoulant**
- **Role:** Project Manager, Developer, Tester
- **Contributions:** Video functionality, ChatGPT API functionality, testing and red teaming
- **Contact:** 23344707@student.uwa.edu.au

**Lewis Wood**
- **Role:** Project Manager, Developer
- **Contributions:** Formatting, Command Line Interface, custom CSV output, code integration and red teaming
- **Contact:** 23104581@student.uwa.edu.au

# License
This project is licensed under the Creative Commons License - see the [LICENSE](LICENSE) file for details.



# Acknowledgements
Special thanks to the University of Western Australia and our client for providing the opportunity to work on this project. We also acknowledge the contributors and open-source libraries that helped make this project possible.

- https://github.com/sreeramsa/DriveSim
- https://github.com/IrohXu/Awesome-Multimodal-LLM-Autonomous-Driving
- https://www.youtube.com/watch?v=lXV2PQgbGAs
- https://github.com/JinkyuKimUCB/explainable-deep-driving/blob/master/data/Sample.csv

# Image References for Overlay Feature

Wet-Filter:
![Natural Rain PNG](https://www.transparentpng.com/thumb/raindrops/natural-rain-png-images-35.png)

Image source: ["Natural Rain PNG Images" by transparentpng.com](https://www.transparentpng.com/details/natural-rain-images_2098.html), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Lens-Flare:
![Png Format Images Of Lens Flare](https://www.freeiconspng.com/uploads/png-format-images-of-lens-flare-16.png)

Image source: ["Png Format Images Of Lens Flare" by freeiconspng.com](https://www.freeiconspng.com/img/46213), **licensed for personal use only**.

Fog:
![Smoke effect, fume, fog](https://www.freeiconspng.com/uploads/smoke-028-2.png)

Image source: ["Smoke effect, fume, fog" by freeiconspng.com](https://www.freeiconspng.com/img/515), **licensed for personal use only**.

Rain:
![Browse and Download Rain PNG Pictures](https://www.freeiconspng.com/uploads/rain-png-transparent-9.png)

Image source: ["Browse and Download Rain PNG Pictures" by freeiconspng.com](https://www.freeiconspng.com/img/34459), **licensed for personal use only**.

Graffiti:
![Black Graffiti Tag](https://www.cleanpng.com/png-black-graffiti-tag-515.html)

Image source: ["Black Graffiti Tag" by Cleanpng.com](https://www.cleanpng.com/png-black-graffiti-tag-515.html).






