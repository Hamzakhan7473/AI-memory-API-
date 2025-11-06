# File Upload Feature for Use Cases

## ✅ File Upload Support Added

### 📋 Supported Use Cases:
1. **Knowledge Bases** - Upload PDF/Word documents
2. **Research Tools** - Upload research papers (PDF/Word)
3. **Educational Platforms** - Upload educational materials (PDF/Word)
4. **Healthcare Systems** - Upload medical documents (PDF/Word)

### 🔧 Backend Implementation:

#### New Endpoints:
1. **POST `/api/use-cases/knowledge-base/upload`**
   - Upload PDF or Word document
   - Parameters: `file`, `category` (optional), `tags` (optional, comma-separated)
   - Returns: `filename`, `file_type`, `total_chunks`, `memories_created`, `memory_ids`

2. **POST `/api/use-cases/research/upload`**
   - Upload research paper (PDF/Word)
   - Parameters: `file`, `authors` (optional, comma-separated), `doi` (optional), `keywords` (optional, comma-separated), `publication_date` (optional)
   - Returns: `filename`, `file_type`, `title`, `total_chunks`, `memories_created`, `memory_ids`

3. **POST `/api/use-cases/education/upload`**
   - Upload educational material (PDF/Word)
   - Parameters: `file`, `category` (optional), `difficulty_level` (optional)
   - Returns: `filename`, `file_type`, `concept_name`, `total_chunks`, `memories_created`, `memory_ids`

4. **POST `/api/use-cases/healthcare/upload`**
   - Upload healthcare document (PDF/Word)
   - Parameters: `file`, `patient_id`, `record_type`, `doctor_id` (optional)
   - Returns: `filename`, `file_type`, `patient_id`, `record_type`, `total_chunks`, `memories_created`, `memory_ids`

#### Document Service:
- **New Service**: `app/services/document_service.py`
- **Features**:
  - PDF text extraction (using pdfplumber and PyPDF2)
  - Word document extraction (using python-docx)
  - Automatic file type detection
  - Text chunking with configurable size and overlap
  - Support for `.pdf`, `.docx`, `.doc` files

#### Processing Flow:
1. **File Upload** → Read file bytes
2. **Text Extraction** → Extract text based on file type
3. **Chunking** → Split text into chunks (default: 1000 chars, 200 overlap)
4. **Memory Creation** → Create memories from chunks
5. **Relationship Building** → Link chunks and find related content
6. **RAG Integration** → Ready for semantic search

### 🎨 Frontend Implementation:

#### Knowledge Base Dashboard:
- ✅ Added file upload UI
- ✅ Toggle between "Manual Entry" and "Upload File"
- ✅ File selection with validation (PDF/Word only)
- ✅ Category and tags input
- ✅ Upload progress indicator
- ✅ Success/error feedback

#### Features:
- **File Validation**: Only accepts `.pdf`, `.docx`, `.doc` files
- **File Preview**: Shows selected file name and size
- **Form Data**: Uses `FormData` for multipart upload
- **Progress Feedback**: Shows uploading status
- **Error Handling**: Displays user-friendly error messages

### 📦 Dependencies Added:
- `python-docx>=1.1.0` - For Word document processing

### 🔄 Integration with RAG:
- Uploaded documents are automatically chunked
- Chunks are embedded and stored in ChromaDB
- Relationships are created between chunks
- Documents are searchable via semantic search
- Ready for RAG query generation

### 📝 Usage Example:

#### Knowledge Base Upload:
```javascript
const formData = new FormData();
formData.append('file', selectedFile);
formData.append('category', 'Technology');
formData.append('tags', 'AI, ML, Data Science');

const response = await axios.post(
  '/api/use-cases/knowledge-base/upload',
  formData,
  { headers: { 'Content-Type': 'multipart/form-data' } }
);
```

#### Research Paper Upload:
```javascript
const formData = new FormData();
formData.append('file', selectedFile);
formData.append('authors', 'Author 1, Author 2');
formData.append('doi', '10.1000/xyz123');
formData.append('keywords', 'NLP, Transformers');

const response = await axios.post(
  '/api/use-cases/research/upload',
  formData,
  { headers: { 'Content-Type': 'multipart/form-data' } }
);
```

### ✅ Features:
- ✅ PDF support (`.pdf`)
- ✅ Word document support (`.docx`, `.doc`)
- ✅ Automatic text extraction
- ✅ Configurable chunking (size, overlap)
- ✅ Relationship building
- ✅ Metadata preservation
- ✅ Error handling
- ✅ Progress feedback

### 🚀 Next Steps:
1. Add file upload UI to Research, Education, and Healthcare dashboards
2. Add file preview (first page/paragraph)
3. Add batch upload support
4. Add file storage management
5. Add document versioning

---

## 📊 Status: ✅ Complete for Knowledge Bases

**Backend**: ✅ All endpoints implemented
**Document Service**: ✅ PDF and Word support
**Frontend**: ✅ Knowledge Base upload UI added
**Integration**: ✅ RAG pipeline ready

**Ready for**: Research, Education, Healthcare upload UIs

