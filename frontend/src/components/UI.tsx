import React from 'react';

/* ── Eyebrow label ── */
export function Eyebrow({ children }: { children: React.ReactNode }) {
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 8,
      fontFamily: 'var(--font-mono)',
      fontSize: 11,
      letterSpacing: '0.12em',
      textTransform: 'uppercase' as const,
      color: 'var(--gold)',
      padding: '6px 14px',
      border: '1px solid var(--border-gold)',
      borderRadius: 40,
      background: 'var(--gold-dim)',
      marginBottom: 16,
    }}>
      <span style={{ fontSize: 7 }}>●</span>
      {children}
    </span>
  );
}

/* ── Display heading ── */
export function DisplayHeading({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <h1 style={{
      fontFamily: 'var(--font-display)',
      fontSize: 'clamp(32px, 5vw, 48px)',
      fontWeight: 700,
      lineHeight: 1.1,
      color: 'var(--text)',
      marginBottom: 14,
      ...style,
    }}>
      {children}
    </h1>
  );
}

/* ── Section heading ── */
export function SectionHeading({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <h2 style={{
      fontFamily: 'var(--font-display)',
      fontSize: 30,
      fontWeight: 700,
      color: 'var(--text)',
      marginBottom: 6,
      ...style,
    }}>
      {children}
    </h2>
  );
}

/* ── Muted paragraph ── */
export function Muted({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <p style={{ fontSize: 14, color: 'var(--text-muted)', lineHeight: 1.7, ...style }}>
      {children}
    </p>
  );
}

/* ── Card surface ── */
export function Card({
  children,
  style,
  gold,
}: {
  children: React.ReactNode;
  style?: React.CSSProperties;
  gold?: boolean;
}) {
  return (
    <div style={{
      background: 'var(--surface2)',
      border: `1px solid ${gold ? 'var(--border-gold)' : 'var(--border)'}`,
      borderRadius: 'var(--radius)',
      padding: '20px 24px',
      ...style,
    }}>
      {children}
    </div>
  );
}

/* ── Primary button ── */
export function PrimaryButton({
  children,
  onClick,
  disabled,
  loading,
  style,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  style?: React.CSSProperties;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 8,
        width: '100%',
        padding: '14px 28px',
        fontFamily: 'var(--font-body)',
        fontSize: 14,
        fontWeight: 500,
        letterSpacing: '0.02em',
        color: '#0E0E10',
        background: disabled || loading ? 'var(--surface4)' : 'var(--gold)',
        border: 'none',
        borderRadius: 'var(--radius-sm)',
        cursor: disabled || loading ? 'not-allowed' : 'pointer',
        transition: 'all var(--transition)',
        opacity: disabled || loading ? 0.5 : 1,
        ...style,
      }}
      onMouseEnter={e => {
        if (!disabled && !loading) (e.currentTarget as HTMLButtonElement).style.background = 'var(--gold-light)';
      }}
      onMouseLeave={e => {
        if (!disabled && !loading) (e.currentTarget as HTMLButtonElement).style.background = 'var(--gold)';
      }}
    >
      {loading ? <LoadingSpinner /> : children}
    </button>
  );
}

/* ── Ghost button ── */
export function GhostButton({
  children,
  onClick,
  style,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  style?: React.CSSProperties;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 8,
        padding: '14px 20px',
        fontFamily: 'var(--font-body)',
        fontSize: 14,
        fontWeight: 500,
        color: 'var(--text-muted)',
        background: 'var(--surface2)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-sm)',
        cursor: 'pointer',
        transition: 'all var(--transition)',
        ...style,
      }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLButtonElement).style.color = 'var(--text)';
        (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border-md)';
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-muted)';
        (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border)';
      }}
    >
      {children}
    </button>
  );
}

/* ── Form field ── */
export function FormField({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        fontSize: 11,
        fontWeight: 500,
        letterSpacing: '0.09em',
        textTransform: 'uppercase' as const,
        color: 'var(--text-muted)',
        marginBottom: 10,
        fontFamily: 'var(--font-mono)',
      }}>
        <span style={{
          width: 6, height: 6,
          borderRadius: '50%',
          background: required ? 'var(--gold)' : 'var(--text-dim)',
          flexShrink: 0,
        }} />
        {label}
        {required && <span style={{ color: 'var(--gold)', marginLeft: -4 }}>*</span>}
      </div>
      {children}
    </div>
  );
}

/* ── Text input ── */
export function TextInput({
  value,
  onChange,
  placeholder,
  type = 'text',
  disabled,
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
  disabled?: boolean;
}) {
  const [focused, setFocused] = React.useState(false);
  return (
    <input
      type={type}
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={{
        width: '100%',
        background: focused ? 'var(--surface3)' : 'var(--surface2)',
        border: `1px solid ${focused ? 'var(--gold)' : 'var(--border)'}`,
        borderRadius: 'var(--radius-sm)',
        padding: '13px 18px',
        fontFamily: 'var(--font-body)',
        fontSize: 15,
        color: 'var(--text)',
        outline: 'none',
        transition: 'all var(--transition)',
      }}
    />
  );
}

/* ── Error bar ── */
export function ErrorBar({ message }: { message: string }) {
  if (!message) return null;
  return (
    <div style={{
      padding: '12px 16px',
      background: 'var(--red-dim)',
      border: '1px solid var(--red-border)',
      borderRadius: 'var(--radius-sm)',
      color: 'var(--red)',
      fontSize: 13,
      marginBottom: 16,
      animation: 'slideIn 0.25s ease',
    }}>
      ⚠ {message}
    </div>
  );
}

/* ── Spinner ── */
export function LoadingSpinner() {
  return (
    <span style={{
      display: 'inline-block',
      width: 16,
      height: 16,
      border: '2px solid rgba(0,0,0,0.2)',
      borderTopColor: '#0E0E10',
      borderRadius: '50%',
      animation: 'spin 0.7s linear infinite',
    }} />
  );
}

/* Spin keyframe injected once */
if (typeof document !== 'undefined') {
  const id = '__spin_kf__';
  if (!document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = '@keyframes spin{to{transform:rotate(360deg)}}';
    document.head.appendChild(s);
  }
}
