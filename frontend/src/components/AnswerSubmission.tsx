import React, { useState, useRef, useEffect } from 'react';
import { ErrorBar, PrimaryButton } from './UI';

interface AnswerSubmissionProps {
  onSubmit: (answer: string) => void;
  loading: boolean;
  error?: string;
  placeholder?: string;
}

export default function AnswerSubmission({ onSubmit, loading, error, placeholder }: AnswerSubmissionProps) {
  const [answer, setAnswer] = useState('');
  const [focused, setFocused] = useState(false);
  const taRef = useRef<HTMLTextAreaElement>(null);

  /* Auto-resize */
  useEffect(() => {
    if (taRef.current) {
      taRef.current.style.height = 'auto';
      taRef.current.style.height = Math.min(taRef.current.scrollHeight, 240) + 'px';
    }
  }, [answer]);

  const handleSubmit = () => {
    if (!answer.trim() || loading) return;
    onSubmit(answer.trim());
    setAnswer('');
  };

  const charCount = answer.length;

  return (
    <div>
      <ErrorBar message={error ?? ''} />

      {/* Label row */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: 10,
      }}>
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 11, fontWeight: 500,
          letterSpacing: '0.08em',
          textTransform: 'uppercase' as const,
          color: 'var(--text-muted)',
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--gold)' }} />
          Your Answer
        </div>
        {charCount > 0 && (
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dim)' }}>
            {charCount} chars
          </span>
        )}
      </div>

      {/* Textarea */}
      <div style={{
        border: `1px solid ${focused ? 'var(--gold)' : 'var(--border)'}`,
        borderRadius: 'var(--radius)',
        background: focused ? 'var(--surface3)' : 'var(--surface2)',
        transition: 'all var(--transition)',
        padding: '14px 18px',
        marginBottom: 14,
      }}>
        <textarea
          ref={taRef}
          value={answer}
          onChange={e => setAnswer(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          disabled={loading}
          placeholder={placeholder ?? 'Type your answer here. Be as detailed and specific as you can…'}
          rows={6}
          style={{
            width: '100%',
            background: 'none',
            border: 'none',
            outline: 'none',
            resize: 'none',
            fontFamily: 'var(--font-body)',
            fontSize: 15,
            color: 'var(--text)',
            lineHeight: 1.65,
            minHeight: 120,
          }}
        />
      </div>

      <PrimaryButton
        onClick={handleSubmit}
        loading={loading}
        disabled={!answer.trim() || loading}
      >
        {loading ? 'Evaluating…' : 'Submit Answer'}
      </PrimaryButton>
    </div>
  );
}
