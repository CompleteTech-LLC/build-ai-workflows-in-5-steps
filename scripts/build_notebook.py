#!/usr/bin/env python3
"""Build build_ai_workflows_in_5_steps.ipynb from source.

Source of truth for the notebook. Run `python scripts/build_notebook.py`
from the project root to regenerate the .ipynb after editing cell content.

Why Python-as-source instead of editing the .ipynb directly:
- version control diffs are readable (Python > JSON)
- cells can be reordered and re-cut without hand-JSON surgery
- escaping hell is avoided (triple-quoted strings > string-escaped JSON)
"""
import json
from pathlib import Path

OUTPUT = Path(__file__).parent.parent / "build_ai_workflows_in_5_steps.ipynb"


def md(source: str, hidden: bool = False) -> dict:
    meta: dict = {}
    if hidden:
        meta["jupyter"] = {"source_hidden": True}
    return {
        "cell_type": "markdown",
        "metadata": meta,
        "source": source.lstrip("\n").splitlines(keepends=True),
    }


def code(source: str, hidden: bool = False) -> dict:
    meta: dict = {}
    if hidden:
        meta["jupyter"] = {"source_hidden": True}
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": meta,
        "outputs": [],
        "source": source.lstrip("\n").splitlines(keepends=True),
    }


# ============================================================================
# CELL 1 — Header
# ============================================================================
CELL_1 = '''
<div align="center">

# Build AI Workflows in 5 Steps

**From goal image to executable workflow code, in one notebook, any AI provider.**

</div>

---

## What you will build

In this notebook you will watch an AI read a goal, then a source document, then design its own workflow to get from one to the other — and finally hand you reusable code that runs that workflow for you.

By the end you will have turned a messy PDF into an executable AI pipeline in under 10 minutes, while learning five advanced prompting techniques that work across Anthropic, OpenAI, and Google.

## Who this is for

**Total beginners** (no Python experience) and **experienced developers** both. Beginners can run every cell top-to-bottom without reading the adapter code. Experienced readers will get the most value from reading every cell — especially the adapter in Cell 5, which shows real vendor SDK code without a third-party abstraction layer hiding the details.

## What you will learn

1. **Context Priming** — load your goal and source into the AI in stages (Steps 1 and 2)
2. **Task Decomposition** — have the AI design a repeatable workflow with a structured execution contract (Step 3)
3. **Visual Workflow Design** — render the workflow as a Mermaid diagram you can share (Step 4)
4. **Workflow Crystallization** — turn the workflow into executable code so future runs skip the expensive AI calls (Step 5)

## How to use this notebook

- **Just want to run it?** Click Run All. The default assets in `assets/` will work end to end.
- **Want to use your own files?** Scroll to Cell 7 (`YOUR INPUTS`) and swap the two file paths. That is the only line you need to change.
- **Want to switch providers?** Set an API key for Anthropic, OpenAI, or Google in your environment. The notebook auto-detects which you have.

**Estimated time:** 15 minutes to read, 5 minutes to run.
**Estimated cost:** 10–50 cents per full run on the default flagship models. Cheaper models are one line away — see Cell 6.
'''

# ============================================================================
# CELL 2 — Prerequisites
# ============================================================================
CELL_2 = '''
## Before you run this

You need **one** API key. Not all three — just whichever you prefer:

| Provider | Where to get a key | Free tier? |
|---|---|---|
| **Anthropic** (Claude) | https://console.anthropic.com/settings/keys | $5 trial credit |
| **OpenAI** (GPT) | https://platform.openai.com/api-keys | Pay-as-you-go |
| **Google** (Gemini) | https://aistudio.google.com/apikey | Yes — generous free tier, no credit card required |

**First time with AI APIs?** Google AI Studio gives you a free Gemini key in under 60 seconds with no credit card. Recommended starting point.

## Where to put your key

Two options — pick whichever is more convenient:

- **Session only (easiest for one-off runs).** Run Cell 6 and you'll get a hidden input prompt. The key stays in memory for this kernel session only and is never written to disk.
- **`.env` file (recommended for repeat runs).** Create a file named `.env` in the same folder as this notebook. The notebook auto-loads it in Cell 6.

Example `.env` contents — pick the one line matching your provider:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
```

The `.env` file is listed in `.gitignore` and will never be committed to Git. A `.env.example` template ships with the repo — copy it to `.env` and fill in your key.

### Want to pick a specific provider or a cheaper model?

By default the notebook auto-detects which key you have and uses that provider's flagship model. To override, add one or both of these lines to your `.env`:

```
PROVIDER=openai
MODEL=gpt-4o-mini
```

…or uncomment a pre-built selector line in Cell 6. Switching providers is literally a one-line edit — this is how you compare Claude / GPT / Gemini on the same workflow.

## What else you need

- **Python 3.10 or newer** (check with `python --version`)
- **Jupyter** — via VS Code with the Python + Jupyter extensions, classic JupyterLab, or Google Colab
- **Internet connection** — the AI calls are live

## Estimated cost to run

This notebook defaults to the **latest flagship models** from each provider (as of April 2026):

| Provider | Default model | Input ($/M tok) | Output ($/M tok) |
|---|---|---:|---:|
| Anthropic | `claude-opus-4-6` | $5.00 | $25.00 |
| OpenAI | `gpt-5.4` | $2.50 | $15.00 |
| Google | `gemini-3.1-pro-preview` | $2.00 | $12.00 |

Running the whole notebook once at flagship-tier costs roughly **$0.10–$0.50** depending on provider and how verbose the model is. If cost matters more than capability for your use case, pass a cheaper model explicitly: `AIClient("anthropic", model="claude-haiku-4-5")` or similar. The pricing table is inside Cell 5 — update it when providers change prices or ship new models.
'''

# ============================================================================
# CELL 3 — Install dependencies
# ============================================================================
CELL_3 = '''
# Install the three vendor SDKs, pypdf for PDF text extraction, and
# python-dotenv so your key can live in a .env file.
# Safe to re-run: pip is quiet when everything is already installed.
%pip install -q anthropic openai google-genai pypdf python-dotenv
'''

# ============================================================================
# CELL 4 — Meet AIClient (explainer)
# ============================================================================
CELL_4 = '''
## Meet `AIClient` — your universal AI interface

The next cell defines a small class called `AIClient`. It is the **only** part of this notebook that talks to an AI provider. Every lesson below will call `ai.ask(...)` and it works regardless of whether you are using Anthropic, OpenAI, or Google.

### Why a thin adapter instead of LiteLLM?

LiteLLM is a great library, but for a *lesson* its abstraction hides the exact thing we want you to see: what each vendor's SDK actually looks like. When you leave this notebook and land on Stack Overflow, the Claude docs, or an OpenAI tutorial, you will see real SDK code — not LiteLLM. We are showing you that same real code here.

### Beginners: you can skip the next cell

The adapter is about 200 lines of code. If you are new to Python, **just run the cell and ignore the contents** — `AIClient` works like an appliance from your perspective. You will call `ai.ask(...)` later and get a reply. That is all you need to know.

### Advanced readers: read every line

You will see:

- How **Anthropic**, **OpenAI**, and **Google** each represent a message differently — and how we translate between them.
- How **assistant prefilling** works natively on Anthropic and is emulated on the other two.
- How **image content blocks** differ across providers. This matters immediately in Step 1.
- How to track **token usage** and **estimated cost** per call.
- How to handle **missing API keys** gracefully with `getpass`.

The adapter is legitimately reusable production code. Copy it, extend it, ship it.

> The next cell is **collapsed by default**. Click the ▸ arrow on the left to expand it if you want to read the code. If you are a beginner, just run it and move on.
'''

# ============================================================================
# CELL 5 — The adapter class (hidden by default)
# ============================================================================
CELL_5 = '''
"""
AIClient — a thin, provider-agnostic AI adapter.
==================================================

Wraps the Anthropic, OpenAI, and Google Gemini SDKs behind one method:
    ai.ask(messages, system=None, prefill=None, **kwargs)

Content helpers:
    ai.text(s)           -> opaque text block
    ai.image(path)       -> opaque image block
    ai.pdf_as_text(path) -> extract text from a PDF via pypdf

Bookkeeping:
    ai.last_usage   {"input_tokens", "output_tokens", "estimated_cost_usd"}
    ai.total_usage  running total across all calls

Read order for the curious:
    1. PRICING + DEFAULTS dicts
    2. __init__ and _get_key            (how we load keys)
    3. .ask()                            (the unified entry point)
    4. _ask_anthropic / _ask_openai /    (per-vendor translation)
       _ask_gemini
    5. _to_*_message helpers             (how content blocks differ)

The three _ask_* methods are where the real lesson lives. Read them
side by side to see what each vendor's SDK expects.
"""
import os
import base64
import getpass
from pathlib import Path

import pypdf


# Rough pricing in $/million tokens. Providers change prices; treat as estimates.
# Update these when providers release new models or adjust pricing.
PRICING = {
    "claude-opus-4-6":        {"in":  5.00, "out": 25.00},
    "gpt-5.4":                {"in":  2.50, "out": 15.00},
    "gemini-3.1-pro-preview": {"in":  2.00, "out": 12.00},
}

# Latest flagship model from each provider (as of April 2026).
# Override via AIClient(provider, model="...") for a cheaper or newer model.
DEFAULTS = {
    "anthropic": "claude-opus-4-6",
    "openai":    "gpt-5.4",
    "gemini":    "gemini-3.1-pro-preview",
}

ENV_KEYS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai":    "OPENAI_API_KEY",
    "gemini":    "GOOGLE_API_KEY",
}


class AIClient:
    """Provider-agnostic wrapper around Anthropic, OpenAI, and Google Gemini."""

    def __init__(self, provider: str, model: str | None = None):
        if provider not in ENV_KEYS:
            raise ValueError(f"provider must be one of {list(ENV_KEYS)}")
        self.provider = provider
        self.model = model or DEFAULTS[provider]
        self.api_key = self._get_key()
        self.last_usage: dict = {}
        self.total_usage: dict = {
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost_usd": 0.0,
        }
        self._client = self._make_client()
        print(f"Ready: {provider} / {self.model}")

    def _get_key(self) -> str:
        key = os.environ.get(ENV_KEYS[self.provider])
        if key:
            return key
        return getpass.getpass(
            f"Enter your {self.provider.upper()} API key: "
        ).strip()

    def _make_client(self):
        if self.provider == "anthropic":
            import anthropic
            return anthropic.Anthropic(api_key=self.api_key)
        if self.provider == "openai":
            import openai
            return openai.OpenAI(api_key=self.api_key)
        if self.provider == "gemini":
            from google import genai
            return genai.Client(api_key=self.api_key)

    # ---------- content helpers (same call site for all providers) ----------

    def text(self, s: str) -> dict:
        """Return an opaque text content block."""
        return {"_type": "text", "text": s}

    def image(self, path: str) -> dict:
        """Return an opaque image content block, resolved per-provider at send time."""
        data = base64.standard_b64encode(Path(path).read_bytes()).decode("ascii")
        ext = Path(path).suffix.lstrip(".").lower()
        mime = {
            "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png", "gif": "image/gif", "webp": "image/webp",
        }.get(ext, "image/png")
        return {"_type": "image", "mime": mime, "data": data}

    def pdf_as_text(self, path: str) -> str:
        """Extract raw text from a PDF using pypdf. Works identically on all providers."""
        reader = pypdf.PdfReader(path)
        return "\\n\\n".join((page.extract_text() or "") for page in reader.pages)

    # ---------- the unified ask method ----------

    def ask(
        self,
        messages: list,
        system: str | None = None,
        prefill: str | None = None,
        **kwargs,
    ) -> str:
        """Send messages to the selected provider and return the text response.

        messages: list of {"role": "user" | "assistant", "content": str or [blocks]}
        system:   optional system prompt (handled differently per provider)
        prefill:  force response to begin with this string
                  (native on Anthropic, emulated on OpenAI and Gemini)
        kwargs:   passed through to the underlying SDK (temperature, etc.)
        """
        try:
            if self.provider == "anthropic":
                return self._ask_anthropic(messages, system, prefill, **kwargs)
            if self.provider == "openai":
                return self._ask_openai(messages, system, prefill, **kwargs)
            if self.provider == "gemini":
                return self._ask_gemini(messages, system, prefill, **kwargs)
        except Exception as e:
            raise RuntimeError(self._friendly_error(e)) from e

    # ---------- Anthropic ----------

    def _ask_anthropic(self, messages, system, prefill, **kwargs):
        api_messages = [self._to_anthropic_message(m) for m in messages]
        if prefill:
            # Anthropic supports native assistant prefill: model continues from this text.
            api_messages.append({"role": "assistant", "content": prefill})
        params = {
            "model": self.model,
            "messages": api_messages,
            "max_tokens": kwargs.pop("max_tokens", 4096),
        }
        if system:
            params["system"] = system
        params.update(kwargs)
        response = self._client.messages.create(**params)
        text = "".join(b.text for b in response.content if hasattr(b, "text"))
        if prefill:
            text = prefill + text
        self._record_usage(response.usage.input_tokens, response.usage.output_tokens)
        return text

    def _to_anthropic_message(self, m):
        content = m["content"]
        if isinstance(content, str):
            return {"role": m["role"], "content": content}
        blocks = []
        for b in content:
            if isinstance(b, str):
                blocks.append({"type": "text", "text": b})
            elif b.get("_type") == "text":
                blocks.append({"type": "text", "text": b["text"]})
            elif b.get("_type") == "image":
                blocks.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": b["mime"],
                        "data": b["data"],
                    },
                })
        return {"role": m["role"], "content": blocks}

    # ---------- OpenAI ----------

    def _ask_openai(self, messages, system, prefill, **kwargs):
        api_messages = []
        if system:
            api_messages.append({"role": "system", "content": system})
        for m in messages:
            api_messages.append(self._to_openai_message(m))
        if prefill:
            # Emulated prefill: Chat Completions has no native assistant-prefill.
            # Inject a late system-level instruction nudging the response start.
            api_messages.append({
                "role": "system",
                "content": f"Begin your response with exactly: {prefill}",
            })
        params = {"model": self.model, "messages": api_messages}
        params.update(kwargs)
        response = self._client.chat.completions.create(**params)
        text = response.choices[0].message.content or ""
        self._record_usage(
            response.usage.prompt_tokens, response.usage.completion_tokens
        )
        return text

    def _to_openai_message(self, m):
        content = m["content"]
        if isinstance(content, str):
            return {"role": m["role"], "content": content}
        blocks = []
        for b in content:
            if isinstance(b, str):
                blocks.append({"type": "text", "text": b})
            elif b.get("_type") == "text":
                blocks.append({"type": "text", "text": b["text"]})
            elif b.get("_type") == "image":
                blocks.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{b['mime']};base64,{b['data']}",
                    },
                })
        return {"role": m["role"], "content": blocks}

    # ---------- Gemini ----------

    def _ask_gemini(self, messages, system, prefill, **kwargs):
        from google.genai import types
        contents = []
        for m in messages:
            # Gemini uses "model" instead of "assistant" for AI turns.
            role = "model" if m["role"] == "assistant" else "user"
            parts = self._to_gemini_parts(m["content"])
            contents.append({"role": role, "parts": parts})
        if prefill:
            # Emulated prefill on Gemini: trailing user instruction.
            contents.append({
                "role": "user",
                "parts": [{"text": f"Begin your response with exactly: {prefill}"}],
            })
        config_kwargs = {}
        if system:
            config_kwargs["system_instruction"] = system
        config_kwargs.update(kwargs)
        config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
        response = self._client.models.generate_content(
            model=self.model, contents=contents, config=config,
        )
        text = response.text or ""
        usage = getattr(response, "usage_metadata", None)
        if usage:
            self._record_usage(
                usage.prompt_token_count or 0,
                usage.candidates_token_count or 0,
            )
        return text

    def _to_gemini_parts(self, content):
        if isinstance(content, str):
            return [{"text": content}]
        parts = []
        for b in content:
            if isinstance(b, str):
                parts.append({"text": b})
            elif b.get("_type") == "text":
                parts.append({"text": b["text"]})
            elif b.get("_type") == "image":
                parts.append({
                    "inline_data": {"mime_type": b["mime"], "data": b["data"]},
                })
        return parts

    # ---------- bookkeeping ----------

    def _record_usage(self, input_tokens, output_tokens):
        p = PRICING.get(self.model, {"in": 0.0, "out": 0.0})
        cost = (input_tokens * p["in"] + output_tokens * p["out"]) / 1_000_000
        self.last_usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(cost, 6),
        }
        self.total_usage["input_tokens"] += input_tokens
        self.total_usage["output_tokens"] += output_tokens
        self.total_usage["estimated_cost_usd"] = round(
            self.total_usage["estimated_cost_usd"] + cost, 6,
        )

    def _friendly_error(self, e):
        s = str(e).lower()
        if any(t in s for t in ("401", "unauthorized", "invalid api key", "invalid_api_key")):
            return (
                f"Your {self.provider.upper()} API key looks invalid. "
                f"Check that {ENV_KEYS[self.provider]} is set correctly, "
                f"or restart the kernel and re-run the provider cell to enter a new one."
            )
        if any(t in s for t in ("429", "rate", "quota", "insufficient")):
            return (
                f"Rate-limited by {self.provider}. Wait ~30 seconds and try again, "
                f"or check your plan's quota."
            )
        if any(t in s for t in ("connection", "network", "timeout", "dns")):
            return f"Cannot reach {self.provider}. Check your internet connection and try again."
        return f"{self.provider} error: {e}"


def auto_detect_provider(preference_order=("anthropic", "openai", "gemini")):
    """Return the first provider whose API key is present in the environment, or None."""
    for p in preference_order:
        if os.environ.get(ENV_KEYS[p]):
            return p
    return None
'''

# ============================================================================
# CELL 6 — Pick your provider
# ============================================================================
CELL_6 = '''
import os

# Load keys (and optional PROVIDER / MODEL overrides) from a .env file in
# this folder. Anything already in os.environ wins; .env only fills gaps.
from pathlib import Path as _Path
if _Path(".env").exists():
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded .env")

# ============================================================
# === PROVIDER & MODEL SELECTION                            ===
# ============================================================
# Three ways to pick:
#   1. Leave both as None  -> auto-detect from whichever API key is in .env
#   2. Set PROVIDER= / MODEL= in your .env file
#   3. Uncomment a pair below to hard-code it in the notebook

PROVIDER = (os.environ.get("PROVIDER") or "").strip().lower() or None
MODEL    = (os.environ.get("MODEL") or "").strip() or None
if PROVIDER in ("auto", "default"):
    PROVIDER = None

# --- Flagship models (default, ~$0.10-$0.50 per full run) ---
# PROVIDER, MODEL = "anthropic", None                  # claude-opus-4-6
# PROVIDER, MODEL = "openai",    None                  # gpt-5.4
# PROVIDER, MODEL = "gemini",    None                  # gemini-3.1-pro-preview

# --- Cheaper mid-tier (~$0.01-$0.05 per full run) ---
# PROVIDER, MODEL = "anthropic", "claude-sonnet-4-5"
# PROVIDER, MODEL = "openai",    "gpt-4o-mini"
# PROVIDER, MODEL = "gemini",    "gemini-2.5-flash"
# ============================================================

# If still not set, auto-detect from whichever API key is in the environment.
# Preference order: Anthropic -> OpenAI -> Gemini.
if PROVIDER is None:
    PROVIDER = auto_detect_provider()

# If still not set (no keys at all), ask interactively.
if PROVIDER is None:
    print("No API key detected in your environment.")
    print("Pick a provider to enter a key for:")
    print("  1. anthropic  (Claude)")
    print("  2. openai     (GPT)")
    print("  3. gemini     (Google)")
    choice = input("Enter 1, 2, or 3: ").strip()
    PROVIDER = {"1": "anthropic", "2": "openai", "3": "gemini"}.get(choice, "gemini")

ai = AIClient(PROVIDER, model=MODEL)
'''

# ============================================================================
# CELL 7 — YOUR INPUTS
# ============================================================================
CELL_7 = '''
# ============================================================
# === YOUR INPUTS — swap these two lines to run on your own ===
# ============================================================
# The notebook works end to end with the defaults. Change either
# of these paths to retarget the whole workflow to your own files.

TARGET_IMAGE = "assets/target_dashboard.png"        # the end state you want
SOURCE_DOC   = "assets/source_financial_pack.pdf"   # the raw input you have

# ============================================================

from pathlib import Path
for label, path in [("TARGET_IMAGE", TARGET_IMAGE), ("SOURCE_DOC", SOURCE_DOC)]:
    assert Path(path).exists(), f"{label} not found at: {path}"
    print(f"OK  {label:12s}  {path}")
'''

# ============================================================================
# CELL 8 — Step 1 explainer
# ============================================================================
CELL_8 = '''
---

# Step 1 of 5 — Context Priming: Show the Goal

Most AI tutorials start by telling the model *what to do*. We are going to do something different: **show it what we want the finished thing to look like — and nothing else.**

## What is context priming?

**Context priming** is loading relevant information into the conversation *before* asking for any work. Think of it like briefing a colleague: you show them the problem, they say "got it," and *then* you ask for help.

We show the AI the goal image and explicitly tell it:

> *"Reply with only the single word: Continue"*

The AI takes in the image, says "Continue," and waits. No tokens wasted on unsolicited analysis. The goal is now part of the conversation history — the AI can refer back to it for the rest of the notebook.

### Why "Continue"?

Instead of letting the AI generate a paragraph of analysis the moment it sees your input, you clamp its response to a single word. That does two things:

1. **It anchors context.** The goal gets committed to the conversation history.
2. **It saves tokens.** Without this constraint, the AI would generate a paragraph analyzing the image — billable tokens that add nothing to the lesson.

### Why goal-first?

When you show an AI the *output* first, it can pattern-match the transformation it needs to perform. This is related to **reverse prompt engineering** in the research literature: starting from the desired result is often more effective than describing it from scratch.

Ready? Let us prime.
'''

# ============================================================================
# CELL 9 — Prime with the goal image
# ============================================================================
CELL_9 = '''
# Step 1: show the AI the target dashboard and have it acknowledge.

messages = [
    {
        "role": "user",
        "content": [
            ai.image(TARGET_IMAGE),
            (
                "Above is the final dashboard we want to produce. "
                "Do not describe it, analyze it, or ask questions. "
                "Reply with only the single word: Continue"
            ),
        ],
    },
]

reply = ai.ask(messages)

print(f"AI replied: {reply!r}")
print(f"Tokens this call: {ai.last_usage}")
'''

# ============================================================================
# CELL 10 — Verify the priming took
# ============================================================================
CELL_10 = '''
# The goal should now be part of the conversation context. Let us confirm
# by asking about it, without re-sending the image.
#
# We grow `history` as a running conversation log. Every subsequent lesson
# appends to it, so the AI carries the full primed context forward.

history = messages + [{"role": "assistant", "content": reply}]

history.append({
    "role": "user",
    "content": "In one short sentence, what are we trying to build?",
})
verification = ai.ask(history)
history.append({"role": "assistant", "content": verification})

print("AI's understanding of the goal:")
print(f"  {verification.strip()}")
print()
print(f"Cumulative tokens so far: {ai.total_usage}")
'''

# ============================================================================
# CELL 11 — Step 1 debrief
# ============================================================================
CELL_11 = '''
## What just happened (and what is next)

You just executed **context priming**. In two AI calls:

1. You showed the AI a goal image and got a one-word acknowledgment.
2. You verified the AI internalized the goal by asking about it — without having to re-send the image.

This is the foundation of every remaining lesson. In Step 2 you will do the same thing with the *source* document: load it once, get an acknowledgment, and both the goal and the source will be in the conversation context for Step 3 (Task Decomposition) to reason over.

### Token-cost sanity check

Look at `Tokens this call` and `Cumulative tokens so far` above. The image consumed roughly 500–1,500 tokens on most providers (images are quantized into fixed-size token budgets). Every subsequent turn in this notebook can now *reference* that goal for free — no re-upload needed.

### Under the hood (advanced readers)

- On **Anthropic**, the image went in as a `base64` content block inside the user message. You can see the exact shape in `_to_anthropic_message()` in the adapter cell above.
- On **OpenAI**, the same image became `{"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}`.
- On **Gemini**, it became `{"inline_data": {"mime_type": "image/png", "data": "..."}}`.

The point of the adapter is that you did not have to care which one — but you *can* read the three `_to_*_message` methods side by side if you want to see how the vendors differ.

**Next up:** Step 2 loads the source PDF into the same conversation. Brace yourself — the text extraction is going to be messy, and that is exactly the point.
'''


# ============================================================================
# CELL 12 — Step 2 explainer
# ============================================================================
CELL_12 = '''
---

# Step 2 of 5 — Context Priming: Show the Source

The AI knows *where we are going*. Let us show it *what we are starting from*.

## Staged context loading

Watch the token counter jump on the next cell — the PDF text is much larger than the goal image. This is normal, and it is exactly why we are priming in stages instead of sending one giant prompt.

Each time we do a "Continue" ack, we let the AI chunk what it has seen so far. Think of it like handing someone a stack of papers one at a time instead of dropping the whole stack on their desk. They get a chance to register each one.

### Bonus: prompt caching synergy

On Anthropic, OpenAI, and Gemini, staged loading plays nicely with prompt caching. When the same prefix appears in multiple calls, providers can serve cached tokens at 10–25% of the normal price. Our adapter does not enable caching explicitly (we kept it small for educational clarity), but this pattern is what production systems use to make multi-turn context loading affordable at scale.
'''

# ============================================================================
# CELL 13 — Extract and prime with source
# ============================================================================
CELL_13 = '''
# Step 2: extract text from the source PDF and prime the AI with it.
# pypdf extraction works identically on all three providers.

source_text = ai.pdf_as_text(SOURCE_DOC)

print(f"Extracted {len(source_text):,} characters from the PDF.")
print()
print("First 400 characters of the extraction:")
print("-" * 60)
print(source_text[:400])
print("-" * 60)
print()

# Append the source as a new user turn, using the same "Continue" pattern.
history.append({
    "role": "user",
    "content": (
        "Here is the raw source document we are starting from "
        f"(extracted text from {SOURCE_DOC}):\\n\\n"
        f"{source_text}\\n\\n"
        "Do not describe, analyze, or summarize it yet. "
        "Reply with only the single word: Continue"
    ),
})

source_ack = ai.ask(history)
history.append({"role": "assistant", "content": source_ack})

print(f"AI replied: {source_ack!r}")
print(f"Tokens this call: {ai.last_usage}")
'''

# ============================================================================
# CELL 14 — The "Parsed cleanly?" teaching moment
# ============================================================================
CELL_14 = '''
## The "Parsed cleanly?" diamond, live

Look at the first 400 characters printed above. The extraction ranges from clean to scrambled depending on your source — some layouts survive `pypdf` intact, others come back with columns misaligned, numbers in the wrong rows, or subtotals scattered across lines. That is the real-world behavior of flattening pivot-table PDFs into plain text.

**This is the first real-world edge case in the reference workflow.** Look back at the Mermaid diagram in `assets/reference_workflow.mmd` — the very first decision point in phase 1 is:

> *"Parsed cleanly?" → No → OCR / manual rescue*

Your source just hit that branch.

### What we are doing about it

For this lesson we are going to continue anyway, for two reasons:

1. **Modern LLMs are surprisingly good at making sense of mangled tables.** Claude, GPT, and Gemini can all recover structure from text that looks completely broken to you. We will watch this happen in Step 3.
2. **Hitting the edge case is educational.** When the AI designs its own workflow in Step 3, you will see it independently identify "the PDF parse is unreliable" as a real concern — because the messy extraction is sitting right there in its context.

In production you would route this to a human or to an OCR fallback. The notebook shows you the degraded path so you can see what the failure mode looks like.
'''

# ============================================================================
# CELL 15 — Cumulative token checkpoint
# ============================================================================
CELL_15 = '''
# Sanity check: how much have we spent on context priming so far?

print("Context priming checkpoint:")
print(f"  input tokens:       {ai.total_usage['input_tokens']:,}")
print(f"  output tokens:      {ai.total_usage['output_tokens']:,}")
print(f"  estimated cost:     ${ai.total_usage['estimated_cost_usd']:.4f}")
print(f"  conversation turns: {len(history) // 2}")
print()
print("Every subsequent cell will build on this primed context without re-sending")
print("the goal or the source. That is the savings context priming buys you.")
'''

# ============================================================================
# CELL 16 — Step 3 explainer
# ============================================================================
CELL_16 = '''
---

# Step 3 of 5 — Task Decomposition

The AI now has the goal (Step 1) and the source (Step 2) in its context. Time to ask it something non-trivial: **design a workflow that gets from the source to the goal.**

## What makes this different from "chain of thought"

You have probably seen the advice *"ask the AI to think step by step."* Task decomposition is a more disciplined version of that. Instead of *"explain your reasoning,"* we ask for a specific structured output: an ordered list of steps where each step carries a **machine-readable execution contract.**

Every step the AI returns must include:

- `step_id`
- `purpose`
- `inputs` / `outputs`
- `confidence` (a 0.00–1.00 self-estimate)
- `assumptions` and `blockers`
- `edge_cases`

Why this matters: it turns prose into something a second agent could actually execute. An LLM workflow that returns structured envelopes is **auditable, testable, and hand-off-able** between different agents or to a human reviewer. An LLM workflow that returns free-form prose is a chatbot.

This pattern comes from Anthropic's [prompt chaining guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-prompts): *"when a single prompt handles everything, the model can drop steps. Breaking complex tasks into focused subtasks ensures each link gets the model's full attention."*
'''

# ============================================================================
# CELL 17 — Ask for decomposition
# ============================================================================
CELL_17 = '''
# Step 3: ask the AI to decompose the goal-from-source transformation
# into a structured workflow that another agent could actually run.

from pathlib import Path

history.append({
    "role": "user",
    "content": (
        "Now design a workflow that transforms the source document into the goal dashboard. "
        "Structure your response as an ordered list of steps. Every step MUST include "
        "these fields:\\n\\n"
        "- step_id (e.g., 'step_1_intake')\\n"
        "- purpose (one sentence)\\n"
        "- inputs (what data the step reads)\\n"
        "- outputs (what the step produces)\\n"
        "- confidence (0.00 to 1.00 estimate of reliability for this kind of input)\\n"
        "- assumptions (what we are taking on faith)\\n"
        "- blockers (what would cause this step to fail)\\n"
        "- edge_cases (at least one per step)\\n\\n"
        "Include decision branches where an AI judgment call is genuinely required "
        "versus where deterministic code would suffice. Do not skip messy parts — "
        "call them out. Target 8 to 12 steps total. Respond in Markdown."
    ),
})

decomposition = ai.ask(history)
history.append({"role": "assistant", "content": decomposition})

# Save the decomposition so Steps 4 and 5 can reuse it.
Path("outputs").mkdir(exist_ok=True)
Path("outputs/decomposition.md").write_text(decomposition, encoding="utf-8")

print(f"Decomposition saved to outputs/decomposition.md")
print(f"Length: {len(decomposition):,} characters")
print(f"Tokens this call: {ai.last_usage}")
print()
print("First 1,500 characters of the decomposition:")
print("=" * 60)
print(decomposition[:1500])
print("=" * 60)
'''

# ============================================================================
# CELL 18 — Compare with reference decomposition (explainer)
# ============================================================================
CELL_18 = '''
## Compare with the reference decomposition

A hand-authored reference decomposition ships with this lesson at `assets/reference_decomposition.md`. Take a moment to scan your AI-generated version above and compare the shapes.

You will likely see:

- **Similar phase structure.** Both versions should move through intake → classification → computation → delivery in roughly that order. Same problem, similar solutions.
- **Overlapping edge cases.** PDF parse reliability, fiscal-year detection, owner compensation ambiguity, capex-vs-opex confusion — these are in both because they are in the *data*.
- **Different opinions on some fields.** Your AI may have picked different confidence thresholds, or different names for the same bucket, or flagged different steps as "needs human review."

Your version does not need to match exactly. The point is that both are valid decompositions of the same problem, and the AI got there from **context priming alone** — no explicit examples of what a good decomposition looks like. That is the power of goal-first priming.

Run the next cell to display the reference below your own output.
'''

# ============================================================================
# CELL 19 — Load and display reference decomposition
# ============================================================================
CELL_19 = '''
# Display the reference decomposition for comparison.

reference_path = Path("assets/reference_decomposition.md")
if reference_path.exists():
    reference = reference_path.read_text(encoding="utf-8")
    print(f"Reference decomposition: {len(reference):,} characters")
    print()
    print("First 1,500 characters of the reference:")
    print("=" * 60)
    print(reference[:1500])
    print("=" * 60)
else:
    print(f"Reference not found at {reference_path}.")
    print("If you swapped in your own source document in Cell 7, there is no reference")
    print("for that specific problem — your AI-generated decomposition is the artifact.")
'''

# ============================================================================
# CELL 20 — Step 4 explainer
# ============================================================================
CELL_20 = '''
---

# Step 4 of 5 — Visual Workflow Design with Mermaid

Text decomposition is great for machines. **Visual decomposition is great for humans.** We are going to ask the AI to render the workflow it just designed as a Mermaid flowchart.

## Why Mermaid specifically

Mermaid is a diagram-as-code syntax that renders natively in GitHub, VS Code, Jupyter, and most modern Markdown viewers. Unlike generic "draw a diagram" prompts, asking for Mermaid has three hard benefits:

1. **Constrained format = reliable output.** The AI cannot hand-wave: either the output parses as Mermaid or it does not. This is structured-output enforcement without a JSON schema.
2. **Token-efficient.** A Mermaid flowchart with 20 nodes is a few hundred tokens. The same diagram described in prose takes thousands. Analysis suggests Mermaid cuts diagram tokens by 80%+ versus alternatives.
3. **Human- and machine-readable.** You can eyeball a Mermaid diagram *and* diff it in Git. Few diagram formats offer both.

## The determinism gradient

Pay attention to the **diamonds** (decision nodes) in the flowchart the AI produces. Diamonds are where the workflow genuinely needs AI judgment. **Rectangles** are where deterministic code can take over. This distinction becomes critical in Step 5 — we will ask the AI to write code for the rectangles and call itself only at the diamonds.
'''

# ============================================================================
# CELL 21 — Ask for mermaid
# ============================================================================
CELL_21 = '''
# Step 4: ask for the decomposition as a Mermaid flowchart.

history.append({
    "role": "user",
    "content": (
        "Render the workflow above as a Mermaid flowchart.\\n\\n"
        "Requirements:\\n"
        "- Use `flowchart TD` (top-down).\\n"
        "- Group related steps into `subgraph` blocks for each major phase.\\n"
        "- Use decision diamonds for confidence gates and critical-input checks.\\n"
        "- Use a dark theme: start the diagram with "
        "`%%{init: {\\"theme\\": \\"dark\\"}}%%`.\\n"
        "- Apply `classDef` styling to distinguish: inputs, process steps, "
        "decisions, and review/fallback nodes.\\n"
        "- Output ONLY the Mermaid code block, nothing else. No prose before or after.\\n"
        "- Wrap the Mermaid in triple-backtick fences with the `mermaid` language tag."
    ),
})

mermaid_response = ai.ask(history)
history.append({"role": "assistant", "content": mermaid_response})

# Extract the mermaid code from the fenced block (strip the fences).
mermaid_code = mermaid_response.strip()
if mermaid_code.startswith("```mermaid"):
    mermaid_code = mermaid_code.split("```mermaid", 1)[1]
if mermaid_code.endswith("```"):
    mermaid_code = mermaid_code.rsplit("```", 1)[0]
mermaid_code = mermaid_code.strip()

Path("outputs/workflow.mmd").write_text(mermaid_code, encoding="utf-8")
print(f"Mermaid saved to outputs/workflow.mmd ({len(mermaid_code):,} characters)")
print(f"Tokens this call: {ai.last_usage}")
'''

# ============================================================================
# CELL 22 — Render the generated mermaid inline
# ============================================================================
CELL_22 = '''
# Render the AI-generated Mermaid flowchart inline.
# VS Code and modern Jupyter render Mermaid in Markdown cells natively.

from IPython.display import Markdown, display

print("Your AI-generated workflow:")
display(Markdown(f"```mermaid\\n{mermaid_code}\\n```"))
'''

# ============================================================================
# CELL 23 — Display reference mermaid for comparison
# ============================================================================
CELL_23 = '''
# Display the reference Mermaid shipped with the lesson for side-by-side comparison.

reference_mmd_path = Path("assets/reference_workflow.mmd")
if reference_mmd_path.exists():
    reference_mmd = reference_mmd_path.read_text(encoding="utf-8")
    print("Reference workflow (hand-authored, shipped with the lesson):")
    display(Markdown(f"```mermaid\\n{reference_mmd}\\n```"))
else:
    print("No reference mermaid found.")
'''

# ============================================================================
# CELL 24 — Step 5 explainer
# ============================================================================
CELL_24 = '''
---

# Step 5 of 5 — Workflow Crystallization

Here is the meta-move. We have spent thousands of tokens designing this workflow with the AI. **If we ran this analysis once a week for a year, that is hundreds of thousands of tokens spent re-deriving the same thing.**

Instead, we are going to ask the AI — once — to give us code that does the deterministic parts of the workflow for us. Next run, those parts are free.

## What we are doing and what we are not

**We are:** asking the AI to write Python code that implements the rectangles from your Mermaid diagram — the steps that are deterministic. Parse the PDF, normalize the ledger, compute ratios, assemble a draft dashboard.

**We are not:** asking it to fully replace itself. The diamonds in the diagram — confidence checks, classification edge cases, plain-English summaries — still need AI judgment. The generated code will call out to an `ai.ask(...)` stub at exactly those places, and every one of them will be marked with a comment explaining *why* deterministic code would not work there.

## Why this technique matters most

This is the meta-technique that makes production AI workflows affordable. Andrej Karpathy [described it](https://www.mindstudio.ai/blog/karpathy-llm-knowledge-base-architecture-compiler-analogy) as treating the LLM like a compiler: you do the expensive reasoning once, and emit cheap, deterministic artifacts that handle the repetitive parts. Real production systems do this all the time — but it is rarely taught as a named technique.

We are going to call it **workflow crystallization**: using an expensive general-purpose model once to produce cheap specialized code that handles everything up to the next decision that genuinely needs judgment.
'''

# ============================================================================
# CELL 25 — Ask for crystallized code
# ============================================================================
CELL_25 = '''
# Step 5: ask for executable Python code that implements the workflow.

history.append({
    "role": "user",
    "content": (
        "Write a single Python file that implements as much of this workflow "
        "as possible in deterministic code.\\n\\n"
        "Requirements:\\n\\n"
        "- Define one top-level function: "
        "`run_workflow(source_path: str, target_dashboard_path: str, ai=None) -> dict`. "
        "It takes a source document path and returns the final dashboard payload dict.\\n"
        "- For any step where AI judgment is genuinely needed (confidence scoring, "
        "ambiguous classification, plain-English narrative generation), call "
        "`ai.ask(...)`. For everything else, write real Python.\\n"
        "- Mark every AI call site with a `# AI_JUDGMENT_CALL: <why>` comment "
        "explaining why deterministic code would not work at that point.\\n"
        "- Include at minimum: PDF parsing, ledger normalization, account "
        "classification, ratio computation, action-item generation, dashboard assembly.\\n"
        "- Use only the standard library, `pypdf`, and the `ai` argument for LLM calls. "
        "Do NOT import the three SDKs directly.\\n"
        "- Add docstrings on the top-level function and any non-trivial helper.\\n"
        "- Output ONLY the Python code inside a single ```python fenced block. "
        "No prose before or after."
    ),
})

crystallized = ai.ask(history)
history.append({"role": "assistant", "content": crystallized})

# Extract the code from the fenced block.
code_text = crystallized.strip()
if code_text.startswith("```python"):
    code_text = code_text.split("```python", 1)[1]
if code_text.endswith("```"):
    code_text = code_text.rsplit("```", 1)[0]
code_text = code_text.strip()

Path("outputs/workflow.py").write_text(code_text, encoding="utf-8")
print(f"Crystallized workflow saved to outputs/workflow.py ({len(code_text):,} characters)")
print(f"Tokens this call: {ai.last_usage}")
'''

# ============================================================================
# CELL 26 — Display crystallized code
# ============================================================================
CELL_26 = '''
# Display the generated code with syntax highlighting.

from IPython.display import Code
Code(filename="outputs/workflow.py", language="python")
'''

# ============================================================================
# CELL 27 — Token-cost comparison
# ============================================================================
CELL_27 = '''
# The payoff: what did we just save?

total_in = ai.total_usage["input_tokens"]
total_out = ai.total_usage["output_tokens"]
total_cost = ai.total_usage["estimated_cost_usd"]

# Count how many AI_JUDGMENT_CALL markers the generated code has.
# These are the ONLY places a future run will need to call the AI.
ai_calls_in_code = code_text.count("AI_JUDGMENT_CALL")

print("LESSON TOKEN BUDGET (Steps 1 through 5 of this notebook):")
print(f"  total input tokens:   {total_in:,}")
print(f"  total output tokens:  {total_out:,}")
print(f"  one-time cost:        ${total_cost:.4f}")
print()
print(f"Your crystallized workflow.py contains {ai_calls_in_code} AI_JUDGMENT_CALL sites.")
print("Those are the only places a future run of run_workflow() will need to call the AI.")
print()
print("Priming + decomposition + mermaid + crystallization = one-time design cost.")
print("Future runs skip all four and pay only for the judgment-call sites.")
print()
print("That is workflow crystallization: pay once at design time, save forever at runtime.")
'''

# ============================================================================
# CELL 28 — What you built + next steps
# ============================================================================
CELL_28 = '''
---

# What you built

In one notebook, you just:

1. **Primed an AI** with a goal image and a messy source PDF using two staged "Continue" priming calls (Steps 1 and 2)
2. **Decomposed the goal-from-source transformation** into a structured, machine-readable workflow contract (Step 3)
3. **Rendered that workflow visually** as a Mermaid flowchart you can share, diff, and review (Step 4)
4. **Crystallized the workflow** into executable Python code that handles the deterministic steps and calls the AI only where real judgment is needed (Step 5)

The artifacts are sitting in `outputs/`:

- `outputs/decomposition.md` — the structured workflow contract
- `outputs/workflow.mmd` — the visual flowchart
- `outputs/workflow.py` — the executable crystallized code

## Your next move

**Swap the inputs.** Replace `assets/target_dashboard.png` and `assets/source_financial_pack.pdf` with your own files in Cell 7 and re-run. The whole notebook works for any goal-image + source-document pair. Try:

- A Slack thread screenshot + a meeting transcript → an action-item extractor
- A finished report PDF + raw interview notes → a report-drafting workflow
- A filled-out form screenshot + a source database dump → a form-filling agent

**Try a different provider.** If you have keys for Anthropic, OpenAI, and Google, re-run the notebook with each. You will see different decompositions, different mermaid styles, and different crystallization strategies. Comparing them across providers is a whole meta-lesson by itself.

**Run the crystallized code.** Import `outputs/workflow.py` and call `run_workflow(source_path, target_dashboard_path, ai=ai)` to actually execute the generated workflow. Bugs are expected on the first run — they are teaching moments for how your chosen AI reasoned about the problem.

## What we deliberately did not teach

This notebook is a primer. Some things are out of scope on purpose:

- **Prompt caching.** Production workflows should use `cache_control` blocks on Anthropic and automatic caching on OpenAI/Gemini to get 75–90% discounts on repeated context.
- **Streaming.** We used blocking calls for simplicity. Real UIs stream tokens as they arrive.
- **Multi-agent orchestration.** Our workflow was sequential. Production systems often fan out to parallel agents at non-conflicting steps.
- **Evaluation.** We did not score the decomposition against a ground truth. Production LLM workflows need evals.

Pointers to all four are in the citations cell below.
'''

# ============================================================================
# CELL 29 — Citations and further reading
# ============================================================================
CELL_29 = '''
## Citations and further reading

> **Attribution.** The integration and pedagogical sequencing below — goal-first context priming → source priming → structured decomposition → mermaid visualization → code crystallization — is **CompleteTech LLC's original methodology**. The citations below are for the individual techniques this method draws on, so you can follow the breadcrumbs.

### Context priming / staged context loading
- [Anthropic — Prompting best practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [LLM Priming — Promptmetheus knowledge base](https://promptmetheus.com/resources/llm-knowledge-base/llm-priming)
- [Exploring LLM Priming Strategies for Few-Shot Stance Detection — ACL 2025](https://aclanthology.org/2025.argmining-1.2.pdf)

### Task decomposition / prompt chaining
- [Anthropic — Chain complex prompts for stronger performance](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-prompts)
- [Anthropic Interactive Prompt Engineering Tutorial (GitHub)](https://github.com/anthropics/prompt-eng-interactive-tutorial)
- [Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in LLMs" (NeurIPS 2022)](https://arxiv.org/abs/2201.11903)

### Goal-first / reverse prompting
- [Reverse Prompt Engineering — Learn Prompting](https://learnprompting.org/docs/language-model-inversion/reverse-prompt-engineering)
- [Lilian Weng — Prompt Engineering survey](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/)

### Structured output / Mermaid
- [MermaidSeqBench: LLM-to-Mermaid generation benchmark](https://arxiv.org/html/2511.14967v1)
- [Diagramming Tools for the LLM Age / Token Efficiency](https://dev.to/akari_iku/analyzing-the-best-diagramming-tools-for-the-llm-age-based-on-token-efficiency-5891)

### Confidence and calibration (Step 3's 0.80 threshold)
- [Xiong et al., "Can LLMs Express Their Uncertainty?" (ICLR 2024)](https://arxiv.org/pdf/2306.13063)
- [On Verbalized Confidence Scores for LLMs (arXiv 2024)](https://arxiv.org/pdf/2412.14737)

### Workflow crystallization / LLM-as-compiler
- [Karpathy's LLM knowledge-base compiler analogy](https://www.mindstudio.ai/blog/karpathy-llm-knowledge-base-architecture-compiler-analogy)
- [My LLM Code Generation Workflow — DEV Community](https://dev.to/simbo1905/my-llm-code-generation-workflow-for-now-1ahj)

### What we left out (pointers for later)
- [Prompt caching — Anthropic](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- Streaming: see each provider's streaming docs.
- Multi-agent orchestration: LangGraph, Anthropic's Claude Code SDK, OpenAI Assistants.
- LLM evaluation: Anthropic's eval cookbook, OpenAI Evals, Inspect.

---

<div align="center">

<img src="assets/completetech_logo.jpg" alt="CompleteTech LLC" width="180"/>

**© 2026 CompleteTech LLC.** Method and teaching material © CompleteTech LLC. Source code MIT licensed.

The individual prompt engineering techniques (context priming, task decomposition, reverse prompting, structured output, workflow crystallization) are drawn from the research and vendor documentation cited above. The **integration and pedagogical sequencing** — goal-first priming → source priming → structured decomposition → mermaid visualization → code crystallization — is CompleteTech's original methodology.

</div>
'''


cells = [
    md(CELL_1),
    md(CELL_2),
    code(CELL_3),
    md(CELL_4),
    code(CELL_5, hidden=True),
    code(CELL_6),
    code(CELL_7),
    md(CELL_8),
    code(CELL_9),
    code(CELL_10),
    md(CELL_11),
    md(CELL_12),
    code(CELL_13),
    md(CELL_14),
    code(CELL_15),
    md(CELL_16),
    code(CELL_17),
    md(CELL_18),
    code(CELL_19),
    md(CELL_20),
    code(CELL_21),
    code(CELL_22),
    code(CELL_23),
    md(CELL_24),
    code(CELL_25),
    code(CELL_26),
    code(CELL_27),
    md(CELL_28),
    md(CELL_29),
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.10",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUTPUT.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
print(f"Wrote {OUTPUT.name} ({OUTPUT.stat().st_size:,} bytes, {len(cells)} cells)")
