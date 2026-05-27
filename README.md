# 🛡️ SOX Compliance AI Assistant

An AI-powered chatbot for SOX compliance, ITGC/ITAC testing, and IT audit guidance — built with Streamlit and OpenAI.

**Live Demo**: [Deploy link once hosted on Streamlit Cloud]

---

## What it does

- Answers questions on SOX § 302 / § 404, ITGC, ITAC, and IPE testing
- Covers Access Management, Change Management, Computer Operations controls
- Explains SoD (Segregation of Duties) conflicts in SAP S/4HANA and ECC
- Guides auditors on evidence collection and control deficiency classification
- Maintains full conversation history so follow-up questions work naturally

## Tech stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| LLM | OpenAI gpt-4o |
| Memory | Streamlit session state (full context window) |
| Deployment | Streamlit Community Cloud (free) |

## Local setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/sox-compliance-assistant
cd sox-compliance-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Enter your [OpenAI API key](https://platform.openai.com/api-keys) in the sidebar when the app opens.

## Deploy to Streamlit Cloud (free, public URL)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → select `app.py` as the entrypoint
4. Under **Settings → Secrets**, add:
   ```
   OPENAI_API_KEY = "sk-ant-your-key-here"
   ```
5. Deploy — you get a public URL like `https://your-app.streamlit.app`

## System prompt design

The assistant is grounded in a detailed system prompt covering:
- SOX ITGC domains (Access, Change, Computer Operations, Program Development)
- ITAC and IPE testing methodology
- COBIT 2019 framework alignment
- SAP transaction-level audit evidence
- Control deficiency classification standards

This prompt was designed using structured prompt engineering techniques — see [Prompt Engineering project](link-to-your-prompt-library-repo) for the methodology.

## Author

**Om Dhede** — IT Audit Analyst at KPMG India (BSR & Co. LLP) | B.Tech AI & Data Science  
[LinkedIn](https://linkedin.com/in/yourprofile) | [Portfolio](https://yourportfolio.com) | [GitHub](https://github.com/yourusername)
