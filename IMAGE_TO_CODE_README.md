# Image-to-Code Generation Service

A service that allows you to upload images and generate code from them using vision-language models.

## Features

- 📸 Upload images (screenshots, diagrams, code snippets, UI mockups)
- 🤖 Generate code using GPT-4 Vision API
- 🎨 Beautiful Gradio web interface
- 🔌 RESTful API for programmatic access
- 📝 Customizable prompts
- 💾 Download generated code

## Setup

### Prerequisites

1. Python 3.9+ (already configured in your environment)
2. OpenAI API key (for code generation)

### Installation

The required packages are already installed in your environment:
- `fastapi`
- `gradio`
- `openai`
- `pillow`
- `uvicorn`

### Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Option 1: Gradio Web Interface (Recommended)

Start the Gradio interface:

```bash
python gradio_interface.py
```

Then open your browser to `http://localhost:7860`

### Option 2: FastAPI Service Only

Start the FastAPI service:

```bash
python image_to_code_service.py
```

The API will be available at `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`
- Interactive API: `http://localhost:8000/redoc`

### Option 3: Run Both Services

Start the FastAPI service in one terminal:

```bash
python image_to_code_service.py
```

Start the Gradio interface in another terminal:

```bash
python gradio_interface.py
```

## API Endpoints

### POST `/upload`
Upload an image file.

**Request:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_image.png"
```

### POST `/generate-code`
Generate code from an uploaded image.

**Request:**
```bash
curl -X POST "http://localhost:8000/generate-code" \
  -F "image=@your_image.png" \
  -F "prompt=Generate clean Python code" \
  -F "model=gpt-4o"
```

### GET `/health`
Check API health status.

**Request:**
```bash
curl http://localhost:8000/health
```

## Supported Image Types

- Screenshots of code
- UI mockups and wireframes
- Diagrams and flowcharts
- Hand-drawn sketches
- Code snippets
- Design mockups

## Models

Supported models:
- `gpt-4o` (recommended, fastest and most capable)
- `gpt-4-vision-preview` (legacy)

## Example Use Cases

1. **Convert Screenshots to Code**: Upload a screenshot of a UI and get the HTML/CSS code
2. **Extract Code from Images**: Upload a photo of code and get clean, formatted code
3. **Diagram to Code**: Upload a flowchart or diagram and generate the corresponding code
4. **UI Mockup to Implementation**: Upload a design mockup and generate the frontend code

## File Structure

```
/workspace/
├── image_to_code_service.py  # FastAPI backend service
├── gradio_interface.py        # Gradio web interface
├── uploads/                    # Directory for uploaded images
└── README.md                   # This file
```

## Troubleshooting

### API Key Not Set
If you see "OpenAI client not configured", make sure you've set the `OPENAI_API_KEY` environment variable.

### Connection Errors
If the Gradio interface can't connect to the API:
1. Make sure the FastAPI service is running
2. Check that the API URL matches (default: `http://localhost:8000`)
3. Update the API URL in `gradio_interface.py` or set `API_URL` environment variable

### Port Already in Use
If port 8000 or 7860 is already in use:
- FastAPI: Use `--port` flag: `python image_to_code_service.py --port 8001`
- Gradio: Use `--server-port` flag: `python gradio_interface.py --server-port 7861`

## Advanced Usage

### Custom API URL

For Gradio interface:
```bash
export API_URL="http://your-api-server:8000"
python gradio_interface.py
```

Or pass as argument:
```bash
python gradio_interface.py --api-url http://your-api-server:8000
```

### Using Different Models

In the Gradio interface, select from the dropdown menu, or via API:

```bash
curl -X POST "http://localhost:8000/generate-code" \
  -F "image=@image.png" \
  -F "model=gpt-4-vision-preview"
```

## License

See LICENSE file for details.

## Notes

- Uploaded images are stored in the `uploads/` directory
- The service automatically handles image format conversion
- Generated code is returned in markdown code blocks when possible
- For production use, consider adding authentication and rate limiting
