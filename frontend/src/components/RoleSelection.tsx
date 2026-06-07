import React, { useState } from 'react';
import { interviewService } from '@/services/interviewService';
import {
  Eyebrow,
  SectionHeading,
  Muted,
  PrimaryButton,
  GhostButton,
  ErrorBar,
} from './UI';

interface RoleSelectionProps {
  candidateInfo: {
    candidateName: string;
    email: string;
    resumeText?: string;
    resumeFile?: File | null;
  };
  onStart: (info: any, sessionId: string) => void;
  onBack: () => void;
}

const ROLES = [
  { name: 'Backend Engineer',    icon: '⚙️',  desc: 'APIs, databases, architecture'        },
  { name: 'Frontend Engineer',   icon: '🎨',  desc: 'UI, performance, accessibility'        },
  { name: 'Full Stack Engineer', icon: '🔗',  desc: 'End-to-end product development'        },
  { name: 'AI / ML Engineer',    icon: '🤖',  desc: 'Models, training, deployment'          },
  { name: 'DevOps Engineer',     icon: '🚀',  desc: 'CI/CD, infrastructure, reliability'    },
  { name: 'Data Scientist',      icon: '📊',  desc: 'Analytics, modeling, insights'         },
];

export default function RoleSelection({ candidateInfo, onStart, onBack }: RoleSelectionProps) {
  const [selectedRole, setSelectedRole] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hovered, setHovered] = useState('');

  const handleStart = async () => {
    if (!selectedRole) { setError('Please select a role to continue.'); return; }
    setLoading(true);
    setError('');
    try {
      const response = await interviewService.startInterview({
        candidate_name: candidateInfo.candidateName,
        email:          candidateInfo.email,
        role:           selectedRole,
        resume_text:    candidateInfo.resumeText || '',
        resume_file:    candidateInfo.resumeFile || null,
      });
      onStart({ ...candidateInfo, role: selectedRole }, response.session_id);
    } catch (err) {
      setError('Error starting interview: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 820, margin: '0 auto', padding: '0 24px 40px', animation: 'fadeUp 0.4s ease both' }}>

      {/* Header */}
      <div style={{ padding: '40px 0 28px' }}>
        <Eyebrow>Step 2 of 3</Eyebrow>
        <SectionHeading>Select your target role</SectionHeading>
        <Muted>We'll tailor questions to the skills that matter most for this position.</Muted>
      </div>

      <ErrorBar message={error} />

      {/* Role grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: 12,
        marginBottom: 28,
      }}>
        {ROLES.map(({ name, icon, desc }) => {
          const isSelected = selectedRole === name;
          const isHovered  = hovered === name;

          return (
            <div
              key={name}
              onClick={() => setSelectedRole(name)}
              onMouseEnter={() => setHovered(name)}
              onMouseLeave={() => setHovered('')}
              style={{
                position: 'relative',
                padding: '20px 18px 18px',
                background: isSelected || isHovered ? 'var(--surface3)' : 'var(--surface2)',
                border: `1px solid ${isSelected ? 'var(--gold)' : isHovered ? 'rgba(201,168,76,0.35)' : 'var(--border)'}`,
                borderRadius: 'var(--radius)',
                cursor: 'pointer',
                transition: 'all var(--transition)',
                overflow: 'hidden',
              }}
            >
              {/* Bottom gold bar */}
              <div style={{
                position: 'absolute',
                bottom: 0, left: 0, right: 0,
                height: 2,
                background: 'var(--gold)',
                transform: `scaleX(${isSelected ? 1 : isHovered ? 0.5 : 0})`,
                transformOrigin: 'left',
                transition: 'transform 0.25s ease',
              }} />

              {/* Checkmark */}
              <div style={{
                position: 'absolute',
                top: 14, right: 14,
                width: 20, height: 20,
                borderRadius: '50%',
                border: `1.5px solid ${isSelected ? 'var(--gold)' : 'var(--border-md)'}`,
                background: isSelected ? 'var(--gold)' : 'transparent',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 10,
                color: '#0E0E10',
                transition: 'all var(--transition)',
              }}>
                {isSelected && '✓'}
              </div>

              <div style={{ fontSize: 28, marginBottom: 12 }}>{icon}</div>
              <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--text)', marginBottom: 4 }}>
                {name}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{desc}</div>
            </div>
          );
        })}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 12 }}>
        <GhostButton onClick={onBack}>← Back</GhostButton>
        <PrimaryButton onClick={handleStart} loading={loading} style={{ flex: 1 }}>
          Begin Interview →
        </PrimaryButton>
      </div>
    </div>
  );
}
