# Medical Entity Extraction API Documentation

## Note

Code in `config.py`, `Dockerfile`, `Makefile`, `pyproject.toml` has taken inspiration from my previous projects/take home task.

## Architecture Overview

### System Architecture

The system follows a modular architecture with **Clean Code** amd **Clean Architecture** in mind with the following components:

1. **API Layer**: FastAPI-based RESTful endpoints that handle client requests
2. **Authentication Layer**: HTTP Basic Authentication for securing API access
3. **PDF Processing Layer**: PDF parsing and text extraction
4. **NLP Layer**: Entity extraction using Hugging Face transformers models
5. **Context Extraction Layer**: Identification of surrounding text for contextualizing entities
6. **Containerization**: Docker support for development and production environments
7. **Server Layer**:
    - Uvicorn: Acts as the ASGI server, leveraging uvloop for high-performance asynchronous request handling.
    - Gunicorn: Serves as a process manager that runs multiple Uvicorn worker processes, optimizing the system for CPU-intensive tasks by utilizing multiple CPU cores.

### API Flow

1. Client sends a PDF document via a POST request to the `/api/v1/extract` endpoint.
2. Request is authenticated using HTTP Basic Auth credentials
3. Validation is performed on the document.
4. PDF is parsed and text is extracted.
5. Text is processed by the Hugging Face NER model to identify medical entities
6. Context is extracted for each identified entity
7. Results are returned in JSON format

## Technical Implementation

### Tools and Technologies

#### FastAPI

I chose FastAPI for its asynchronous support, fast performance, and automatic OpenAPI documentation generation.

#### pypdf

`pypdf` was used for PDF parsing due to its ease of use, and it's ability to check for valid pdf.

#### Hugging Face transformers pipeline

I used it for entity extraction (with the `d4data/biomedical-ner-all` model) and selected it to leverage a 
domain-specific model for biomedical entity recognition.

#### Torch

It was needed as part of the transformer package.

#### Uvicorn and Gunicorn

I chose `uvicorn` (with `uvloop`) as our ASGI server because uvloop is a high-performance event loop implemented in C that 
greatly speeds up asynchronous operations compared to Python’s default asyncio loop. This is especially beneficial for 
web applications where fast request handling and low latency are critical.

At the same time, I also opted for `gunicorn` as our WSGI server. Gunicorn excels at managing multiple worker processes, 
which is essential for CPU-intensive tasks. Since our task (semantic extraction, PDF parsing, and NLP model inference) 
is CPU intensive rather than I/O bound, running several workers allows us to fully utilize the available CPU cores and 
improve overall throughput and performance.

In Production use, we will use 2 workers per CPU.

#### python-json-logger

I chose to use `python-json-logger` because it formats our application logs as JSON, giving us a structured way of logging.
This enables easier integration with log aggregation systems (such as ELK) by making logs machine-readable and consistent.

#### python-multipart

`python-multipart` is a library that parses multipart/form-data requests, which is essential for handling file uploads in 
FastAPI. Our API endpoint accepts PDF files via a form upload, so this package is required to properly parse and 
extract the uploaded files from the request body. Additionally, using a fixed version (if specified) ensures 
compatibility and consistency across different deployments.

### Key Components

#### API Endpoints

The service exposes a single endpoint:

- **POST `/api/v1/extract`**: Accepts a PDF file and returns extracted entities with context

#### Entity Extraction

The entity extraction pipeline involves:

1. Loading a pre-trained Hugging Face model specified in the configuration (such as `d4data/biomedical-ner-all`)
2. Processing the extracted text to identify entities
3. For each entity, extracting a window of surrounding text to provide context.
4. Returning the entity text, context, and position information.

#### Authentication and Security

- HTTP Basic Authentication is implemented to secure API access.
- Environment variables are used for credential management.
- Request ID tracking for monitoring and debugging.

#### Containerization Strategy

The Dockerfile implements a multi-stage build process:

1. **Python Base**: Sets up Python environment variables
2. **Builder Base**: Installs Poetry and project dependencies
3. **Model Base**: Downloads and caches the Hugging Face model
4. **Development**: Includes development tools and hot reloading
5. **Production**: Optimized for production use with Gunicorn workers

## Development Workflow

### Local Development

The project supports multiple development workflows:

1. **Direct execution**: Using Poetry for dependency management and running directly with Uvicorn
2. **Docker-based**: Running in a containerized environment.
3. **Debugging**: PyCharm debugging support with environment variable integration

### Testing Strategy

The testing approach includes:

1. **Unit Tests**: Testing individual components in isolation
2. **End-to-End Tests**: Testing the complete API flow with actual PDF documents
3. **Integration Tests**  Testing the model output.
3. **Test Data**: Sample PDFs and expected outputs for verification

## Challenges and Solutions

### Model Management

**Challenge**: Managing and distributing large NLP models efficiently.

**Solution**: I solved this with a multi-stage Docker build which has a dedicated model download stage. 
This allows the model to be cached as a Docker layer, optimizing build times and storage usage. 
The `download_model.sh` script handles model fetching from Hugging Face dynamically.

### PDF Processing

**Challenge**: Reliable extraction of text from various PDF formats.

**Solution**: Utilized the PyPDF library for robust PDF parsing. Implemented error handling to gracefully manage 
issues with PDF parsing and provide clear feedback to the API clients.

### Performance Optimization

**Challenge**: Optimizing the performance of entity extraction for potentially large documents.

**Solution**: 
- Implemented LRU caching for repeated text processing.
- Configured Gunicorn workers based on CPU cores (2 * num_cores). Our workload is CPU intensive.
- Used PyTorch optimizations where available.

### Environment Configuration

**Challenge**: Managing different configurations across development, testing, and production environments.

**Solution**: Implemented a structured approach to environment variables with:
- Required vs. optional variables clearly defined
- Default values for non-critical settings
- Validation of critical variables at startup
- Support for .env files in development

### tracking logs for the same request

**Challenge**: Logs are hard to read when we do not know which request it belongs to.

**Solution**: Implemented creating `request_id` with every request and storing it in `Context Var`. This way we could
track what request id initiated the request throughout the lifecycle of the request.

### Time it took to complete a request

**Challenge**: Checking how long an API took to complete.

**Solution**: Implemented a middleware that would log the time it took to complete a response.

## Deployment Considerations

### Resource Requirements

- **CPU**: Entity extraction is CPU-intensive; scaling should account for this. The workers for FastAPI will 
automatically cater to the change in CPU in the underlying resource.
- **Memory**: NLP models require significant memory (varies by model size). 1 GB is recommended.
- **Storage**: Models are cached locally and require storage space. 512 MB is recommended.

### Scaling Strategy

- Horizontally scalable through containerization. Change in CPU will automically be picked up by gunicorn.
- Performance primarily limited by CPU and model size.
- Consider GPU acceleration for high-volume deployments. We would need to set the `HUGGING_FACE_DEVICE` to `gpu` or `cuda`
for this to work

### Monitoring and Logging

- Structured JSON logging for machine parsing
- Request ID tracking across the processing pipeline
- Performance metrics included in response headers
- Detailed error reporting with appropriate HTTP status codes