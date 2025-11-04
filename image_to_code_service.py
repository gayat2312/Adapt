"""
Image-to-Code Generation Service
Allows users to upload images and generate code from them.
"""

import os
import base64
from pathlib import Path
from typing import Optional
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
from PIL import Image
import io

app = FastAPI(title="Image-to-Code Generation Service")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize OpenAI client (you can replace this with other vision models)
# Make sure to set OPENAI_API_KEY environment variable
client = None
try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"Warning: OpenAI client not initialized: {e}")
    print("Set OPENAI_API_KEY environment variable to enable code generation")


class CodeGenerationRequest(BaseModel):
    image_path: Optional[str] = None
    prompt: Optional[str] = "Generate clean, well-commented code based on this image."
    model: Optional[str] = "gpt-4o"  # or "gpt-4-vision-preview"


class CodeGenerationResponse(BaseModel):
    code: str
    explanation: Optional[str] = None
    image_path: str


@app.get("/")
async def root():
    return {
        "message": "Image-to-Code Generation Service",
        "endpoints": {
            "POST /upload": "Upload an image file",
            "POST /generate-code": "Generate code from an uploaded image",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "client_configured": client is not None}


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image file"""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save the uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "message": "Image uploaded successfully",
            "filename": file.filename,
            "path": str(file_path),
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")


@app.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code(
    image: UploadFile = File(...),
    prompt: Optional[str] = "Generate clean, well-commented code based on this image. Include comments explaining the logic.",
    model: Optional[str] = "gpt-4o"
):
    """Generate code from an uploaded image"""
    
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="OpenAI client not configured. Please set OPENAI_API_KEY environment variable."
        )
    
    try:
        # Validate file type
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await image.read()
        
        # Save uploaded image
        file_path = UPLOAD_DIR / image.filename
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # Convert image to base64 for API
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Prepare the prompt
        system_prompt = """You are an expert code generator. Analyze the uploaded image and generate clean, production-ready code.
        - If the image contains code, extract and improve it
        - If the image contains a diagram or UI mockup, generate the corresponding code
        - If the image contains a screenshot, generate the code to recreate it
        - Always include helpful comments
        - Follow best practices for the detected programming language"""
        
        user_prompt = f"{prompt}\n\nPlease analyze the image and generate the appropriate code."
        
        # Call OpenAI Vision API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image.content_type.split('/')[1]};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        generated_text = response.choices[0].message.content
        
        # Try to extract code blocks if present
        code = generated_text
        explanation = None
        
        if "```" in generated_text:
            # Extract code from markdown code blocks
            parts = generated_text.split("```")
            if len(parts) >= 3:
                code = parts[1].split("\n", 1)[1] if "\n" in parts[1] else parts[1]
                explanation = "\n".join([p.strip() for p in parts[0::2] if p.strip()])
        
        return CodeGenerationResponse(
            code=code,
            explanation=explanation,
            image_path=str(file_path)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating code: {str(e)}")


@app.post("/generate-code-from-path")
async def generate_code_from_path(request: CodeGenerationRequest):
    """Generate code from an already uploaded image path"""
    
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="OpenAI client not configured. Please set OPENAI_API_KEY environment variable."
        )
    
    if not request.image_path:
        raise HTTPException(status_code=400, detail="image_path is required")
    
    file_path = Path(request.image_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")
    
    try:
        # Read image
        with open(file_path, "rb") as f:
            image_data = f.read()
        
        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Determine content type
        content_type = f"image/{file_path.suffix[1:]}" if file_path.suffix else "image/png"
        
        # Prepare prompt
        system_prompt = """You are an expert code generator. Analyze the uploaded image and generate clean, production-ready code."""
        
        user_prompt = request.prompt or "Generate clean, well-commented code based on this image."
        
        # Call OpenAI Vision API
        response = client.chat.completions.create(
            model=request.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{content_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        generated_text = response.choices[0].message.content
        
        # Extract code blocks
        code = generated_text
        explanation = None
        
        if "```" in generated_text:
            parts = generated_text.split("```")
            if len(parts) >= 3:
                code = parts[1].split("\n", 1)[1] if "\n" in parts[1] else parts[1]
                explanation = "\n".join([p.strip() for p in parts[0::2] if p.strip()])
        
        return CodeGenerationResponse(
            code=code,
            explanation=explanation,
            image_path=str(file_path)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating code: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Image-to-Code Generation Service")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"Starting Image-to-Code Generation Service on http://{args.host}:{args.port}")
    print(f"API Documentation available at http://{args.host}:{args.port}/docs")
    
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)
