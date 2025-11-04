"""
Gradio Interface for Image-to-Code Generation
Provides a user-friendly web interface for uploading images and generating code.
"""

import gradio as gr
import requests
import os
from pathlib import Path

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def generate_code_from_image(image, prompt, model):
    """Generate code from uploaded image using the API"""
    
    if image is None:
        return "Please upload an image first.", ""
    
    try:
        # Prepare the file for upload
        with open(image, "rb") as f:
            files = {"image": (os.path.basename(image), f, "image/png")}
            data = {
                "prompt": prompt or "Generate clean, well-commented code based on this image.",
                "model": model or "gpt-4o"
            }
            
            # Make API request
            response = requests.post(
                f"{API_URL}/generate-code",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                code = result.get("code", "")
                explanation = result.get("explanation", "")
                
                return code, explanation or "Code generated successfully!"
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                return "", error_msg
                
    except requests.exceptions.ConnectionError:
        return "", "Error: Could not connect to the API. Make sure the FastAPI service is running on " + API_URL
    except Exception as e:
        return "", f"Error: {str(e)}"


def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            return "✅ API is running"
        else:
            return "❌ API returned an error"
    except requests.exceptions.ConnectionError:
        return "❌ API is not running. Please start the service with: python image_to_code_service.py"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Image-to-Code Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🖼️ Image-to-Code Generation Service
        
        Upload an image (screenshot, diagram, code snippet, or UI mockup) and generate code from it!
        
        **Instructions:**
        1. Upload an image file
        2. (Optional) Provide a custom prompt
        3. Select a model (default: gpt-4o)
        4. Click "Generate Code"
        
        **Note:** Make sure the FastAPI service is running. Start it with:
        ```bash
        python image_to_code_service.py
        ```
        """
    )
    
    with gr.Row():
        api_status = gr.Textbox(
            label="API Status",
            value="Checking...",
            interactive=False
        )
        check_btn = gr.Button("Check API Status")
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(
                label="Upload Image",
                type="filepath",
                sources=["upload", "clipboard"]
            )
            
            prompt_input = gr.Textbox(
                label="Custom Prompt (Optional)",
                placeholder="Generate clean, well-commented code based on this image. Include comments explaining the logic.",
                lines=3,
                value="Generate clean, well-commented code based on this image. Include comments explaining the logic."
            )
            
            model_dropdown = gr.Dropdown(
                choices=["gpt-4o", "gpt-4-vision-preview"],
                value="gpt-4o",
                label="Model"
            )
            
            generate_btn = gr.Button("Generate Code", variant="primary", size="lg")
        
        with gr.Column():
            code_output = gr.Code(
                label="Generated Code",
                language="python",
                lines=20,
                interactive=True
            )
            
            explanation_output = gr.Textbox(
                label="Explanation",
                lines=5,
                interactive=False
            )
            
            download_btn = gr.File(
                label="Download Code",
                visible=False
            )
    
    # Event handlers
    check_btn.click(
        fn=check_api_health,
        outputs=api_status
    )
    
    generate_btn.click(
        fn=generate_code_from_image,
        inputs=[image_input, prompt_input, model_dropdown],
        outputs=[code_output, explanation_output]
    )
    
    # Check API status on load
    demo.load(fn=check_api_health, outputs=api_status)
    
    # Examples
    gr.Examples(
        examples=[],
        inputs=image_input,
        label="Example Images (add your own examples to the examples/ folder)"
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gradio Interface for Image-to-Code Generation")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000", help="API URL")
    parser.add_argument("--server-name", type=str, default="0.0.0.0", help="Server host")
    parser.add_argument("--server-port", type=int, default=7860, help="Server port")
    parser.add_argument("--share", action="store_true", help="Create a public link")
    
    args = parser.parse_args()
    
    # Set API URL environment variable
    os.environ["API_URL"] = args.api_url
    
    print(f"Starting Gradio interface on http://{args.server_name}:{args.server_port}")
    print(f"API URL: {args.api_url}")
    
    demo.launch(
        server_name=args.server_name,
        server_port=args.server_port,
        share=args.share
    )
