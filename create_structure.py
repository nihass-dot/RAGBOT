# create_structure.py
import os

# Define the folder structure
folders = [
    "backend/src/config",
    "backend/src/controllers",
    "backend/src/models",
    "backend/src/dao",
    "backend/src/services",
    "backend/src/routes",
    "backend/src/middleware",
    "backend/src/utils",
    "backend/data"
]

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Define files to create
files = [
    "backend/src/config/db.py",
    "backend/src/config/models.py",
    "backend/src/controllers/rag_controller.py",
    "backend/src/models/document.py",
    "backend/src/dao/document_dao.py",
    "backend/src/services/rag_service.py",
    "backend/src/routes/rag_routes.py",
    "backend/src/middleware/error_handlers.py",
    "backend/src/utils/text_processing.py",
    "backend/src/app.py",
    "backend/src/main.py",
    "backend/.env",
    "backend/.gitignore",
    "backend/requirements.txt",
    "backend/README.md",
    "backend/data/india.txt"
]

# Create files
for file in files:
    with open(file, 'w') as f:
        pass  # Creates empty file

print("Folder structure created successfully!")