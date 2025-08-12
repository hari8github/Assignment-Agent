# AI Assignment Generator 📚

An intelligent web application that automatically generates comprehensive academic assignments on any topic using AI-powered Wikipedia research and writing.

## 🌟 Features

- **AI-Powered Research**: Conducts thorough Wikipedia research automatically
- **Academic Writing**: Generates university-level assignments with proper structure
- **Live Editing**: Edit any part of the assignment directly in the browser
- **Multiple Formats**: Export as TXT, PDF, or DOCX
- **Source Citations**: Automatically collects and cites Wikipedia sources

## 🏗️ Tech Stack

- **Backend**: Flask + LangChain + Groq (Llama3-8b-8192)
- **Research**: Wikipedia API integration
- **Documents**: ReportLab (PDF), python-docx (Word)
- **Frontend**: Vanilla JavaScript + Modern CSS
- **Deployment**: Render.com ready

## 🚀 How It Works

1. **Research Phase**: AI agent explores multiple aspects of your topic on Wikipedia
2. **Writing Phase**: Structures findings into academic format:
   - Introduction (150-200 words)
   - 4 Main Sections (300-400 words each)
   - Conclusion (150-200 words)
   - Auto-generated citations
3. **Edit & Export**: Modify content and download in your preferred format

## 🎯 Who It's For

- **Students**: Research starting points and assignment structure
- **Educators**: Teaching materials and discussion topics
- **Professionals**: Quick comprehensive overviews of new topics
- **Researchers**: Structured information gathering

## 🛠️ Setup

### Local Development
```bash
git clone <repository-url>
cd ai-assignment-generator
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
python app.py
```

### Deployment
Deploy to Render.com using the included `render.yaml` - just add your `GROQ_API_KEY`.

## 📝 Usage

1. Enter your topic in the text area
2. Click "Generate Assignment" (30-60 seconds)
3. Review and edit the generated content
4. Download in your preferred format

## ⚡ Strengths & Limitations

**✅ Great For:**
- Research starting points
- Academic structure learning
- Topic exploration
- Educational examples

**❌ Limitations:**
- Wikipedia-only research
- Fixed assignment structure
- Requires fact verification
- Not for final submissions without review

## 🤝 Contributing

Areas for improvement:
- Additional research sources
- Different assignment formats
- Multi-language support
- Advanced editing features

---

**⚠️ Academic Integrity**: This tool assists with research and structure. Always verify facts, add original analysis, and follow your institution's academic integrity policies.
