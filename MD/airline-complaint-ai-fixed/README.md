# Airline Complaint AI - Fixed copy

## What this folder contains

The workspace contains an `airline-complaint-ai-fixed` folder with a nested `airline-complaint-ai` application. The nested project contains a full Streamlit/NLP project layout, including application entry points, pages, scripts, source modules, tests, model/artifact folders, and deployment notes.

This is a separate copy from the sibling `airline-complaint-ai` folder. Its files may not be identical, so check the nested source before relying on details from another copy.

## Documentation and setup

Use the guides in this folder for this project copy:

- [Setup instructions](./SETUP.md)
- [File guide](./FILES.md)
- [Function and class guide](./FUNCTIONS.md)
- [Test guide](./TESTS.md)

The sibling [Airline Complaint AI guide](../airline-complaint-ai/README.md) explains shared application concepts, but use the nested copy's own README and code as the source of truth for this version.

Nested project location:

```text
airline-complaint-ai-fixed/airline-complaint-ai/
```

Run commands from that nested project folder, not from the outer wrapper folder. See the [setup guide](./SETUP.md) before running.

## Important difference from the sibling

The fixed copy has additional project files and directories, such as `.env.example`, `.devcontainer`, notebooks, and model/artifact folders. Keep real secrets in environment configuration, never in committed source. Because this copy is distinct, do not assume the sibling's model artifacts, data, or exact behavior are interchangeable.
