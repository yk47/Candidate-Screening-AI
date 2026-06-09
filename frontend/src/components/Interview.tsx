import React, { useState, useEffect } from 'react';
import { interviewService } from '@/services/interviewService';
import ChatWindow, { Message } from './ChatWindow';
import ChatInput from './ChatInput';
import FinalReport from './FinalReport';
import { ErrorBar } from './UI';

interface InterviewProps {
  sessionId: string;
  candidateInfo: any;
  onComplete: (finalReport?: any) => void;
}

type Stage = 'greeting' | 'waiting_ready' | 'asking_questions' | 'summary';

function initials(name: string) {
  return (name || 'C')
    .split(' ')
    .map((w: string) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}

/* ── Interview header ── */
function InterviewHeader({
  candidateInfo,
  stage,
}: {
  candidateInfo: any;
  stage: Stage;
}) {
  const name = candidateInfo?.candidateName || 'Candidate';
  const role = candidateInfo?.role || 'Interview';
  const isLive = stage === 'asking_questions';

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '24px 0 20px',
      borderBottom: '1px solid var(--border)',
      marginBottom: 20,
    }}>
      {/* Candidate info */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <div style={{
          width: 44, height: 44,
          borderRadius: '50%',
          background: 'var(--gold-dim)',
          border: '1.5px solid var(--border-gold)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'var(--font-display)',
          fontSize: 16, fontWeight: 700,
          color: 'var(--gold)',
        }}>
          {initials(name)}
        </div>
        <div>
          <div style={{ fontSize: 15, fontWeight: 500, color: 'var(--text)' }}>{name}</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{role}</div>
        </div>
      </div>

      {/* Status badge */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        padding: '7px 14px',
        background: 'var(--surface2)',
        border: '1px solid var(--border)',
        borderRadius: 40,
        fontFamily: 'var(--font-mono)',
        fontSize: 12,
        color: 'var(--text-muted)',
      }}>
        {isLive && (
          <div style={{
            width: 6, height: 6,
            borderRadius: '50%',
            background: 'var(--gold)',
            animation: 'pulse 2s infinite',
          }} />
        )}
        {isLive
          ? 'Interview in progress'
          : stage === 'greeting' || stage === 'waiting_ready'
            ? 'Starting…'
            : 'Wrapping up…'
        }
      </div>
    </div>
  );
}

export default function Interview({ sessionId, candidateInfo, onComplete }: InterviewProps) {
  const [stage, setStage]             = useState<Stage>('greeting');
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState('');
  const [currentQuestionId, setCurrentQuestionId] = useState('');
  const [questionNumber, setQuestionNumber]       = useState(0);
  const [answers, setAnswers]         = useState<any[]>([]);
  const [finalReport, setFinalReport] = useState<any>(null);

  const [messages, setMessages] = useState<Message[]>([]);

  /* ── Greeting on mount ── */
  useEffect(() => {
    const name = (candidateInfo?.candidateName || 'Candidate').split(' ')[0];
    const role = candidateInfo?.role || 'the selected position';

    setMessages([{
      id:     'greeting',
      sender: 'ai',
      text:   `Hello, ${name}! 👋\n\nWelcome to your AI-powered interview for the ${role} position. I'll ask you a series of questions to assess your skills and experience.\n\nType "Ready" whenever you'd like to begin.`,
      meta:   'Greeting',
    }]);
    setStage('waiting_ready');
  }, []);

  /* ── Notify parent when interview completes ── */
  useEffect(() => {
    // Deliberately NOT calling onComplete here — it's called after
    // the 5-second delay in loadSummary / completion paths so the
    // candidate can read the "Thank you" message before being redirected.
  }, [stage, finalReport, onComplete]);

  const addMsg = (msg: Omit<Message, 'id'>) =>
    setMessages(m => [...m, { ...msg, id: `${msg.sender}-${Date.now()}` }]);

  /* ── Load a question ── */
  const loadQuestion = async (expectedNum?: number) => {
    setLoading(true);
    setError('');
    try {
      const q = await interviewService.getNextQuestion(sessionId);
      setCurrentQuestionId(q.question_id);
      setQuestionNumber(q.question_number ?? (expectedNum || questionNumber + 1));
      setStage('asking_questions');
      addMsg({
        sender: 'ai',
        text:   q.question_text,
      });
    } catch (err) {
      const msg = (err as Error).message;
      if (msg.includes('completed') || msg.includes('not found')) {
        await loadSummary();
      } else {
        setError('Error loading question: ' + msg);
      }
    } finally {
      setLoading(false);
    }
  };

  /* ── Finish ── */
  const loadSummary = async () => {
    setStage('summary');
    // Show the end-of-interview message
    addMsg({
      sender: 'ai',
      text:   'Thank you for your time. This interview has now ended.',
      meta:   'Session closed',
    });
    // Wait 5 seconds so the candidate can read the thank-you message,
    // then fetch the evaluation report and navigate to results
    setTimeout(async () => {
      try {
        const summary = await interviewService.getSessionSummary(sessionId);
        if (summary) {
          onComplete(summary);
        } else {
          onComplete();
        }
      } catch (e) {
        onComplete();
      }
    }, 5000);
  };

  /* ── Handle user message ── */
  const handleSend = async (message: string) => {
    addMsg({ sender: 'user', text: message });

    /* Waiting for "ready" */
    if (stage === 'waiting_ready') {
      const ready = ['yes', 'ok', 'okay', 'ready', "let's go", 'start', 'begin', 'sure', 'yep', 'go'];
      if (ready.some(k => message.toLowerCase().includes(k))) {
        await loadQuestion(1);
      } else {
        addMsg({
          sender: 'ai',
          text:   'Whenever you\'re ready, just type "Ready" or "Yes" to start the first question.',
          meta:   'Waiting',
        });
      }
      return;
    }

    /* Answering a question */
    if (stage === 'asking_questions') {
      setLoading(true);
      setError('');
      try {
        const evaluation = await interviewService.submitAnswer({
          session_id:  sessionId,
          question_id: currentQuestionId,
          answer:      message,
        });

        setAnswers(a => [...a, {
          questionNumber,
          answer:   message,
          score:    evaluation.score,
          feedback: evaluation.feedback,
        }]);

        addMsg({
          sender: 'ai',
          text:   `Thank you for your answer. Processing...`,
        });

        // Check if interview was terminated early
        if (evaluation.interview_terminated && evaluation.final_report) {
          setFinalReport(evaluation.final_report);
          setTimeout(() => {
            setStage('summary');
            addMsg({
              sender: 'ai',
              text:   'Thank you for your time. This interview has now ended.',
              meta:   'Session closed',
            });
            // Wait 5 seconds so the candidate can read the thank-you message,
            // then navigate to results
            setTimeout(() => {
              onComplete(evaluation.final_report);
            }, 5000);
          }, 1000);
        } else {
          setTimeout(() => {
            loadQuestion(questionNumber + 1);
          }, 1000);
        }
      } catch (err) {
        const msg = (err as Error).message;
        if (msg.includes('completed')) {
          setStage('summary');
          addMsg({
            sender: 'ai',
            text:   'Thank you for your time. This interview has now ended.',
            meta:   'Session closed',
          });
          // Wait 5 seconds so the candidate can read the thank-you message,
          // then fetch the evaluation report and navigate to results
          setTimeout(async () => {
            try {
              const summary = await interviewService.getSessionSummary?.(sessionId);
              onComplete(summary);
            } catch (e) {
              onComplete();
            }
          }, 5000);
        } else {
          setError('Error submitting answer: ' + msg);
        }
      } finally {
        setLoading(false);
      }
    }
  };

  const inputActive = stage === 'waiting_ready' || stage === 'asking_questions';

  return (
    <div style={{ maxWidth: 820, margin: '0 auto', padding: '0 24px 40px', animation: 'fadeUp 0.4s ease both' }}>
      <InterviewHeader
        candidateInfo={candidateInfo}
        stage={stage}
      />

      <ErrorBar message={error} />

      {/* Always show chat window (includes greeting + "Thank you" message) */}
      <ChatWindow
        messages={messages}
        candidateInitials={initials(candidateInfo?.candidateName || 'C')}
      />

      {inputActive && (
        <ChatInput
          onSend={handleSend}
          loading={loading}
          placeholder={
            stage === 'waiting_ready'
              ? 'Type "Ready" to begin your interview…'
              : 'Share your answer here…'
          }
        />
      )}

      {/* Answer counter badges removed per requirement */}

      {/* After interview completes, show the evaluation report */}
      {stage === 'summary' && finalReport && (
        <FinalReport
          report={finalReport}
          candidateName={candidateInfo?.candidateName || 'Candidate'}
        />
      )}
    </div>
  );
}
