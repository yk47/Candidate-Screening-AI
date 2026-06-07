"""LLM prompt templates for interview workflow."""

TOPIC_GENERATION_PROMPT = """You are an expert interviewer preparing for a structured technical interview.

Based on the candidate's resume and the target role, generate 5 relevant interview topics that would effectively evaluate the candidate.

**Candidate Background:**
Skills: {skills}
Technologies: {technologies}
Experience Years: {experience_years}
Domain Exposure: {domain_exposure}

**Target Role:** {role}

**Instructions:**
1. Generate topics that align with the role requirements
2. Consider the candidate's experience level
3. Mix conceptual and practical topics
4. Ensure topics are progressive in difficulty

Return the topics as a JSON list: ["topic1", "topic2", "topic3", "topic4", "topic5"]
"""

QUESTION_GENERATION_PROMPT = """You are an expert interviewer creating interview questions.

Generate a highly relevant technical interview question based on the following context:

**Topic:** {topic}
**Role:** {role}
**Difficulty:** {difficulty}
**Candidate Skills:** {skills}
**Candidate Experience:** {experience_years} years

**Retrieved Knowledge Base Context:**
{retrieved_context}

**Instructions:**
1. The question should be based on the retrieved context and specific to the role
2. Consider the candidate's background when framing the question
3. Avoid generic questions - make it specific and meaningful
4. The question should test both conceptual and practical understanding
5. Format as a clear, well-structured question

Return a JSON object with:
{{
    "question": "your question here",
    "context_used": "brief explanation of which context was used",
    "expected_depth": "what depth of answer is expected"
}}
"""

ANSWER_EVALUATION_PROMPT = """You are an expert evaluator assessing technical interview answers.

Evaluate the candidate's answer to the interview question.

**Question:** {question}
**Candidate Answer:** {answer}
**Topic:** {topic}
**Role:** {role}

**Knowledge Base Context (Reference):**
{reference_context}

**Evaluation Criteria:**
1. Accuracy: Does the answer align with the knowledge base and best practices?
2. Depth: Does it show sufficient understanding of the topic?
3. Relevance: Is it directly addressing the question?
4. Clarity: Is the answer well-structured and understandable?

Provide evaluation in this JSON format:
{{
    "score": 0.0-1.0,
    "accuracy": "assessment",
    "depth": "assessment",
    "relevance": "assessment",
    "clarity": "assessment",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "feedback": "constructive feedback for improvement",
    "follow_up_suggestion": "optional follow-up question"
}}
"""

RESUME_PARSING_PROMPT = """You are an expert resume parser specializing in technical profiles.

Extract key information from the candidate's resume.

**Resume:**
{resume_text}

Extract and return a JSON object with:
{{
    "skills": ["skill1", "skill2", ...],
    "technologies": ["tech1", "tech2", ...],
    "experience_years": integer,
    "domain_exposure": ["domain1", "domain2", ...],
    "education": "education details",
    "certifications": ["cert1", "cert2"],
    "key_projects": ["project1", "project2"]
}}

Focus on:
- Technical skills and programming languages
- Frameworks and tools
- Domain experience (web, mobile, ML, cloud, etc.)
- Years of professional experience
"""

SESSION_SUMMARY_PROMPT = """You are an expert technical interviewer creating interview summaries.

Generate a comprehensive summary of the interview session.

**Session Details:**
- Role: {role}
- Questions Asked: {questions_count}
- Average Score: {average_score}

**Questions and Answers:**
{qa_pairs}

Create a JSON summary:
{{
    "overall_assessment": "summary of candidate's performance",
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "recommendations": "hiring recommendation and explanation",
    "key_observations": ["observation1", "observation2", ...],
    "suggested_follow_ups": ["follow_up1", "follow_up2"]
}}
"""
