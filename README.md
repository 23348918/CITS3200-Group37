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

### Recquirements
- Operating System: Windows, MacOS, Ubuntu - Ubuntu Recommended 
- GitHub Account
- Python Version 3.8 and above

### Steps
1. Clone the repository:
    ```
    git clonehttps://github.com/23348918/CITS3200-Group37
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
    echo "Enter Gemeni Key here" > Private/ClientKeys/gemini-api.txt
    ```
    **`NOTE:`** Please enter the keys for the respective LLM into the placeholder. 



# Usage
To start using the program, locate the python script `main.py` under `Scripts/api/main.py` or from the root of the repository, run the following:
```
cd Scripts/api
python3 main.py
```


### Use Cases
 1. LLM Model Processing

    **Command:**

    ```bash
    python3 main.py model -process [path] -prompt [prompt] --verbose
    ```

    - model: Specifies the model type (i.e. ChatGPT).
    - -process path: Indicates that you want to process the model at the given path.
    - -prompt prompt: custom prompt for the given model, else a default case is used
    - --verbose: Enables verbose output for more detailed logs.

### Use Case 2: List Batches

**Command:**

```bash
python3 main.py -list --verbose
```

Description:

- -list: Requests a list of available batches.
- --verbose: Enables verbose output for detailed batch information.


### Use Case 3: Check Batch

**Command:**

```bash
python3 main.py model -check batch_id --verbose
```

Description:

- model: Specifies the model type (i.e. ChatGPT).
- -check batch_id: Checks the status or details of the batch with the given batch_id.
- --verbose: Provides detailed output about the batch check.

### Use Case 4: Export Batch

**Command:**

```bash
python3 main.py model -export batch_id --verbose
```

- model: Specifies the model type (i.e. ChatGPT).
- -export batch_id: Exports the batch with the given batch_id.
- --verbose: Provides detailed output about the export process.

# Testing

# Contributors

# License
This project is licensed under the Creative Commons License - see the [LICENSE](LICENSE) file for details.



# Acknowledgements
Special thanks to the University of Western Australia and our client for providing the opportunity to work on this project. We also acknowledge the contributors and open-source libraries that helped make this project possible.

- https://github.com/sreeramsa/DriveSim
- https://github.com/IrohXu/Awesome-Multimodal-LLM-Autonomous-Driving
- https://www.youtube.com/watch?v=lXV2PQgbGAs
- https://github.com/JinkyuKimUCB/explainable-deep-driving/blob/master/data/Sample.csv






