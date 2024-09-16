# CITS3200-Group37

https://github.com/JinkyuKimUCB/explainable-deep-driving/blob/master/data/Sample.csv
https://github.com/sreeramsa/DriveSim/assets/24236215/5665eaa4-5615-4b11-bcc1-80e89073f541
https://www.youtube.com/watch?v=lXV2PQgbGAs

# CLI Usage Documentation

## Overview

This document provides a brief overview of how to use the `main.py` script for various use cases. The script supports different commands and options for processing models, listing batches, checking batches, and exporting batches.

## Use Cases

### 1. LLM Model Processing

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