#!/bin/bash

# Check if a command-line argument is provided for HUGGING_FACE_MODEL_PATH
if [ $# -ge 1 ]; then
  export HUGGING_FACE_MODEL_PATH="$1"
  echo "Using HUGGING_FACE_MODEL_PATH from argument: ${HUGGING_FACE_MODEL_PATH}"
else
  # If not provided, try to load it from the .env file
  if [ -f ".env" ]; then
    source .env
    echo "Using HUGGING_FACE_MODEL_PATH from .env file: ${HUGGING_FACE_MODEL_PATH}"
  else
    echo ".env file not found. Please provide HUGGING_FACE_MODEL_PATH as an argument or in a .env file."
    exit 1
  fi
fi

# Ensure that HUGGING_FACE_MODEL_PATH is set
if [ -z "$HUGGING_FACE_MODEL_PATH" ]; then
  echo "HUGGING_FACE_MODEL_PATH is not set. Please set it either via argument or .env file."
  exit 1
fi

MODEL_DIR="models/${HUGGING_FACE_MODEL_PATH}"
mkdir -p "$MODEL_DIR"

echo "Downloading model: ${HUGGING_FACE_MODEL_PATH}"

FILES_JSON=$(curl -s "https://huggingface.co/api/models/${HUGGING_FACE_MODEL_PATH}/tree/main")

FILES=$(echo "$FILES_JSON" | grep -o '"path":"[^"]*"' | cut -d'"' -f4)

for FILE in $FILES; do
  echo "Downloading: $FILE"

  FILE_DIR=$(dirname "${MODEL_DIR}/${FILE}")
  mkdir -p "$FILE_DIR"

  curl -L "https://huggingface.co/${HUGGING_FACE_MODEL_PATH}/resolve/main/${FILE}" -o "${MODEL_DIR}/${FILE}"
done

echo "Model download complete: ${HUGGING_FACE_MODEL_PATH}"
