import React, { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSend: (text: string) => void;
  loading?: boolean;
  placeholder?: string;
  disabled?: boolean;
}

export default function ChatInput({ onSend, loading, placeholder, disabled }: ChatInputProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [focused, setFocused] = useState(false);

  useEffect(() => {
    if (!loading && !disabled && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [loading, disabled]);

  /* Auto-resize textarea */
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [text]);

  const submit = () => {
    const t = text.trim();
    if (!t || loading || disabled) return;
    onSend(t);
    setText('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const canSend = text.trim().length > 0 && !loading && !disabled;

  return (
    <div style={{ marginTop: 14 }}>
      {/* Input wrap */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-end',
        gap: 10,
        background: 'var(--surface2)',
        border: `1px solid ${focused ? 'var(--gold)' : 'var(--border)'}`,
        borderRadius: 'var(--radius)',
        padding: '12px 12px 12px 18px',
        transition: 'border-color var(--transition)',
      }}>
        <textarea
          ref={textareaRef}
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          disabled={loading || disabled}
          placeholder={placeholder ?? 'Share your answer here…'}
          rows={1}
          style={{
            flex: 1,
            background: 'none',
            border: 'none',
            outline: 'none',
            resize: 'none',
            fontFamily: 'var(--font-body)',
            fontSize: 14,
            color: 'var(--text)',
            lineHeight: 1.55,
            minHeight: 22,
            maxHeight: 120,
            paddingTop: 4,
          }}
        />

        {/* Send button */}
        <button
          onClick={submit}
          disabled={!canSend}
          style={{
            width: 38, height: 38,
            borderRadius: '50%',
            border: 'none',
            background: canSend ? 'var(--gold)' : 'var(--surface4)',
            color: canSend ? '#0E0E10' : 'var(--text-dim)',
            cursor: canSend ? 'pointer' : 'not-allowed',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: loading ? 13 : 16,
            flexShrink: 0,
            transition: 'all var(--transition)',
            transform: canSend ? 'scale(1)' : 'scale(0.92)',
          }}
          onMouseEnter={e => {
            if (canSend) (e.currentTarget as HTMLButtonElement).style.background = 'var(--gold-light)';
          }}
          onMouseLeave={e => {
            if (canSend) (e.currentTarget as HTMLButtonElement).style.background = 'var(--gold)';
          }}
          title={loading ? 'Processing…' : 'Send (Enter)'}
        >
          {loading
            ? <SpinnerMini />
            : '➤'
          }
        </button>
      </div>

      {/* Hint */}
      <p style={{
        fontFamily: 'var(--font-mono)',
        fontSize: 10,
        color: 'var(--text-dim)',
        textAlign: 'center',
        marginTop: 8,
        letterSpacing: '0.05em',
      }}>
        Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}

function SpinnerMini() {
  return (
    <span style={{
      display: 'inline-block',
      width: 14, height: 14,
      border: '2px solid rgba(0,0,0,0.15)',
      borderTopColor: '#0E0E10',
      borderRadius: '50%',
      animation: 'spin 0.7s linear infinite',
    }} />
  );
}
