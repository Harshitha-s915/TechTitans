#  TechTitans Hackathon
## Agentic AI Gamified Coding & Interview Assistant

***

##  Overview
The **Agentic AI Gamified Coding & Interview Assistant** is an intelligent, adaptive learning platform designed to help students and aspiring developers strengthen both coding skills and interview performance.

Unlike traditional platforms that only **teach** or only **test**, this system acts like a smart mentor. It continuously observes user performance, adjusts the difficulty level, provides guidance in real time, and creates a personalized learning journey.

***

##  Problem Statement
Many learners struggle with common challenges during coding preparation:

- **Passive Learning:** Watching tutorials without enough hands-on problem solving.
- **Static Learning Paths:** Fixed content that does not adapt to the learner’s progress.
- **Delayed Feedback:** Lack of immediate correction and improvement suggestions.
- **Interview Readiness Gap:** Difficulty moving from basic syntax knowledge to real problem-solving under pressure.

***

##  Solution
This project introduces an **Agentic AI system** that creates a continuous learning and feedback loop.

It can:

1. **Teach concepts interactively** with explanations and examples.
2. **Generate coding challenges** based on the learner’s level.
3. **Evaluate user responses** as correct, partial, or incorrect.
4. **Provide hints gradually** to encourage critical thinking.
5. **Simulate interview scenarios** for realistic practice.

***

##  Core Concept: Agentic Loop
This system is not a simple linear chatbot. It follows a dynamic decision cycle:

> **Teach → Test → Evaluate → Adapt → Repeat**

The internal agent logic decides what should happen next based on the learner’s performance. If the learner performs well, the difficulty increases. If the learner struggles, the system can return to teaching mode or provide step-by-step hints.

***

##  Features

| Feature | Description |
| :--- | :--- |
| ** Teach Mode** | Explains programming concepts with examples and syntax breakdowns. |
| ** Challenge Mode** | Generates dynamic coding tasks based on topic and difficulty. |
| ** Evaluation Mode** | Classifies answers as  Correct,  Partial, or  Incorrect. |
| ** Hint Mode** | Offers logical guidance without directly revealing the full answer. |
| ** Interview Mode** | Simulates technical interviews with focus on logic, communication, and confidence. |

***

##  Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.x
- **AI Integration:** OpenAI / Gemini / Groq *(optional)*
- **Architecture:** State-machine-based agentic logic

***

##  Project Structure

```text
project/
│
├── app.py            # Main Streamlit UI and entry point
├── agent.py          # Core decision-making and state logic
├── prompts.py        # Prompt templates for AI interactions
├── utils.py          # Helper functions and formatting utilities
├── state.py          # Session state and progress tracking
├── requirements.txt  # Project dependencies
└── .env              # Environment variables and API keys
```

***

##  Installation & Setup

### 1. Clone the repository

```bash
git clone <your-repo-link>
cd project
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

***

##  What Makes This Unique?

- **Agent-Based Decision System:** The platform reacts intelligently instead of following a fixed question sequence.
- **Gamified Learning Flow:** Users can progress through levels based on performance.
- **Hint-First Learning Philosophy:** Encourages understanding instead of spoon-feeding answers.
- **Flexible Architecture:** Can work with powerful LLMs or use structured fallback logic.

***

##  Future Roadmap

- **Multi-language Support:** Expand beyond Python, Java, and C++.
- **Advanced Evaluation:** Analyze code quality, efficiency, and complexity.
- **Progress Persistence:** Integrate Supabase or Firebase for long-term tracking.
- **Multiplayer Practice:** Real-time coding battles and collaborative challenges.

***

##  Author
Developed for the **TechTitans Hackathon** to explore how **Agentic AI** can transform technical education, coding practice, and interview preparation.
