# Project Setup Guide

This guide provides instructions on how to set up the project for local development and production.

## Prerequisites

Ensure you have the following installed:

- **Python 3.11**
- **Poetry** (for dependency management)
- **Docker** (for containerized deployment)
- **Makefile** (For running commands such as install)
## Local Development Setup

### 1. Clone the Repository
```bash
git clone git@github.com:Dashing-Nelson/contextualizes_entities_from_medical_document.git
cd contextualizes_entities_from_medical_document
```

### 2. Create `.env` file

Create the file in the root folder.

### 3. Install Dependencies

```bash
make install
```

### 4. Activate Virtual Environment

```bash
poetry shell
```

### 5. Run the Application (Development Mode)

```bash
make run-dev
```

Now, you could go to `localhost:<YOUR_PORT_IN_ENV>/docs` and see the swagger API documentation.

### 6. Using Debugger in PyCharm

For debugging, use `debug.py` as the entry point in PyCharm:

- Open PyCharm
- Navigate to **Run > Edit Configurations**
- Add a new **Python** configuration
- Set **Script Path** to `debug.py`
- Set **Paths to .env file** to the location of your `.env` file.
- Ensure the **Python Interpreter** is set to the Poetry virtual environment
- Run the debugger

### 7. Running Linter and Formatter

This project includes several Makefile targets to help maintain code quality. You can run these commands in your terminal:

    make format: Formats code using Black.
    make isort: Sorts and organizes import statements using isort.
    make lint: Lints code with Flake8 to catch potential issues.
    make test: Runs your test suite using pytest.
    make check: Runs format, isort, and lint sequentially to ensure code meets formatting and style guidelines.

### Running in Docker (Development Mode)

1. Build the development image:
```bash
make docker-dev-build
```
2. Run the container:
```bash
make docker-dev-run
```

### Running in Docker (Production Mode)

1. Build the production image:
```bash
make docker-prod-build
```
2. Run the container:
```bash
make docker-prod-run
```

The application should now be accessible at `http://localhost:<YOUR_PORT_IN_ENV>`.

## **🚀 Environment Variables Overview**
The table below lists all environment variables, their descriptions, and whether they are required.

| **Variable**                        | **Required?** | **Description**                                                            | **Default Value** |
|-------------------------------------|---------------|----------------------------------------------------------------------------|-------------------|
| `HTTP_BASIC_AUTH_USERNAME`          | ✅ Yes         | Username for HTTP Basic Authentication.                                    | N/A               |
| `HTTP_BASIC_AUTH_PASSWORD`          | ✅ Yes         | Password for HTTP Basic Authentication.                                    | N/A               |
| `STAGE`                             | ✅ Yes         | Defines the deployment environment (`dev`, `staging`, `prod`).             | N/A               |
| `HUGGING_FACE_MODEL_PATH`           | ✅ Yes         | Path to the Hugging Face model repository.                                 | N/A               |
| `HUGGING_FACE_TASK`                 | ❌ No          | Task type for the Hugging Face model (`ner`, `text-classification`, etc.). | `ner`             |
| `HUGGING_FACE_AGGREGATION_STRATEGY` | ❌ No          | Aggregation strategy for token classification.                             | `simple`          |
| `HUGGING_FACE_DEVICE`               | ❌ No          | Device to run the model (`cpu`, `cuda:0`, etc.).                           | `cpu`             |
| `HTTP_PORT`                         | ✅ Yes         | Port to set for the HTTP Server                                            | N/A               |

> ⚠️ **The application will fail to start if the required variables are missing.**  
> Ensure these are set in **`.env`** in the root folder. You could check the `config.py` file inside `app/util/` folder for more info.

---

## **📌 Example `.env` File**
To set up the environment variables locally, create a `.env` file with the following content:

```ini
# Required Variables
HTTP_BASIC_AUTH_USERNAME=admin
HTTP_BASIC_AUTH_PASSWORD=admin
STAGE=dev
HUGGING_FACE_MODEL_PATH=d4data/biomedical-ner-all
HUGGING_FACE_TASK=ner
HUGGING_FACE_AGGREGATION_STRATEGY=simple
HUGGING_FACE_DEVICE=cpu
```

## Run tests using Poetry:
```bash
make test
```