"""
Question Answering Prompt Templates
"""

from langchain.prompts import PromptTemplate


QA_PROMPT_TEMPLATE = """You are an expert consultant assistant helping users find information from a document knowledge base. Your role is to provide accurate, comprehensive answers based strictly on the provided context.

Context from documents:
{context}

Question: {question}

Instructions:
1. Answer based ONLY on the information in the provided context
2. Be specific and cite which source contains the information when relevant
3. If the context doesn't contain enough information to fully answer the question, clearly state what is missing
4. Provide a well-structured, professional response
5. If multiple sources provide different information, acknowledge and explain the differences
6. Use bullet points or numbered lists when appropriate for clarity

Answer:"""

QA_PROMPT = PromptTemplate(
    template=QA_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)


QA_WITH_HISTORY_TEMPLATE = """You are an expert consultant assistant with access to a document knowledge base and conversation history. Provide accurate, contextual answers.

Previous Conversation:
{chat_history}

Context from documents:
{context}

Current Question: {question}

Instructions:
1. Consider the conversation history for context
2. Answer based primarily on the provided document context
3. Reference previous conversation points when relevant
4. Maintain consistency with earlier responses
5. Be specific and professional
6. Cite sources when providing information

Answer:"""

QA_WITH_HISTORY_PROMPT = PromptTemplate(
    template=QA_WITH_HISTORY_TEMPLATE,
    input_variables=["context", "question", "chat_history"]
)


FOLLOWUP_PROMPT_TEMPLATE = """Based on this question-answer interaction, suggest 3 relevant follow-up questions:

Question: {question}
Answer: {answer}

Generate 3 natural follow-up questions that would help the user explore this topic further. Make them specific and directly related to the content discussed.

Format: Return only the questions, one per line."""

FOLLOWUP_PROMPT = PromptTemplate(
    template=FOLLOWUP_PROMPT_TEMPLATE,
    input_variables=["question", "answer"]
)