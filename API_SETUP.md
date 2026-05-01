# API Setup Guide

This project is configuration-driven. To run it, create a local `.env` file from `.env.example` and fill in these values:

- `TEXT_MODEL_ENDPOINT`
- `TEXT_MODEL_API_KEY`
- `TEXT_MODEL_API_VERSION`
- `TEXT_MODEL_DEPLOYMENT`
- `IMAGE_MODEL_ENDPOINT`
- `IMAGE_MODEL_API_KEY`
- `IMAGE_MODEL_API_VERSION`
- `IMAGE_MODEL_DEPLOYMENT`

## How it works

- The report stage reads the text-model variables.
- The image stage reads the image-model variables.
- The dashboard and probe script use the same local `.env` file.

## Important

- Never commit `.env`.
- Never place real keys inside source files, JSON configs, or documentation examples.
- After filling `.env`, the project should run without any code changes.
