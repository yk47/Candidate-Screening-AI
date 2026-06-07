import React, { useEffect, useRef } from 'react';
import { PrimaryButton } from './UI';

interface InterviewSummaryProps {
  summary: any;
  candidateInfo: any;
  onComplete: () => void;
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  const barRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (barRef.current) barRef.current.style.width = `${Math.min(score * 10, 100)}%`;
    }, 200);
    return () => clearTimeout(timer);
  }, [score]);

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 14,
      padding: '14px 0',
      borderBottom: '1px solid var(--border)',
    }}>
      <div style={{ flex: 1, fontSize: 14, color: 'var(--text)' }}>{label}</div>
      <div style={{
        flex: 2, height: 4,
        background: 'var(--surface4)',
        borderRadius: 4,
        overflow: 'hidden',
      }}>
        <div
          ref={barRef}
          style={{
            height: '100%',
            width: '0%',
            background: 'var(--gold)',
            borderRadius: 4,
            transition: 'width 1.1s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        />
      </div>
      <div style={{
        fontFamily: 'var(--font-mono)',
        fontSize: 13,
        color: 'var(--gold)',
        minWidth: 38,
        textAlign: 'right',
      }}>
        {score}/10
      </div>
    </div>
  );
}

function StatCard({ num, label, sub }: { num: string; label: string; sub?: string }) {
  return (
    <div style={{
      background: 'var(--surface2)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius)',
      padding: '22px 20px',
      textAlign: 'center',
    }}>
      <div style={{
        fontFamily: 'var(--font-display)',
        fontSize: 36,
        fontWeight: 700,
        color: 'var(--gold)',
        marginBottom: 6,
      }}>
        {num}
      </div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.07em', textTransform: 'uppercase' }}>
        {label}
      </div>
      {sub && (
        <div style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 3 }}>{sub}</div>
      )}
    </div>
  );
}

function TagGroup({
  title,
  items,
  variant,
}: {
  title: string;
  items: string[];
  variant: 'green' | 'gold';
}) {
  const colors = {
    green: { bg: 'var(--green-dim)', border: 'var(--green-border)', text: 'var(--green)', symbol: '✓' },
    gold:  { bg: 'var(--gold-dim)', border: 'var(--border-gold)', text: 'var(--gold)',  symbol: '↗' },
  }[variant];

  return (
    <div style={{
      background: 'var(--surface2)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius)',
      padding: '20px',
    }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
        fontSize: 11, fontWeight: 500,
        letterSpacing: '0.10em', textTransform: 'uppercase' as const,
        color: 'var(--text-muted)',
        marginBottom: 14,
        fontFamily: 'var(--font-mono)',
      }}>
        <span style={{ width: 12, height: 1, background: 'var(--gold)', display: 'inline-block' }} />
        {title}
      </div>

      {items.length === 0 ? (
        <p style={{ fontSize: 13, color: 'var(--text-dim)' }}>None identified.</p>
      ) : (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {items.map((item, i) => (
            <span key={i} style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              padding: '6px 12px',
              borderRadius: 40,
              fontSize: 13,
              background: colors.bg,
              border: `1px solid ${colors.border}`,
              color: colors.text,
            }}>
              {colors.symbol} {item}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function gradeFromScore(avg: number): string {
  if (avg >= 9.5) return 'A+';
  if (avg >= 9.0) return 'A';
  if (avg >= 8.5) return 'A−';
  if (avg >= 8.0) return 'B+';
  if (avg >= 7.5) return 'B';
  if (avg >= 7.0) return 'B−';
  if (avg >= 6.0) return 'C+';
  return 'C';
}

function getScoreColor(score: number): string {
  if (score >= 8) return 'var(--green)';
  if (score >= 6) return 'var(--gold)';
  if (score >= 4) return 'var(--orange)';
  return 'var(--red)';
}

function QuestionFeedback({ qa }: { qa: any }) {
  const scoreColor = getScoreColor((qa.score || 0) * 10);
  
  return (
    <div style={{
      background: 'var(--surface2)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius)',
      padding: '20px',
      marginBottom: 12,
    }}>
      <div style={{ marginBottom: 16 }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: 8,
          gap: 12,
        }}>
          <div style={{ flex: 1 }}>
            <div style={{
              fontSize: 12,
              color: 'var(--text-muted)',
              fontFamily: 'var(--font-mono)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: 4,
            }}>
              {qa.topic}
            </div>
            <h4 style={{
              fontSize: 14,
              fontWeight: 600,
              color: 'var(--text)',
              margin: 0,
              lineHeight: 1.5,
            }}>
              {qa.question}
            </h4>
          </div>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 4,
            paddingTop: 4,
          }}>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 18,
              fontWeight: 700,
              color: scoreColor,
            }}>
              {(qa.score * 10).toFixed(1)}
            </div>
            <div style={{
              fontSize: 10,
              color: 'var(--text-muted)',
              textAlign: 'center',
            }}>
              / 10
            </div>
          </div>
        </div>
      </div>

      {qa.answered ? (
        <>
          <div style={{ marginBottom: 12 }}>
            <div style={{
              fontSize: 11,
              color: 'var(--text-muted)',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: 6,
            }}>
              Your Answer
            </div>
            <div style={{
              fontSize: 13,
              color: 'var(--text)',
              lineHeight: 1.6,
              padding: '10px 12px',
              background: 'var(--surface3)',
              borderLeft: `3px solid ${scoreColor}`,
              borderRadius: 2,
            }}>
              {qa.answer}
            </div>
          </div>

          {qa.feedback && (
            <div style={{ marginBottom: 0 }}>
              <div style={{
                fontSize: 11,
                color: 'var(--text-muted)',
                fontWeight: 500,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                marginBottom: 6,
              }}>
                Feedback
              </div>
              <div style={{
                fontSize: 13,
                color: 'var(--text)',
                lineHeight: 1.6,
                padding: '10px 12px',
                background: 'var(--surface3)',
                borderRadius: 4,
              }}>
                {qa.feedback}
              </div>
            </div>
          )}
        </>
      ) : (
        <div style={{
          fontSize: 13,
          color: 'var(--text-dim)',
          fontStyle: 'italic',
        }}>
          Question was not answered.
        </div>
      )}
    </div>
  );
}

export default function InterviewSummary({ summary, candidateInfo, onComplete }: InterviewSummaryProps) {
  const name  = candidateInfo?.candidateName || 'Candidate';
  const role  = candidateInfo?.role || '';
  const avg   = typeof summary?.average_score === 'number'
    ? summary.average_score
    : 0;
  const grade = gradeFromScore(avg * 10);

  const scores: [string, number][] = summary?.scores
    ? Object.entries(summary.scores).map(([k, v]) => [k, v as number])
    : [];

  return (
    <div style={{
      maxWidth: 820, margin: '0 auto', padding: '0 24px 40px',
      animation: 'fadeUp 0.4s ease both',
    }}>

      {/* Trophy header */}
      <div style={{ textAlign: 'center', padding: '40px 0 32px' }}>
        <div style={{
          width: 72, height: 72,
          background: 'var(--gold-dim)',
          border: '1px solid var(--border-gold)',
          borderRadius: 20,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 34,
          margin: '0 auto 20px',
        }}>
          🏆
        </div>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 28, fontWeight: 700,
          color: 'var(--text)',
          marginBottom: 6,
        }}>
          {name}
        </h2>
        <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>
          {role} — Interview Complete
        </p>
      </div>

      {/* Stat row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 24 }}>
        <StatCard num={String(summary?.total_questions ?? 5)}   label="Questions" />
        <StatCard num={(avg * 10).toFixed(1)} label="Avg Score" sub="out of 10" />
        <StatCard num={grade}                  label="Overall Grade" />
      </div>

      {/* Score bars */}
      {scores.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          {scores.map(([topic, score]) => (
            <ScoreBar key={topic} label={topic} score={score} />
          ))}
        </div>
      )}

      {/* Strengths / Areas */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 28 }}>
        <TagGroup
          title="Strengths"
          items={summary?.strengths ?? []}
          variant="green"
        />
        <TagGroup
          title="Growth areas"
          items={summary?.weaknesses ?? []}
          variant="gold"
        />
      </div>

      {/* Questions & Answers Feedback */}
      {summary?.questions_and_answers && summary.questions_and_answers.length > 0 && (
        <div style={{ marginBottom: 28 }}>
          <h3 style={{
            fontSize: 16,
            fontWeight: 600,
            color: 'var(--text)',
            marginBottom: 16,
            fontFamily: 'var(--font-display)',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
          }}>
            <span style={{
              width: 4,
              height: 4,
              borderRadius: '50%',
              background: 'var(--gold)',
            }} />
            Detailed Feedback
          </h3>
          {summary.questions_and_answers.map((qa: any, idx: number) => (
            <QuestionFeedback key={idx} qa={qa} />
          ))}
        </div>
      )}

      <PrimaryButton onClick={onComplete}>
        Start New Interview
      </PrimaryButton>
    </div>
  );
}
