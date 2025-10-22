"""
Document Summarization Prompt Templates
"""

from langchain.prompts import PromptTemplate


BRIEF_SUMMARY_TEMPLATE = """Provide a concise summary of the following text. Focus on the main points and key takeaways.

Text:
{text}

Brief Summary (3-5 sentences):"""

BRIEF_SUMMARY_PROMPT = PromptTemplate(
    template=BRIEF_SUMMARY_TEMPLATE,
    input_variables=["text"]
)


COMPREHENSIVE_SUMMARY_TEMPLATE = """As an expert analyst, create a comprehensive summary of the following documents. Your summary should be detailed, well-organized, and professional.

Documents:
{text}

Provide your analysis in the following structure:

Summary:
[Provide a detailed 3-4 paragraph overview covering all major themes and findings]

Key Points:
[List 5-7 most important points from the documents]

Insights:
[Identify 2-3 key insights, patterns, or implications]

Make your summary thorough, accurate, and actionable."""

COMPREHENSIVE_SUMMARY_PROMPT = PromptTemplate(
    template=COMPREHENSIVE_SUMMARY_TEMPLATE,
    input_variables=["text"]
)


EXECUTIVE_SUMMARY_TEMPLATE = """Create an executive summary for senior stakeholders. Focus on high-level insights, strategic implications, and actionable recommendations.

Documents:
{text}

Executive Summary:

**Overview** (2-3 sentences)
[High-level summary of the content]

**Key Findings** (3-5 bullet points)
[Most critical findings or data points]

**Strategic Implications** (2-3 bullet points)
[What this means for the organization]

**Recommendations** (2-3 bullet points)
[Actionable next steps]

Keep it concise, strategic, and focused on business value."""

EXECUTIVE_SUMMARY_PROMPT = PromptTemplate(
    template=EXECUTIVE_SUMMARY_TEMPLATE,
    input_variables=["text"]
)


# Map-Reduce Prompts for large document sets
MAP_REDUCE_MAP_TEMPLATE = """Summarize the following document section, extracting key points and important information:

{text}

Concise Summary:"""

MAP_REDUCE_MAP_PROMPT = PromptTemplate(
    template=MAP_REDUCE_MAP_TEMPLATE,
    input_variables=["text"]
)


MAP_REDUCE_COMBINE_TEMPLATE = """You are given summaries of different sections from a document collection. Create a cohesive, comprehensive summary that synthesizes all the information.

Section Summaries:
{text}

Create a final comprehensive summary that includes:

Summary:
[Integrated overview of all sections]

Key Points:
[5-7 most important points across all sections]

Insights:
[Key insights and patterns identified]

Your summary should be well-organized, coherent, and capture the essence of all sections."""

MAP_REDUCE_COMBINE_PROMPT = PromptTemplate(
    template=MAP_REDUCE_COMBINE_TEMPLATE,
    input_variables=["text"]
)