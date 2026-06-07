import React, { useState } from 'react';
import ResumeUpload from '@/components/ResumeUpload';
import RoleSelection from '@/components/RoleSelection';
import Interview from '@/components/Interview';
import InterviewSummary from '@/components/InterviewSummary';

type Stage = 'upload' | 'role' | 'interview' | 'summary';

/* ── Step indicator ── */
const STEPS = ['Profile', 'Role', 'Interview', 'Results'] as const;

function StepBar({ stage }: { stage: Stage }) {
  const idx = { upload: 0, role: 1, interview: 2, summary: 3 }[stage];

  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 0,
      padding: '0 24px',
    }}>
      {STEPS.map((label, i) => {
        const done    = i < idx;
        const current = i === idx;

        return (
          <React.Fragment key={label}>
            {i > 0 && (
              <div style={{
                width: 48, height: 1,
                background: done ? 'var(--gold)' : 'var(--border)',
                transition: 'background 0.4s ease',
                flexShrink: 0,
              }} />
            )}
            <div style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
              cursor: 'default',
            }}>
              <div style={{
                width: 28, height: 28,
                borderRadius: '50%',
                border: `1.5px solid ${current ? 'var(--gold)' : done ? 'var(--gold)' : 'var(--border)'}`,
                background: done ? 'var(--gold)' : current ? 'var(--gold-dim)' : 'transparent',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 11,
                color: done ? '#0E0E10' : current ? 'var(--gold)' : 'var(--text-dim)',
                fontWeight: 600,
                fontFamily: 'var(--font-mono)',
                transition: 'all 0.4s ease',
              }}>
                {done ? '✓' : i + 1}
              </div>
              <div style={{
                fontSize: 10,
                letterSpacing: '0.08em',
                textTransform: 'uppercase' as const,
                color: current ? 'var(--gold)' : done ? 'var(--text-muted)' : 'var(--text-dim)',
                fontFamily: 'var(--font-mono)',
                transition: 'color 0.3s ease',
              }}>
                {label}
              </div>
            </div>
          </React.Fragment>
        );
      })}
    </nav>
  );
}

/* ── Top bar ── */
function TopBar({ stage }: { stage: Stage }) {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '18px 32px',
      borderBottom: '1px solid var(--border)',
      background: 'var(--surface)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 32, height: 32,
          borderRadius: 8,
          background: 'var(--gold-dim)',
          border: '1px solid var(--border-gold)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 16,
        }}>
          ✦
        </div>
        <div>
          <div style={{
            fontFamily: 'var(--font-display)',
            fontSize: 15,
            fontWeight: 700,
            color: 'var(--text)',
            lineHeight: 1,
          }}>
            InterviewAI
          </div>
        </div>
      </div>

      {/* Step bar */}
      <StepBar stage={stage} />

      {/* Right */}
      <div style={{
        fontFamily: 'var(--font-mono)',
        fontSize: 11,
        color: 'var(--text-dim)',
        letterSpacing: '0.05em',
      }}>
        🔒 Secure session
      </div>
    </header>
  );
}

/* ── Main ── */
export default function Home() {
  const [stage, setStage]           = useState<Stage>('upload');
  const [sessionId, setSessionId]   = useState<string | null>(null);
  const [candidateInfo, setCandidateInfo] = useState<any>(null);
  const [summary, setSummary]       = useState<any>(null);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--dark)', display: 'flex', flexDirection: 'column' }}>
      <TopBar stage={stage} />

      {/* Ambient glow orbs */}
      <div style={{
        position: 'fixed', inset: 0, pointerEvents: 'none', overflow: 'hidden', zIndex: 0,
      }}>
        <div style={{
          position: 'absolute',
          top: '-10%', left: '20%',
          width: 480, height: 480,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(201,168,76,0.06) 0%, transparent 70%)',
        }} />
        <div style={{
          position: 'absolute',
          bottom: '-10%', right: '15%',
          width: 380, height: 380,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(74,158,255,0.04) 0%, transparent 70%)',
        }} />
      </div>

      {/* Content */}
      <main style={{ flex: 1, position: 'relative', zIndex: 1 }}>
        {stage === 'upload' && (
          <ResumeUpload
            onNext={info => {
              setCandidateInfo(info);
              setStage('role');
            }}
          />
        )}

        {stage === 'role' && (
          <RoleSelection
            candidateInfo={candidateInfo}
            onStart={(info, sId) => {
              setCandidateInfo(info);
              setSessionId(sId);
              setStage('interview');
            }}
            onBack={() => setStage('upload')}
          />
        )}

        {stage === 'interview' && sessionId && (
          <Interview
            sessionId={sessionId}
            candidateInfo={candidateInfo}
            onComplete={(finalReport) => {
              setSummary(finalReport);
              setStage('summary');
            }}
          />
        )}

        {stage === 'summary' && (
          <InterviewSummary
            summary={summary}
            candidateInfo={candidateInfo}
            onComplete={() => {
              setSessionId(null);
              setCandidateInfo(null);
              setSummary(null);
              setStage('upload');
            }}
          />
        )}
      </main>

      {/* Footer */}
      <footer style={{
        textAlign: 'center',
        padding: '16px 24px',
        borderTop: '1px solid var(--border)',
        fontFamily: 'var(--font-mono)',
        fontSize: 10,
        color: 'var(--text-dim)',
        letterSpacing: '0.05em',
        position: 'relative', zIndex: 1,
      }}>
        Your information is only used for this session and is never shared.
      </footer>
    </div>
  );
}
