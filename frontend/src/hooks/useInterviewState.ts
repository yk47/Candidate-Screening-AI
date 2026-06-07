/* Interview state hook. */

import { useState, useCallback } from 'react';

export interface Question {
  id: string;
  text: string;
  topic: string;
  difficulty: string;
}

export interface Answer {
  questionId: string;
  text: string;
  score: number;
  feedback: string;
}

interface UseInterviewState {
  sessionId: string | null;
  currentQuestion: Question | null;
  currentAnswer: string;
  questions: Question[];
  answers: Answer[];
  isLoading: boolean;
  error: string | null;
}

export function useInterviewState() {
  const [state, setState] = useState<UseInterviewState>({
    sessionId: null,
    currentQuestion: null,
    currentAnswer: '',
    questions: [],
    answers: [],
    isLoading: false,
    error: null,
  });

  const startSession = useCallback((sessionId: string) => {
    setState((prev) => ({ ...prev, sessionId }));
  }, []);

  const setCurrentQuestion = useCallback((question: Question) => {
    setState((prev) => ({
      ...prev,
      currentQuestion: question,
      questions: [...prev.questions, question],
    }));
  }, []);

  const setCurrentAnswer = useCallback((answer: string) => {
    setState((prev) => ({ ...prev, currentAnswer: answer }));
  }, []);

  const submitAnswer = useCallback((answerData: Answer) => {
    setState((prev) => ({
      ...prev,
      answers: [...prev.answers, answerData],
      currentAnswer: '',
    }));
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, isLoading: loading }));
  }, []);

  const setError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, error }));
  }, []);

  return {
    ...state,
    startSession,
    setCurrentQuestion,
    setCurrentAnswer,
    submitAnswer,
    setLoading,
    setError,
  };
}
