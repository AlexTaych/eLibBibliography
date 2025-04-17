from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
from citation_maker import get_bibliography
from citation_dump import clean_bibliography

app = FastAPI()

# Разрешаем CORS (чтобы расширение могло обращаться к бэкенду)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_citation(request: Request):
    data = await request.json()
    html_content = data.get("html", "")
    url = data.get("url", "")
    save_to_bibliography = data.get("saveToBibliography", True)

    # Запись в файл для отладки ошибок, которые встречаются часто
    base_folder = Path(__file__).resolve().parent
    try:
        with open(base_folder.joinpath("temp.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
    except Exception as e:
        print(f"Ошибка при записи файла: {e}")

    if save_to_bibliography:
        citation_dict = get_bibliography(html_content, url=url, bibl=True)
        if isinstance(citation_dict, dict):
            citation_resp = citation_dict['short_cite']
        else:
            citation_resp = citation_dict
    else:
        citation_resp = get_bibliography(html_content, url=url)

    return JSONResponse({"citation": citation_resp})

@app.post("/clean")
async def clean_bibliography_endpoint():
    try:
        clean_bibliography()
        return JSONResponse({"success": True})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)