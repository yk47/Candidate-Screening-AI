/* Interview API service. */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" &&
   window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "https://candidate-screening-ai-1.onrender.com");

console.debug('Interview service API_BASE_URL:', API_BASE_URL);

interface StartInterviewRequest {
  candidate_name: string;
  email?: string;
  role: string;
  resume_text?: string;
  resume_file?: File | null;
}

interface AnswerSubmissionRequest {
  session_id: string;
  question_id: string;
  answer: string;
}

export const interviewService = {
  async startInterview(data: StartInterviewRequest) {
    try {
      let response: Response;

      // If a file is provided, send as FormData so backend can receive the file
      if (data.resume_file) {
        const form = new FormData();
        form.append('candidate_name', data.candidate_name);
        if (data.email) form.append('email', data.email);
        form.append('role', data.role);
        if (data.resume_text) form.append('resume_text', data.resume_text);
        form.append('resume_file', data.resume_file);

        response = await fetch(`${API_BASE_URL}/api/interview/start`, {
          method: 'POST',
          body: form,
        });
      } else {
        response = await fetch(`${API_BASE_URL}/api/interview/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
      }

      if (!response.ok) {
        const text = await response.text().catch(() => null);
        throw new Error(`Failed to start interview: ${response.status} ${response.statusText} ${text || ''}`);
      }

      return response.json();
    } catch (err) {
      // Network error (e.g., backend not running or CORS) will surface here
      throw new Error('Failed to fetch from backend: ' + (err as Error).message);
    }
  },

  async getNextQuestion(sessionId: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/interview/next-question?session_id=${sessionId}`,
      { method: 'POST' }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get question');
    }

    return response.json();
  },

  async submitAnswer(data: AnswerSubmissionRequest) {
    const response = await fetch(`${API_BASE_URL}/api/interview/submit-answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to submit answer');
    }

    return response.json();
  },

  async getSessionDetails(sessionId: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/interview/session/${sessionId}`
    );

    if (!response.ok) {
      throw new Error('Failed to get session details');
    }

    return response.json();
  },

  async getSessionSummary(sessionId: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/interview/summary/${sessionId}`
    );

    if (!response.ok) {
      throw new Error('Failed to get session summary');
    }

    return response.json();
  },
};
