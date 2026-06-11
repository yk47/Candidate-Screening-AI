import React, { useEffect, useRef } from 'react';
import { PrimaryButton } from './UI';

interface FinalReportProps {
  report: any;
  candidateName: string;
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
  if (avg >= 9.5) return 'O+';
  if (avg >= 9.0) return 'O';
  if (avg >= 8.5) return 'A+';
  if (avg >= 8.0) return 'A';
  if (avg >= 7.0) return 'B+';
  if (avg >= 6.0) return 'B';
  if (avg >= 5.0) return 'C+';
  if (avg >= 4.0) return 'C';
  return 'D';
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

export default function FinalReport({ report, candidateName, onComplete }: FinalReportProps) {
  if (!report) return null;

  const role = report.role || '';
  const avg = typeof report?.average_score === 'number' ? report.average_score : 0;
  const grade = gradeFromScore(avg * 10);
  const overallScore = report.overall_score || 0;

  const scores: [string, number][] = report?.scores
    ? Object.entries(report.scores).map(([k, v]) => [k, v as number])
    : [];

  const recommendationColors: Record<string, string> = {
    "Strong Hire": "var(--success)",
    "Hire": "var(--gold)",
    "Borderline": "var(--warning)",
    "No Hire": "var(--danger)",
  };

  const recommendationColor =
    recommendationColors[String(report.hiring_recommendation)] ??
    "var(--gold)";

  return (
    <div style={{
      maxWidth: 900,
      margin: '0 auto',
      padding: '40px 24px',
      animation: 'fadeUp 0.6s ease both'
    }}>
      {/* Trophy header */}
      <div style={{ textAlign: 'center', paddingBottom: 32, borderBottom: '1px solid var(--border)', marginBottom: 32 }}>
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
        <h1 style={{ fontSize: 28, fontWeight: 700, color: 'var(--text)', marginBottom: 6, fontFamily: 'var(--font-display)' }}>
          Interview Complete! 🎉
        </h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>
          {candidateName} — {role}
        </p>
      </div>

      {/* Stat row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 24 }}>
        <StatCard num={String(report?.total_questions ?? 5)} label="Questions" sub={`${report?.questions_answered ?? 0} answered`} />
        <StatCard num={(avg * 10).toFixed(1)} label="Avg Score" sub="out of 10" />
        <StatCard num={grade} label="Overall Grade" />
      </div>

      {/* Hiring Recommendation */}
      <div style={{
        padding: 24,
        background: `linear-gradient(135deg, rgba(${
          recommendationColor === 'var(--success)' ? '76,201,121' :
          recommendationColor === 'var(--gold)' ? '201,168,76' :
          recommendationColor === 'var(--warning)' ? '255,193,7' :
          '239,68,68'
        },0.1) 0%, transparent 100%)`,
        border: `1.5px solid ${recommendationColor}`,
        borderRadius: 12,
        marginBottom: 32,
        textAlign: 'center'
      }}>
        <div style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 8 }}>
          Hiring Recommendation
        </div>
        <div style={{ fontSize: 28, fontWeight: 700, color: recommendationColor }}>
          {report.hiring_recommendation}
        </div>
      </div>

      {/* Score bars from topic scores */}
      {scores.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text)', marginBottom: 16 }}>
            Topic Scores
          </h2>
          {scores.map(([topic, score]) => (
            <ScoreBar key={topic} label={topic} score={score} />
          ))}
        </div>
      )}

      {/* Communication Assessment */}
      {report.communication_assessment && (
        <div style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text)', marginBottom: 16 }}>
            Communication Assessment
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 16
          }}>
            {Object.entries(report.communication_assessment).map(([key, value]: [string, any]) => (
              <div key={key} style={{
                padding: 16,
                background: 'var(--surface2)',
                border: '1px solid var(--border)',
                borderRadius: 8
              }}>
                <div style={{
                  fontSize: 12, color: 'var(--text-muted)',
                  textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8
                }}>
                  {key.replace(/_/g, ' ')}
                </div>
                <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--gold)' }}>
                  {value}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strengths & Weaknesses */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: 16,
        marginBottom: 28
      }}>
        <TagGroup title="Strengths" items={report?.strengths ?? []} variant="green" />
        <TagGroup title="Growth Areas" items={report?.weaknesses ?? []} variant="gold" />
      </div>

      {/* Topic-wise Breakdown */}
      {report.topic_wise_breakdown && Object.keys(report.topic_wise_breakdown).length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text)', marginBottom: 16 }}>
            Topic-wise Breakdown
          </h2>
          <div style={{ display: 'grid', gap: 12 }}>
            {Object.entries(report.topic_wise_breakdown).map(([topic, data]: [string, any]) => (
              <div key={topic} style={{
                padding: 16, background: 'var(--surface2)',
                border: '1px solid var(--border)', borderRadius: 8
              }}>
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8
                }}>
                  <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text)', margin: 0 }}>{topic}</h3>
                  <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--gold)', fontFamily: 'var(--font-mono)' }}>
                    {data.score}/10
                  </div>
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '8px 0 4px', lineHeight: 1.5 }}>
                  {data.observations}
                </p>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: 0, fontStyle: 'italic' }}>
                  💡 {data.suggestions}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Learning Path */}
      {report.learning_path && report.learning_path.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text)', marginBottom: 16 }}>
            Suggested Learning Path 🚀
          </h2>
          <div style={{ display: 'grid', gap: 12 }}>
            {report.learning_path.map((item: any, i: number) => (
              <div key={i} style={{
                padding: 16,
                background: 'linear-gradient(135deg, rgba(201,168,76,0.1) 0%, transparent 100%)',
                border: '1px solid rgba(201,168,76,0.2)', borderRadius: 8
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--gold)', margin: 0 }}>{item.topic}</h3>
                  <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    {item.priority} Priority
                  </span>
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '8px 0 4px', lineHeight: 1.5 }}>
                  {item.suggested_resources}
                </p>
                {item.prerequisites && item.prerequisites.length > 0 && (
                  <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: 0, fontStyle: 'italic' }}>
                    Prerequisites: {item.prerequisites.join(', ')}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Q&A Review */}
      {report.questions_and_answers && report.questions_and_answers.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h3 style={{
            fontSize: 16, fontWeight: 600, color: 'var(--text)', marginBottom: 16,
            fontFamily: 'var(--font-display)', display: 'flex', alignItems: 'center', gap: 10
          }}>
            <span style={{ width: 4, height: 4, borderRadius: '50%', background: 'var(--gold)' }} />
            Detailed Feedback
          </h3>
          {report.questions_and_answers.map((qa: any, idx: number) => (
            <QuestionFeedback key={idx} qa={qa} />
          ))}
        </div>
      )}

      {/* Summary */}
      {report.summary && (
        <div style={{
          padding: 24, background: 'var(--surface2)',
          border: '1px solid var(--border)', borderRadius: 12, marginBottom: 32
        }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text)', marginBottom: 12 }}>
            Interview Summary
          </h2>
          <p style={{ fontSize: 14, color: 'var(--text-muted)', lineHeight: 1.6, margin: 0, whiteSpace: 'pre-wrap' }}>
            {report.summary}
          </p>
        </div>
      )}

      {/* Early Termination Notice */}
      {report.early_termination && (
        <div style={{
          padding: 16, background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 8, marginBottom: 32
        }}>
          <p style={{ fontSize: 13, color: 'var(--text)', margin: 0 }}>
            ⚠️ <strong>Note:</strong> This interview was terminated early due to: {report.termination_reason?.replace(/_/g, ' ')}
          </p>
        </div>
      )}

      <PrimaryButton onClick={onComplete}>
        Start New Interview
      </PrimaryButton>
    </div>
  );
}