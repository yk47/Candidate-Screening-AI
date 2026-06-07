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

/* ── Progress dots ── */
function ProgressDots({ current, total }: { current: number; total: number }) {
  return (
    <div style={{ display: 'flex', gap: 5 }}>
      {Array.from({ length: total }).map((_, i) => (
        <div key={i} style={{
          width: 20, height: 4,
          borderRadius: 4,
          background:
            i < current - 1 ? 'var(--gold)'
            : i === current - 1 ? 'rgba(201,168,76,0.5)'
            : 'var(--surface4)',
          transition: 'background 0.4s ease',
        }} />
      ))}
    </div>
  );
}

/* ── Interview header ── */
function InterviewHeader({
  candidateInfo,
  questionNumber,
  maxQuestions,
  stage,
}: {
  candidateInfo: any;
  questionNumber: number;
  maxQuestions: number;
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

      {/* Progress */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        {isLive && <ProgressDots current={questionNumber} total={maxQuestions} />}
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
            ? `Q ${questionNumber} / ${maxQuestions}`
            : stage === 'greeting' || stage === 'waiting_ready'
              ? 'Starting…'
              : 'Wrapping up…'
          }
        </div>
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
    if (stage === 'summary') {
      onComplete(finalReport);
    }
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
        meta:   `Question ${q.question_number ?? (expectedNum || questionNumber + 1)} · ${q.topic} · ${q.difficulty}`,
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
    addMsg({
      sender: 'ai',
      text:   '🎉 Interview complete!\n\nThank you for your time. Your responses have been recorded and will be reviewed shortly.',
      meta:   'Session closed',
    });
    // onComplete will be called by useEffect when stage changes to 'summary'
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
          meta:   'Acknowledgment',
        });

        // Check if interview was terminated early
        if (evaluation.interview_terminated && evaluation.final_report) {
          setFinalReport(evaluation.final_report);
          setTimeout(() => {
            setStage('summary');
            addMsg({
              sender: 'ai',
              text:   '📋 Interview completed.\n\nHere is your detailed evaluation report:',
              meta:   'Final Report',
            });
          }, 1000);
        } else {
          setTimeout(() => {
            loadQuestion(questionNumber + 1);
          }, 1000);
        }
      } catch (err) {
        const msg = (err as Error).message;
        if (msg.includes('completed')) {
          // Fetch final report when interview completes naturally
          try {
            const summary = await interviewService.getSessionSummary?.(sessionId);
            if (summary) {
              setFinalReport(summary);
            }
          } catch (e) {
            // Fallback if summary endpoint doesn't exist
          }
          setStage('summary');
          addMsg({ sender: 'ai', text: '📋 Interview completed.\n\nHere is your detailed evaluation report:', meta: 'Complete' });
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
        questionNumber={questionNumber}
        maxQuestions={Math.max(7, questionNumber + 2)}
        stage={stage}
      />

      <ErrorBar message={error} />

      {/* Display chat during interview, report after completion */}
      {stage !== 'summary' || !finalReport ? (
        <>
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

          {stage === 'asking_questions' && answers.length > 0 && (
            <div style={{ marginTop: 20, display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
              {answers.map((a, i) => (
                <div key={i} style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 11,
                  padding: '4px 12px',
                  borderRadius: 40,
                  background: 'var(--surface2)',
                  border: '1px solid var(--border)',
                  color: 'var(--gold)',
                }}>
                  Q{a.questionNumber}
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <FinalReport
          report={finalReport}
          candidateName={candidateInfo?.candidateName || 'Candidate'}
        />
      )}
    </div>
  );
}
