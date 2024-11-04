import uvicorn

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from app import PhiloDocumentParser

# Instantiate the FastAPI app
app = FastAPI()

# Initialize document parser instance
document_parser = PhiloDocumentParser()


@app.post("/parse/pdf")
async def parse_pdf(file: UploadFile = File(...)):
    print("Hello World")
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_content = await file.read()
    parse_result = document_parser.parse_pdf(file_content)
    return JSONResponse(content=parse_result.model_dump())


@app.post("/parse/image")
async def parse_image(
    image: UploadFile = File(...),
    task_prompt: Optional[str] = "<MORE_DETAILED_CAPTION>",
):
    if not (image.content_type.startswith("image/")):
        raise HTTPException(status_code=400, detail="Only image files are accepted.")

    image_content = await image.read()
    parse_result = document_parser.parse_img(
        image_content, image_name=image.filename, task_prompt=task_prompt
    )
    return JSONResponse(content=parse_result.model_dump())


@app.post("/parse/doc_ppt")
async def parse_doc_ppt(file: UploadFile = File(...)):
    if not (
        file.filename.endswith(".doc")
        or file.filename.endswith(".docx")
        or file.filename.endswith(".ppt")
        or file.filename.endswith(".pptx")
    ):
        raise HTTPException(
            status_code=400, detail="Only DOC, DOCX, PPT, and PPTX files are accepted."
        )

    file_content = await file.read()
    parse_result = document_parser.parse_doc_ppt(file_content)
    return JSONResponse(content=parse_result.model_dump())


if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8001, reload=True)
