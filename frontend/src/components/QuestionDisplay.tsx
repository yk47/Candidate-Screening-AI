import React from 'react';

interface QuestionDisplayProps {
  question: {
    question_text: string;
    topic: string;
    difficulty: string;
    question_number?: number;
    total_questions?: number;
  };
}

const DIFFICULTY_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  easy:   { bg: 'var(--green-dim)',  border: 'var(--green-border)', text: 'var(--green)' },
  medium: { bg: 'var(--gold-dim)',   border: 'var(--border-gold)',  text: 'var(--gold)' },
  hard:   { bg: 'var(--red-dim)',    border: 'var(--red-border)',   text: 'var(--red)' },
};

export default function QuestionDisplay({ question }: QuestionDisplayProps) {
  const diff   = question.difficulty.toLowerCase();
  const colors = DIFFICULTY_COLORS[diff] ?? DIFFICULTY_COLORS.medium;

  return (
    <div style={{
      background: 'var(--surface2)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius)',
      padding: '24px 28px',
      marginBottom: 20,
      animation: 'slideIn 0.3s ease both',
    }}>
      {/* Tags row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        {question.question_number && (
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 10,
            letterSpacing: '0.08em',
            color: 'var(--text-dim)',
            textTransform: 'uppercase',
          }}>
            Q{question.question_number}
            {question.total_questions ? `/${question.total_questions}` : ''}
          </span>
        )}

        {question.topic && (
          <span style={{
            fontSize: 11,
            padding: '3px 10px',
            borderRadius: 40,
            background: 'var(--surface4)',
            border: '1px solid var(--border)',
            color: 'var(--text-muted)',
          }}>
            {question.topic}
          </span>
        )}

        <span style={{
          fontSize: 11,
          padding: '3px 10px',
          borderRadius: 40,
          background: colors.bg,
          border: `1px solid ${colors.border}`,
          color: colors.text,
          textTransform: 'capitalize',
        }}>
          {question.difficulty}
        </span>
      </div>

      {/* Question text */}
      <p style={{
        fontSize: 16,
        lineHeight: 1.7,
        color: 'var(--text)',
        fontWeight: 400,
      }}>
        {question.question_text}
      </p>
    </div>
  );
}
