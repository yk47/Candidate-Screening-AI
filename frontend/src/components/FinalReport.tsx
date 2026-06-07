import React from 'react';

interface FinalReportProps {
  report: any;
  candidateName: string;
}

export default function FinalReport({ report, candidateName }: FinalReportProps) {
  if (!report) return null;

  const recommendationColor = {
    "Strong Hire": "var(--success)",
    "Hire": "var(--gold)",
    "Borderline": "var(--warning)",
    "No Hire": "var(--danger)"
  }[report.hiring_recommendation] || "var(--gold)";

  return (
    <div style={{
      maxWidth: 900,
      margin: '0 auto',
      padding: '40px 24px',
      animation: 'fadeUp 0.6s ease both'
    }}>
      {/* Header */}
      <div style={{
        textAlign: 'center',
        marginBottom: 40,
        paddingBottom: 30,
        borderBottom: '1px solid var(--border)'
      }}>
        <h1 style={{ fontSize: 32, fontWeight: 700, color: 'var(--text)', marginBottom: 8 }}>
          Interview Complete! 🎉
        </h1>
        <p style={{ fontSize: 16, color: 'var(--text-muted)', marginBottom: 24 }}>
          {candidateName}, here's your comprehensive evaluation
        </p>

        {/* Overall Score */}
        <div style={{
          display: 'inline-block',
          textAlign: 'center',
          padding: '24px 40px',
          background: 'linear-gradient(135deg, rgba(201,168,76,0.1) 0%, rgba(201,168,76,0.05) 100%)',
          borderRadius: 16,
          border: '1px solid rgba(201,168,76,0.2)'
        }}>
          <div style={{ fontSize: 48, fontWeight: 700, color: 'var(--gold)', lineHeight: 1 }}>
            {report.overall_score || 0}
          </div>
          <div style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 8 }}>
            Overall Score / 10
          </div>
        </div>
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
        <div style={{
          fontSize: 28,
          fontWeight: 700,
          color: recommendationColor,
        }}>
          {report.hiring_recommendation}
        </div>
      </div>

      {/* Communication Assessment */}
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text)', marginBottom: 16 }}>
          Communication Assessment
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 16
        }}>
          {report.communication_assessment && Object.entries(report.communication_assessment).map(([key, value]: [string, any]) => (
            <div key={key} style={{
              padding: 16,
              background: 'var(--surface2)',
              border: '1px solid var(--border)',
              borderRadius: 8
            }}>
              <div style={{
                fontSize: 12,
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: 0.5,
                marginBottom: 8
              }}>
                {key.replace(/_/g, ' ')}
              </div>
              <div style={{
                fontSize: 16,
                fontWeight: 600,
                color: 'var(--gold)'
              }}>
                {value}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: 24,
        marginBottom: 32
      }}>
        {/* Strengths */}
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text)', marginBottom: 16 }}>
            Technical Strengths 💪
          </h2>
          <ul style={{
            listStyle: 'none',
            padding: 0,
            margin: 0
          }}>
            {report.strengths && report.strengths.length > 0 ? (
              report.strengths.map((strength: string, i: number) => (
                <li key={i} style={{
                  padding: 12,
                  marginBottom: 8,
                  background: 'rgba(76, 201, 121, 0.1)',
                  border: '1px solid rgba(76, 201, 121, 0.2)',
                  borderRadius: 6,
                  color: 'var(--text)',
                  fontSize: 14
                }}>
                  ✓ {strength}
                </li>
              ))
            ) : (
              <li style={{ padding: 12, color: 'var(--text-muted)', fontSize: 14 }}>
                No strengths identified
              </li>
            )}
          </ul>
        </div>

        {/* Weaknesses */}
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text)', marginBottom: 16 }}>
            Areas for Improvement 📈
          </h2>
          <ul style={{
            listStyle: 'none',
            padding: 0,
            margin: 0
          }}>
            {report.weaknesses && report.weaknesses.length > 0 ? (
              report.weaknesses.map((weakness: string, i: number) => (
                <li key={i} style={{
                  padding: 12,
                  marginBottom: 8,
                  background: 'rgba(255, 193, 7, 0.1)',
                  border: '1px solid rgba(255, 193, 7, 0.2)',
                  borderRadius: 6,
                  color: 'var(--text)',
                  fontSize: 14
                }}>
                  ⚡ {weakness}
                </li>
              ))
            ) : (
              <li style={{ padding: 12, color: 'var(--text-muted)', fontSize: 14 }}>
                No areas identified
              </li>
            )}
          </ul>
        </div>
      </div>

      {/* Topic Breakdown */}
      {report.topic_wise_breakdown && Object.keys(report.topic_wise_breakdown).length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text)', marginBottom: 16 }}>
            Topic-wise Breakdown
          </h2>
          <div style={{
            display: 'grid',
            gap: 12
          }}>
            {Object.entries(report.topic_wise_breakdown).map(([topic, data]: [string, any]) => (
              <div key={topic} style={{
                padding: 16,
                background: 'var(--surface2)',
                border: '1px solid var(--border)',
                borderRadius: 8
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 8
                }}>
                  <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text)', margin: 0 }}>
                    {topic}
                  </h3>
                  <div style={{
                    fontSize: 16,
                    fontWeight: 700,
                    color: 'var(--gold)',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    {data.score}/10
                  </div>
                </div>
                <p style={{
                  fontSize: 13,
                  color: 'var(--text-muted)',
                  margin: '8px 0 4px',
                  lineHeight: 1.5
                }}>
                  {data.observations}
                </p>
                <p style={{
                  fontSize: 12,
                  color: 'var(--text-muted)',
                  margin: 0,
                  fontStyle: 'italic'
                }}>
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
          <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text)', marginBottom: 16 }}>
            Suggested Learning Path 🚀
          </h2>
          <div style={{
            display: 'grid',
            gap: 12
          }}>
            {report.learning_path.map((item: any, i: number) => (
              <div key={i} style={{
                padding: 16,
                background: 'linear-gradient(135deg, rgba(201,168,76,0.1) 0%, transparent 100%)',
                border: '1px solid rgba(201,168,76,0.2)',
                borderRadius: 8
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 8
                }}>
                  <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--gold)', margin: 0 }}>
                    {item.topic}
                  </h3>
                  <span style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: 'var(--text-muted)',
                    textTransform: 'uppercase'
                  }}>
                    {item.priority} Priority
                  </span>
                </div>
                <p style={{
                  fontSize: 13,
                  color: 'var(--text-muted)',
                  margin: '8px 0 4px',
                  lineHeight: 1.5
                }}>
                  {item.suggested_resources}
                </p>
                {item.prerequisites && item.prerequisites.length > 0 && (
                  <p style={{
                    fontSize: 12,
                    color: 'var(--text-muted)',
                    margin: 0,
                    fontStyle: 'italic'
                  }}>
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
          <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text)', marginBottom: 16 }}>
            Detailed Q&A Review
          </h2>
          <div style={{
            display: 'grid',
            gap: 16
          }}>
            {report.questions_and_answers.map((qa: any, i: number) => (
              <div key={i} style={{
                padding: 16,
                background: 'var(--surface2)',
                border: '1px solid var(--border)',
                borderRadius: 8
              }}>
                {/* Question */}
                <div style={{ marginBottom: 12 }}>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'start',
                    marginBottom: 8
                  }}>
                    <h3 style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: 'var(--gold)',
                      margin: 0
                    }}>
                      Q{i + 1}: {qa.topic}
                    </h3>
                    <div style={{
                      fontSize: 12,
                      fontWeight: 600,
                      color: 'var(--text-muted)',
                      textTransform: 'uppercase'
                    }}>
                      {qa.difficulty}
                    </div>
                  </div>
                  <p style={{
                    fontSize: 13,
                    color: 'var(--text-muted)',
                    margin: 0,
                    fontStyle: 'italic',
                    lineHeight: 1.5
                  }}>
                    {qa.question}
                  </p>
                </div>

                {/* Answer & Feedback */}
                {qa.answered ? (
                  <div style={{ borderTop: '1px solid var(--border)', paddingTop: 12 }}>
                    {/* Score */}
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: 12
                    }}>
                      <span style={{
                        fontSize: 12,
                        color: 'var(--text-muted)',
                        textTransform: 'uppercase',
                        letterSpacing: 0.5
                      }}>
                        Your Answer
                      </span>
                      <div style={{
                        fontSize: 14,
                        fontWeight: 700,
                        color: 'var(--gold)',
                        fontFamily: 'var(--font-mono)'
                      }}>
                        {(qa.score * 10).toFixed(1)}/10
                      </div>
                    </div>

                    {/* Answer Text */}
                    <p style={{
                      fontSize: 13,
                      color: 'var(--text)',
                      margin: '8px 0',
                      lineHeight: 1.5,
                      padding: 8,
                      background: 'rgba(201, 168, 76, 0.05)',
                      borderRadius: 4,
                      borderLeft: '2px solid var(--gold)'
                    }}>
                      {qa.answer}
                    </p>

                    {/* Feedback */}
                    {qa.feedback && (
                      <p style={{
                        fontSize: 12,
                        color: 'var(--text-muted)',
                        margin: '8px 0 0',
                        lineHeight: 1.5,
                        fontStyle: 'italic'
                      }}>
                        💬 <strong>Feedback:</strong> {qa.feedback}
                      </p>
                    )}
                  </div>
                ) : (
                  <p style={{
                    fontSize: 12,
                    color: 'var(--text-muted)',
                    margin: 0,
                    fontStyle: 'italic'
                  }}>
                    Not answered
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary */}
      {report.summary && (
        <div style={{
          padding: 24,
          background: 'var(--surface2)',
          border: '1px solid var(--border)',
          borderRadius: 12,
          marginBottom: 32
        }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text)', marginBottom: 12 }}>
            Interview Summary
          </h2>
          <p style={{
            fontSize: 14,
            color: 'var(--text-muted)',
            lineHeight: 1.6,
            margin: 0,
            whiteSpace: 'pre-wrap'
          }}>
            {report.summary}
          </p>
        </div>
      )}

      {/* Early Termination Notice */}
      {report.early_termination && (
        <div style={{
          padding: 16,
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: 8,
          marginBottom: 32
        }}>
          <p style={{ fontSize: 13, color: 'var(--text)', margin: 0 }}>
            ⚠️ <strong>Note:</strong> This interview was terminated early due to: {report.termination_reason?.replace(/_/g, ' ')}
          </p>
        </div>
      )}
    </div>
  );
}
