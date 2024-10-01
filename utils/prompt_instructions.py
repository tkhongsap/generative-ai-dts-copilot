def get_summary_system_prompt():
    return "You are an AI assistant that analyzes meeting transcripts. Provide a concise summary with sections for key insights, action items, timeline, and stakeholder information. Always respond in the same language as the input transcript."

def get_summary_user_prompt(transcript):
    return f"""Please analyze the following meeting transcript and provide a summary with the following sections:

    ### Summary
    (3-5 sentences overview of the meeting)

    ### Key Insights
    (4-6 main takeaways or important points discussed)

    ### Action Items
    (List of tasks or actions to be taken, with responsible parties if mentioned)

    ### Timeline
    (Any mentioned deadlines or important dates)

    ### Stakeholders
    (Key people or teams mentioned, with their roles or responsibilities if available)

    Use markdown formatting for the section titles.

    Transcript: {transcript}

    IMPORTANT: Respond in the same language as the transcript."""

def get_detailed_report_system_prompt():
    return "You are an AI assistant that provides detailed reports on meeting transcripts. Offer a comprehensive analysis with additional context. Always respond in the same language as the input transcript."

def get_detailed_report_user_prompt(transcript):
    return f"""Please provide a detailed report on the following meeting transcript. Include:

    1. Comprehensive overview of the meeting
    2. In-depth analysis of key topics discussed
    3. Detailed breakdown of action items, with context and implications
    4. Thorough timeline of events and deadlines mentioned
    5. Extensive stakeholder analysis, including roles, responsibilities, and potential impacts

    Provide additional context and insights from the transcript where relevant.

    Transcript: {transcript}

    IMPORTANT: Respond in the same language as the transcript."""

def get_business_requirement_system_prompt():
    return """You are an expert business analyst. Your task is to translate the given input into a well-structured business requirement document for the technology team. Always respond in the same language as the input."""

def get_business_requirement_user_prompt(input_text):
    return f"""Please translate the following input into a business requirement document:

{input_text}

Your response should include:
1. A clear and concise summary of the business need
2. Specific, measurable, achievable, relevant, and time-bound (SMART) objectives
3. Key stakeholders and their roles
4. Functional requirements
5. Non-functional requirements (e.g., performance, security, scalability)
6. Any constraints or assumptions
7. Success criteria

Please format your response using Markdown for better readability.

IMPORTANT: Respond in the same language as the input text."""
