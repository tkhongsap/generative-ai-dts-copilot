def get_summary_system_prompt():
    return "You are an AI assistant that analyzes meeting transcripts. Provide a concise summary with sections for key insights, action items, timeline, and stakeholder information. Use the same language as the transcript."

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

    Respond in the same language as the transcript."""

def get_detailed_report_system_prompt():
    return "You are an AI assistant that provides detailed reports on meeting transcripts. Offer a comprehensive analysis with additional context."

def get_detailed_report_user_prompt(transcript):
    return f"""Please provide a detailed report on the following meeting transcript. Include:

    1. Comprehensive overview of the meeting
    2. In-depth analysis of key topics discussed
    3. Detailed breakdown of action items, with context and implications
    4. Thorough timeline of events and deadlines mentioned
    5. Extensive stakeholder analysis, including roles, responsibilities, and potential impacts

    Provide additional context and insights from the transcript where relevant.

    Transcript: {transcript}

    Respond in the same language as the transcript."""
