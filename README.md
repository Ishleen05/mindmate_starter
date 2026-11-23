# MindMate

**An intelligent learning assistant for promoting independent thinking and responsible use of generative AI.**

## Current status
Working prototype with an Overview dashboard, a session-only study notebook, and six learning modes: Socratic Tutor, Examples & Visuals, Verify Before Trusting, Knowledge Check, Reflection Mode and PDF Learning. Five learning workspaces now include visual thinking flows, original practice scenarios, and optional credited Commons picture searches. PDF examples remain grounded in retrieved document excerpts. AI responses use the OpenAI Responses API when configured; otherwise clearly labelled simulated responses are used.

## Technology
- Python and Streamlit
- OpenAI Python SDK (optional real-AI integration)
- pypdf for text extraction
- Keyword-overlap retrieval for PDF passages
- Streamlit session state for lesson context and study notes
- Wikimedia Commons image search with source and license attribution

## Run locally
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and optionally add an API key.
4. Run: `streamlit run app.py`

## Limitations
PDF support currently extracts selectable text only; scanned PDFs and OCR are not supported. Retrieval uses keyword overlap rather than embeddings. The verification mode supports critical evaluation and does not independently verify claims. Simulated mode is a demonstration fallback, not a language model.
Examples & Visuals searches Wikimedia Commons and therefore requires an internet connection. Topic-specific generated explanations and examples require an OpenAI API key; without one, the app provides an example-finding guide instead.

## Development record
- Initial scaffold: Streamlit navigation, five feature screens, hybrid AI service, PDF extraction and baseline passage retrieval.
- Added a styled Overview dashboard, quick links to all six modes, and downloadable session-only study notes.
- Added Examples & Visuals mode with level-adjusted explanations, practical examples, a simple text diagram, and credited Wikimedia Commons images.
- Added step-by-step visual aids, novel practice scenarios, and optional credited topic pictures to the Socratic, verification, quiz, reflection and PDF workspaces.
- Planned next: test each mode, improve document retrieval, add tests, capture storyboards and document design rationale.

## AI assistance
Generative AI was used to help scaffold code and draft prompts. The developer should inspect, run and test all generated code, record material changes, and verify behaviour before submission.
