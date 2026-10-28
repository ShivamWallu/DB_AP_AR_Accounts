"""
Entry point wrapper for Day Book ERP.
Allows running via `python main.py` as well as `python run.py`.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["app", "static"],
        reload_excludes=["uploads/*", "*.db*", "*.xlsx", "*.xls", "*.log", "data_files/*"]
    )
