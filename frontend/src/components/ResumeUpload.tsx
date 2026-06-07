import React, { useState, useRef } from 'react';
import {
  Eyebrow,
  DisplayHeading,
  Muted,
  FormField,
  TextInput,
  PrimaryButton,
  ErrorBar,
} from './UI';

interface ResumeUploadProps {
  onNext: (info: {
    candidateName: string;
    email: string;
    resumeText?: string;
    resumeFile?: File | null;
  }) => void;
}

const HERO_STATS = [
  { num: '5', label: 'Questions per session' },
  { num: '~12', label: 'Minutes on average' },
  { num: 'AI', label: 'Real-time evaluation' },
];

export default function ResumeUpload({ onNext }: ResumeUploadProps) {
  const [candidateName, setCandidateName] = useState('');
  const [email, setEmail] = useState('');
  const [resumeText, setResumeText] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState('');
  const [fileSize, setFileSize] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File | null | undefined) => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      if (file.type === 'text/plain') {
        const text = await file.text();
        setResumeText(text);
      } else if (file.type === 'application/pdf') {
        setResumeText('');
      } else {
        setError('Please upload a .txt or .pdf file.');
        return;
      }
      setResumeFile(file);
      setFileName(file.name);
      setFileSize((file.size / 1024).toFixed(0) + ' KB');
    } catch (err) {
      setError('Error reading file: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = () => {
    if (!candidateName.trim()) { setError('Please enter your full name.'); return; }
    if (!resumeFile) { setError('Please upload your resume.'); return; }
    setError('');
    onNext({ candidateName: candidateName.trim(), email, resumeText, resumeFile });
  };

  return (
    <div style={{ maxWidth: 820, margin: '0 auto', padding: '0 24px 40px', animation: 'fadeUp 0.4s ease both' }}>

      {/* Hero row */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 48, padding: '48px 0 36px' }}>

        {/* Left: copy */}
        <div style={{ flex: 1 }}>
          <Eyebrow>AI Interview Platform</Eyebrow>
          <DisplayHeading>
            Hire <em style={{ color: 'var(--gold)', fontStyle: 'italic' }}>smarter,</em>
            <br />interview better.
          </DisplayHeading>
          <Muted style={{ maxWidth: 400 }}>
            Create your candidate profile to begin an AI-powered screening session.
            Questions adapt to your resume and role in real time.
          </Muted>
        </div>

        {/* Right: stats */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 0,
          background: 'var(--surface2)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius)',
          overflow: 'hidden',
          minWidth: 190,
          flexShrink: 0,
        }}>
          {HERO_STATS.map((s, i) => (
            <React.Fragment key={s.label}>
              {i > 0 && <div style={{ height: 1, background: 'var(--border)' }} />}
              <div style={{ padding: '18px 22px' }}>
                <div style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: 30,
                  fontWeight: 700,
                  color: 'var(--gold)',
                  lineHeight: 1,
                  marginBottom: 4,
                }}>
                  {s.num}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', letterSpacing: '0.02em' }}>
                  {s.label}
                </div>
              </div>
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Form */}
      <div style={{ maxWidth: 520 }}>
        <ErrorBar message={error} />

        <FormField label="Full Name" required>
          <TextInput
            value={candidateName}
            onChange={setCandidateName}
            placeholder="Alexandra Chen"
          />
        </FormField>

        <FormField label="Email Address">
          <TextInput
            value={email}
            onChange={setEmail}
            type="email"
            placeholder="alex@company.com"
          />
        </FormField>

        <FormField label="Resume" required>
          <div
            onClick={() => inputRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            style={{
              position: 'relative',
              border: `1.5px dashed ${resumeFile ? 'var(--green)' : dragOver ? 'var(--gold)' : 'var(--border-md)'}`,
              borderRadius: 'var(--radius)',
              padding: '36px 24px',
              textAlign: 'center',
              cursor: 'pointer',
              background: resumeFile
                ? 'var(--green-dim)'
                : dragOver
                  ? 'var(--gold-dim)'
                  : 'var(--surface2)',
              transition: 'all var(--transition)',
            }}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".txt,.pdf"
              style={{ display: 'none' }}
              onChange={e => handleFile(e.target.files?.[0])}
              disabled={loading}
            />

            {/* Icon */}
            <div style={{
              width: 52, height: 52,
              borderRadius: 14,
              background: resumeFile ? 'var(--green-dim)' : 'var(--gold-dim)',
              border: `1px solid ${resumeFile ? 'var(--green-border)' : 'var(--border-gold)'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 14px',
              fontSize: 22,
            }}>
              {loading ? '⏳' : resumeFile ? '✅' : '📄'}
            </div>

            {resumeFile ? (
              <>
                <div style={{ fontSize: 15, fontWeight: 500, color: 'var(--green)', marginBottom: 4 }}>
                  {fileName}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  {fileSize} · Click to replace
                </div>
              </>
            ) : (
              <>
                <div style={{ fontSize: 15, fontWeight: 500, color: 'var(--text)', marginBottom: 6 }}>
                  {loading ? 'Reading file…' : 'Drop your resume here'}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  or click to browse — PDF or TXT, up to 10 MB
                </div>
              </>
            )}
          </div>
        </FormField>

        <PrimaryButton onClick={handleSubmit} loading={loading} disabled={loading}>
          Continue to Role Selection &nbsp;→
        </PrimaryButton>
      </div>
    </div>
  );
}
