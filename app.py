import streamlit as st
from mindmate.services.ai_service import generate
from mindmate.services.image_service import ImageSearchError, search_commons_images
from mindmate.services.pdf_service import extract_and_chunk, retrieve_chunks

st.set_page_config(page_title="MindMate", page_icon="🧠", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --ink: #172426;
        --muted: #647476;
        --teal: #167c72;
        --teal-dark: #105e58;
        --mint: #e7f4ef;
        --paper: #f7faf8;
        --line: #e3ebe7;
    }

    html, body, [class*="css"] {
        font-family: 'Avenir Next', 'Segoe UI', sans-serif;
        color: var(--ink);
    }

    .stApp {
        background:
            radial-gradient(ellipse at 92% 0%, rgba(201, 232, 220, .34), transparent 34rem),
            var(--paper);
    }

    [data-testid="stSidebar"] {
        background: #f0f6f2;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Avenir Next', 'Segoe UI', sans-serif;
        letter-spacing: -.03em;
    }

    h1, h2, h3 {
        font-family: 'Avenir Next', 'Segoe UI', sans-serif;
        letter-spacing: -.04em;
    }

    .brand-mark {
        color: var(--teal-dark);
        font: 800 1.55rem 'Avenir Next', 'Segoe UI', sans-serif;
        letter-spacing: -.06em;
        margin: 0 0 .1rem;
    }

    .eyebrow {
        color: var(--teal);
        font-size: .75rem;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: .45rem;
    }

    .hero {
        background: linear-gradient(118deg, #e5f3ed 0%, #f1f7f2 54%, #f8f5e9 100%);
        border: 1px solid #dcebe3;
        border-radius: 24px;
        padding: 2rem 2.2rem;
        margin: .25rem 0 1.35rem;
    }

    .hero h1 {
        color: #173c38;
        font-size: clamp(2rem, 3.8vw, 3.3rem);
        line-height: 1.08;
        margin: 0;
    }

    .hero p {
        color: #4c6863;
        font-size: 1.05rem;
        margin: .7rem 0 0;
        max-width: 42rem;
    }

    .mode-card {
        background: #fff;
        border: 1px solid var(--line);
        border-radius: 18px;
        min-height: 128px;
        padding: 1.1rem 1.2rem;
        margin-bottom: .55rem;
    }

    .mode-card .icon {
        font-size: 1.45rem;
        margin-bottom: .4rem;
    }

    .mode-card strong {
        color: #193c38;
        display: block;
        font: 700 1rem 'Avenir Next', 'Segoe UI', sans-serif;
        margin-bottom: .2rem;
    }

    .mode-card span {
        color: var(--muted);
        font-size: .88rem;
        line-height: 1.4;
    }

    [data-testid="stMetric"] {
        background: #fff;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: .8rem 1rem;
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: var(--teal);
        border-color: var(--teal);
        border-radius: 10px;
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {
        background: var(--teal-dark);
        border-color: var(--teal-dark);
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
        border-radius: 10px;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid var(--line);
        border-radius: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_chunks" not in st.session_state:
    st.session_state.pdf_chunks = []
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""
if "study_notes" not in st.session_state:
    st.session_state.study_notes = ""
if "mode_selector" not in st.session_state:
    st.session_state.mode_selector = "Overview"

learning_modes = [
    "Overview",
    "Socratic Tutor",
    "Examples & Visuals",
    "Verify Before Trusting",
    "Knowledge Check",
    "Reflection Mode",
    "PDF Learning",
]

def open_mode(selected_mode):
    st.session_state.mode_selector = selected_mode

with st.sidebar:
    st.markdown('<div class="brand-mark">🧠 MindMate</div>', unsafe_allow_html=True)
    st.caption("YOUR LEARNING STUDIO")
    st.divider()
    mode = st.radio(
        "WORKSPACE",
        learning_modes,
        key="mode_selector",
    )
    st.divider()
    if st.session_state.get("tutor_topic"):
        st.caption("IN PROGRESS")
        st.markdown(f"**{st.session_state.tutor_topic}**")
        st.caption(f"{st.session_state.tutor_level} • Socratic lesson")
        st.divider()
    st.caption("MindMate • Learning prototype")
    st.caption("AI responses may be simulated when no API key is configured.")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        if "tutor_history" in st.session_state:
            st.session_state.tutor_history = []
        st.rerun()

def show_answer(prompt, system_prompt, simulated_prompt):
    with st.spinner("MindMate is thinking..."):
        answer, source = generate(system_prompt, prompt, simulated_prompt)
    st.markdown(answer)
    st.caption(f"Response mode: {source}")

def show_visual_aid(mode_key, topic, steps, example_title, example_text):
    st.markdown("### A picture for your thinking")
    st.caption("Follow the three steps, then try the mini-example.")
    columns = st.columns([5, 1, 5, 1, 5])
    for index, (label, detail) in enumerate(steps):
        with columns[index * 2]:
            with st.container(border=True):
                st.caption(f"STEP {index + 1}")
                st.markdown(f"**{label}**")
                st.caption(detail)
        if index < len(steps) - 1:
            with columns[index * 2 + 1]:
                st.markdown("### →")

    st.info(f"**{example_title}**\n\n{example_text}")
    with st.expander(f"Find pictures for {topic or 'this topic'}"):
        if not topic:
            st.caption("Enter a topic or claim first to search for related pictures.")
        elif st.button("Search Wikimedia Commons", key=f"{mode_key}_image_search"):
            try:
                st.session_state[f"{mode_key}_images"] = search_commons_images(topic)
                st.session_state[f"{mode_key}_image_error"] = ""
            except ImageSearchError as error:
                st.session_state[f"{mode_key}_images"] = []
                st.session_state[f"{mode_key}_image_error"] = str(error)

        image_error = st.session_state.get(f"{mode_key}_image_error", "")
        images = st.session_state.get(f"{mode_key}_images", [])
        if image_error:
            st.warning(image_error)
        elif images:
            image_columns = st.columns(min(2, len(images)))
            for index, image in enumerate(images):
                with image_columns[index % len(image_columns)]:
                    st.image(image["thumbnail_url"], use_container_width=True)
                    st.caption(
                        f"{image['title'].removeprefix('File:')} · "
                        f"{image['artist']} · {image['license']}"
                    )
                    st.markdown(f"[Source and license]({image['source_url']})")
        else:
            st.caption("Pictures are optional; explanations and diagrams work without them.")

if mode == "Overview":
    st.markdown(
        """
        <section class="hero">
            <div class="eyebrow">A calmer way to learn</div>
            <h1>Think deeper.<br>Learn at your pace.</h1>
            <p>Choose a study mode, explore a tricky idea, and keep your own notes as you go.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    active_topic = st.session_state.get("tutor_topic") or "No lesson started"
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Ways to learn", "6", "Pick the approach that fits")
    metric_b.metric("Current lesson", active_topic)
    metric_c.metric(
        "Notes in this session",
        f"{len(st.session_state.study_notes.split())} words",
        "Private to this browser session",
    )

    st.markdown("### Choose your next step")
    st.caption("Each mode is designed to help you do the thinking, not just collect answers.")
    mode_cards = [
        ("💬", "Socratic Tutor", "Work through an idea one question at a time."),
        ("🖼️", "Examples & Visuals", "Explore real-world examples and topic images."),
        ("🔎", "Verify Before Trusting", "Unpack claims and identify evidence to seek."),
        ("📝", "Knowledge Check", "Generate practice questions for a topic."),
        ("🪞", "Reflection Mode", "Explain an idea and spot gaps in your understanding."),
        ("📄", "PDF Learning", "Ask questions using passages from your own document."),
    ]
    for row_start in range(0, len(mode_cards), 3):
        cols = st.columns(3)
        for col, (icon, title, description) in zip(cols, mode_cards[row_start:row_start + 3]):
            with col:
                st.markdown(
                    f'<div class="mode-card"><div class="icon">{icon}</div>'
                    f'<strong>{title}</strong><span>{description}</span></div>',
                    unsafe_allow_html=True,
                )
                st.button(
                    f"Open {title}",
                    key=f"open_{title}",
                    use_container_width=True,
                    on_click=open_mode,
                    args=(title,),
                )

    st.markdown("### Your study notebook")
    st.caption("Capture a question, a useful idea, or something you want to revisit. Notes are not uploaded.")
    st.text_area(
        "Notes",
        key="study_notes",
        height=140,
        placeholder="One thing I understand better now is...\nA question I still have is...",
        label_visibility="collapsed",
    )
    if st.session_state.study_notes.strip():
        st.download_button(
            "Download notes",
            data=f"# MindMate study notes\n\n{st.session_state.study_notes}\n",
            file_name="mindmate-study-notes.md",
            mime="text/markdown",
        )

elif mode == "Socratic Tutor":
    st.markdown('<div class="eyebrow">Learn by exploring</div>', unsafe_allow_html=True)
    st.subheader("💬 Socratic Tutor")
    st.write(
        "Build your understanding one step at a time. "
        "MindMate will ask questions before giving a full explanation."
    )

    if "tutor_topic" not in st.session_state:
        st.session_state.tutor_topic = ""
    if "tutor_level" not in st.session_state:
        st.session_state.tutor_level = "Beginner"
    if "tutor_history" not in st.session_state:
        st.session_state.tutor_history = []

    with st.form("tutor_start_form"):
        topic = st.text_input(
            "What would you like to understand?",
            value=st.session_state.tutor_topic,
            placeholder="e.g. supervised machine learning"
        )

        levels = ["Beginner", "Intermediate", "Advanced"]

        level = st.selectbox(
            "Your current level",
            levels,
            index=levels.index(st.session_state.tutor_level)
        )

        start = st.form_submit_button(
            "Start or restart lesson",
            type="primary"
        )

    system = (
        "You are MindMate, a patient Socratic tutor. "
        "Help the learner construct understanding. "
        "Ask one clear guiding question at a time. "
        "Give a small hint if useful. Avoid giving the full "
        "answer immediately unless the learner asks. "
        "Be encouraging and concise."
    )

    if start and topic.strip():
        st.session_state.tutor_topic = topic.strip()
        st.session_state.tutor_level = level
        st.session_state.tutor_history = []

        prompt = (
            f"Start a Socratic lesson about {topic.strip()} "
            f"for a {level.lower()} learner. "
            "Ask one accessible opening question and give "
            "a small hint. Include one brief, original everyday example "
            "that the learner can test against the idea. Do not give the "
            "full definition yet."
        )

        simulated = (
            f"Let's explore **{topic.strip()}** together.\n\n"
            "**First question:** Where have you seen this idea "
            "used, or what do you already know about it?\n\n"
            "Hint: Start with a real-world example."
        )

        answer, source = generate(system, prompt, simulated)

        st.session_state.tutor_history.append({
            "role": "assistant",
            "content": answer,
            "source": source
        })

    if st.session_state.tutor_topic:
        st.caption(
            f"Current lesson: {st.session_state.tutor_topic} "
            f"• {st.session_state.tutor_level}"
        )

        for message in st.session_state.tutor_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                if message["role"] == "assistant":
                    st.caption(
                        f"Response mode: {message.get('source', 'unknown')}"
                    )

        show_visual_aid(
            "tutor",
            st.session_state.tutor_topic,
            [
                ("Your idea", "Say what you think is happening."),
                ("Tiny case", "Try it in a familiar situation."),
                ("Next clue", "Notice what still needs explaining."),
            ],
            "Mini-case: the campus café",
            "A café keeps running out of muffins before lunch. Use your topic to "
            "think through what information the café could notice, what decision "
            "it might make, and what result would show the decision helped. Treat "
            "this as a case to adapt, not a definition of every topic.",
        )
    else:
        show_visual_aid(
            "tutor",
            "",
            [
                ("Choose an idea", "Start with a topic you are curious about."),
                ("Try a small case", "Connect it to an ordinary situation."),
                ("Build understanding", "Use a question to take the next step."),
            ],
            "Example: turn a big topic into a small question",
            "Pick one everyday process—like choosing a route to school—and ask "
            "which part of your topic could help explain a choice or outcome.",
        )

    if st.session_state.tutor_topic:
        learner_reply = st.chat_input(
            "Write your answer or ask for a hint..."
        )

        if learner_reply:
            st.session_state.tutor_history.append({
                "role": "user",
                "content": learner_reply
            })

            conversation = "\n".join(
                f"{m['role'].upper()}: {m['content']}"
                for m in st.session_state.tutor_history[-8:]
            )

            prompt = (
                f"Lesson topic: {st.session_state.tutor_topic}\n"
                f"Learner level: {st.session_state.tutor_level}\n"
                f"Recent conversation:\n{conversation}\n"
                "Respond to the learner's latest message. When useful, offer "
                "one fresh, concrete everyday example connected to the topic. "
                "Ask one next guiding question. "
                "Do not reveal a complete answer unless requested."
            )

            simulated = (
                "Good thinking. Can you explain **why** your answer "
                "makes sense, or give a concrete example? "
                "If you are unsure, type 'hint' and I will offer a clue."
            )

            answer, source = generate(system, prompt, simulated)

            st.session_state.tutor_history.append({
                "role": "assistant",
                "content": answer,
                "source": source
            })

            st.rerun()

elif mode == "Examples & Visuals":
    st.markdown('<div class="eyebrow">Make ideas concrete</div>', unsafe_allow_html=True)
    st.subheader("🖼️ Examples & Visuals")
    st.write(
        "Search a topic for everyday examples, a clear explanation, and related images "
        "from Wikimedia Commons."
    )
    with st.form("examples_form"):
        topic = st.text_input(
            "What topic would you like to explore?",
            placeholder="e.g. computer vision, photosynthesis, or supply and demand",
        )
        level = st.selectbox("Explanation level", ["Beginner", "Intermediate", "Advanced"])
        search = st.form_submit_button("Find examples & visuals", type="primary")

    if search:
        if not topic.strip():
            st.warning("Enter a topic to search.")
        else:
            topic = topic.strip()
            prompt = (
                f"Teach the topic '{topic}' to a {level.lower()} learner. "
                "Give a clear short explanation, three specific real-world examples "
                "with enough detail to make each one concrete, and a simple text-based "
                "diagram showing how the idea works. Explain any analogy and where it "
                "stops being accurate. Use concise headings."
            )
            system = (
                "You are a clear, careful learning guide. Make examples specific to the "
                "topic, distinguish examples from analogies, and do not invent facts. "
                "If uncertain about a factual detail, say so."
            )
            simulated = (
                f"### Explore {topic}\n\n"
                f"**Start with the idea:** Write a one-sentence definition of {topic} "
                "using your own words, then compare it with a trusted course source.\n\n"
                "### Three ways to find examples\n"
                f"1. **Everyday life:** Look for a familiar situation where {topic} "
                "might appear. What is happening, and what clues connect it to the idea?\n"
                f"2. **Real-world use:** Find an organization, tool, or profession that "
                f"uses {topic}. Identify the problem it helps solve.\n"
                f"3. **Compare and contrast:** Find a case that looks like {topic} but "
                "is not. Which important feature is missing?\n\n"
                "### Sketch the idea\n"
                f"`Situation → key {topic} idea → result`\n\n"
                "**Demo mode:** These are guided example-finding prompts, not verified "
                "topic-specific examples. Add an OpenAI API key for tailored examples."
            )
            with st.spinner("Building an explanation and searching for images..."):
                answer, source = generate(system, prompt, simulated)
                try:
                    images = search_commons_images(topic)
                    image_error = ""
                except ImageSearchError as error:
                    images = []
                    image_error = str(error)

            st.session_state.examples_topic = topic
            st.session_state.examples_answer = answer
            st.session_state.examples_source = source
            st.session_state.examples_images = images
            st.session_state.examples_image_error = image_error

    if st.session_state.get("examples_topic"):
        st.markdown(f"### Learning guide: {st.session_state.examples_topic}")
        st.markdown(st.session_state.examples_answer)
        st.caption(f"Explanation mode: {st.session_state.examples_source}")

        st.markdown("### Related pictures")
        if st.session_state.examples_image_error:
            st.warning(st.session_state.examples_image_error)
        elif not st.session_state.examples_images:
            st.info("No matching images were found. Try a shorter or more specific topic.")
        else:
            image_columns = st.columns(min(2, len(st.session_state.examples_images)))
            for index, image in enumerate(st.session_state.examples_images):
                with image_columns[index % len(image_columns)]:
                    st.image(image["thumbnail_url"], use_container_width=True)
                    st.write(image["title"].removeprefix("File:"))
                    st.caption(f"Author: {image['artist']} • License: {image['license']}")
                    st.markdown(f"[View source and license]({image['source_url']})")
        st.caption(
            "Images are retrieved from Wikimedia Commons. Review each source page for "
            "full license and attribution details before reuse."
        )

elif mode == "Verify Before Trusting":
    st.markdown('<div class="eyebrow">Practice critical thinking</div>', unsafe_allow_html=True)
    st.subheader("🔎 Verify Before Trusting")
    st.write("Break down a claim and decide what evidence would be needed before accepting it.")
    claim = st.text_area("Enter a claim or AI-generated statement", placeholder="e.g. Generative AI always improves student learning.")
    show_visual_aid(
        "verify",
        claim.strip(),
        [
            ("The claim", "What exactly is being promised?"),
            ("The evidence", "What comparison could test it?"),
            ("Your view", "What remains uncertain?"),
        ],
        "Mini-case: a study app's big promise",
        "An app says its new reminder feature raises test scores by 20%. Before "
        "believing it, ask who was compared, how scores were measured, and whether "
        "another change could explain the result. This is a practice example, "
        "not a verified real-world claim.",
    )
    if st.button("Examine this claim", type="primary") and claim.strip():
        prompt = (
            f"Analyse this claim: {claim}\nIdentify its key assumptions, what "
            "evidence would support or weaken it, possible confounders, and 3 "
            "verification questions. Include one short, clearly hypothetical "
            "worked example showing how to test the claim. Do not assert that "
            "you have independently verified it."
        )
        system = ("You are a critical-thinking coach. Do not claim to fact-check or verify a claim unless evidence "
                  "is supplied. Distinguish claim, assumption, evidence required, uncertainty and next steps. "
                  "Encourage the student to consult credible primary sources.")
        simulated = ("### Claim\n" + claim + "\n\n### What should be checked?\n"
                     "- What terms need a precise definition?\n- What reliable evidence would support this statement?\n"
                     "- Are there counterexamples or alternative explanations?\n\n"
                     "### Verification questions\n1. Who produced the evidence, and what is their expertise?\n"
                     "2. Is the evidence based on an appropriate sample or method?\n"
                     "3. Do independent sources reach a similar conclusion?\n\n"
                     "**Caution:** This is a critical-thinking analysis, not an independent fact-check.")
        show_answer(prompt, system, simulated)

elif mode == "Knowledge Check":
    st.markdown('<div class="eyebrow">Practice active recall</div>', unsafe_allow_html=True)
    st.subheader("📝 Knowledge Check")
    topic = st.text_input("Quiz topic", placeholder="e.g. human-computer interaction")
    show_visual_aid(
        "quiz",
        topic.strip(),
        [
            ("Recall", "Name the key idea."),
            ("Apply", "Use it in a new situation."),
            ("Explain", "Show why your answer fits."),
        ],
        "Mini-case: the event-day bike-share",
        f"A bike-share team prepares for a busy stadium event. Create one quiz "
        f"question asking a learner to use '{topic or 'their topic'}' to solve a "
        "concrete problem, then explain what a strong answer should include.",
    )
    if st.button("Generate quiz", type="primary") and topic.strip():
        prompt = (
            f"Create 4 short questions about {topic}. Mix recall and application. "
            "Include one original, concrete mini-scenario that requires transferring "
            "the concept to an unfamiliar situation. Give questions first, then an "
            "answer key under a clearly labelled section with brief explanations."
        )
        system = "You are an educational assessment assistant. Make accurate, level-appropriate questions and explain answers clearly."
        simulated = (f"### Quick quiz: {topic}\n\n"
                     "1. Define the central concept in your own words.\n"
                     "2. Give one practical example.\n"
                     "3. Explain how it differs from a closely related concept.\n"
                     "4. Apply it to a simple real-world scenario.\n\n"
                     "### Self-check guidance\nReview your notes after answering. A strong answer should define the concept, give a relevant example, and explain your reasoning.")
        show_answer(prompt, system, simulated)

elif mode == "Reflection Mode":
    st.markdown('<div class="eyebrow">Make your thinking visible</div>', unsafe_allow_html=True)
    st.subheader("🪞 Reflection Mode")
    st.write("Explain what you have learned. MindMate will help you identify strengths and gaps.")
    concept = st.text_input("Concept you are learning", placeholder="e.g. cognitive offloading")
    reflection = st.text_area("Explain it in your own words", height=180)
    show_visual_aid(
        "reflection",
        concept.strip(),
        [
            ("Explain it", "Use your own words."),
            ("Give an example", "Show where the idea appears."),
            ("Find a boundary", "Say where it may not fit."),
        ],
        "Mini-case: explain it to a new learner",
        f"Try explaining '{concept or 'your concept'}' to a classmate using one "
        "ordinary situation. Then add one sentence about where your example stops "
        "being a perfect match. That boundary often reveals what you understand.",
    )
    if st.button("Review my understanding", type="primary") and concept.strip() and reflection.strip():
        prompt = (
            f"Concept: {concept}\nStudent explanation: {reflection}\nGive supportive "
            "feedback: identify what is understood, any ambiguity or missing ideas, "
            "and one follow-up question. Include one novel everyday example that "
            "could help clarify a gap, and explain the limit of that example. Do not "
            "grade harshly."
        )
        system = ("You are a supportive learning coach. Evaluate the student's explanation constructively. "
                  "Do not assume their answer is wrong merely because it is concise. Identify strengths, "
                  "possible gaps, and ask one question that deepens understanding.")
        simulated = (f"### Reflection on {concept}\n\n"
                     "**What is working:** You have made an attempt to explain the idea in your own words, which is a useful learning strategy.\n\n"
                     "**Check for gaps:** Compare your explanation with your lecture notes. Have you included the key definition, why the concept matters, and an example?\n\n"
                     "**Follow-up question:** Can you give a specific example of {concept} and explain why it fits?")
        show_answer(prompt, system, simulated)

elif mode == "PDF Learning":
    st.markdown('<div class="eyebrow">Learn from your materials</div>', unsafe_allow_html=True)
    st.subheader("📄 PDF Learning")
    st.write("Upload a text-based PDF, then ask questions grounded in relevant extracted passages.")
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded is not None:
        if uploaded.name != st.session_state.pdf_name:
            st.session_state.pop("pdf_last_question", None)
            st.session_state.pop("pdf_last_passages", None)
            st.session_state.pop("pdf_last_answer", None)
            st.session_state.pop("pdf_last_source", None)
            try:
                st.session_state.pdf_chunks = extract_and_chunk(uploaded.getvalue())
                st.session_state.pdf_name = uploaded.name
                st.success(f"Loaded {uploaded.name} — {len(st.session_state.pdf_chunks)} text chunks extracted.")
            except Exception as exc:
                st.error(f"Could not read this PDF: {exc}")
        if not st.session_state.pdf_chunks:
            st.warning("No extractable text found. This may be a scanned PDF; OCR is not included in this prototype.")
    if st.session_state.pdf_chunks:
        question = st.text_input("Ask a question about the uploaded document")
        if st.button("Ask document", type="primary") and question.strip():
            passages = retrieve_chunks(question, st.session_state.pdf_chunks, top_k=3)
            context = "\n\n".join(f"[Page {p['page']}] {p['text']}" for p in passages)
            prompt = (
                "Answer the question using ONLY the supplied document excerpts. "
                "If they do not contain the answer, say so. Cite page numbers in "
                "the answer. When the excerpts support it, give one concrete example "
                "or simple text diagram grounded in the document. Never invent "
                "document examples or facts.\n\n"
                f"EXCERPTS:\n{context}\n\nQUESTION: {question}"
            )
            system = ("You answer questions about an uploaded academic document. Use only supplied excerpts. "
                      "Do not invent facts or page references. If evidence is insufficient, say that clearly.")
            if passages:
                simulated = (
                    "### Evidence found in your PDF\n\n"
                    + context
                    + "\n\n**Try this example:** Choose one sentence above. Explain the "
                    "idea in your own words, then point to the exact page and phrase "
                    "that supports your explanation.\n\n"
                    "**Demo mode:** This shows retrieved evidence rather than "
                    "generating a document-based synthesis."
                )
            else:
                simulated = (
                    "I couldn't find a matching passage in the extracted PDF text. "
                    "Try different words from the document or a more specific question."
                )
            with st.spinner("Searching the document..."):
                answer, source = generate(system, prompt, simulated)
            st.session_state.pdf_last_question = question
            st.session_state.pdf_last_passages = passages
            st.session_state.pdf_last_answer = answer
            st.session_state.pdf_last_source = source

        if st.session_state.get("pdf_last_question"):
            question = st.session_state.pdf_last_question
            passages = st.session_state.pdf_last_passages
            st.markdown(st.session_state.pdf_last_answer)
            st.caption(f"Response mode: {st.session_state.pdf_last_source}")
            show_visual_aid(
                "pdf",
                question,
                [
                    ("Your question", "What are you trying to understand?"),
                    ("PDF evidence", "Use only the retrieved page passages."),
                    ("Grounded answer", "Explain it and point to the page."),
                ],
                "Mini-case: show your evidence trail",
                (
                    f"Question: {question} "
                    + (
                        f"Start with page {passages[0]['page']}: "
                        f"“{passages[0]['text'][:180]}...”"
                        if passages
                        else "No matching excerpt was retrieved, so there is not enough PDF evidence to give a document-based example."
                    )
                ),
            )
            with st.expander("Show retrieved passages"):
                for p in passages:
                    st.markdown(f"**Page {p['page']}**")
                    st.write(p["text"])
        else:
            show_visual_aid(
                "pdf",
                "",
                [
                    ("Upload a PDF", "Choose a text-based course document."),
                    ("Ask a question", "Use words that appear in the document."),
                    ("Check the pages", "Trace the answer back to its evidence."),
                ],
                "Example: keep the evidence visible",
                "After a question is asked, use the page and matching excerpt to "
                "build a document-based example. MindMate should not add facts "
                "that are missing from your PDF.",
            )
    else:
        show_visual_aid(
            "pdf",
            "",
            [
                ("Upload a PDF", "Select a text-based learning document."),
                ("Find a passage", "Search for wording related to your question."),
                ("Explain with evidence", "Keep the page citation beside the idea."),
            ],
            "Example: a source-first explanation",
            "A learner asks what a highlighted term means, finds the page where "
            "it appears, and uses that passage—not a guess—to explain it.",
        )
    st.caption("PDF support in this prototype extracts selectable text. Scanned-image OCR is not implemented.")

st.divider()
st.caption("Educational prototype. Check important information against your course materials and reliable sources.")
