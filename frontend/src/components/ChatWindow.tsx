import React, { useEffect, useRef } from 'react';

export interface Message {
  id: string;
  sender: 'ai' | 'user';
  text: string;
  meta?: string;
  isLoading?: boolean;
}

interface ChatWindowProps {
  messages: Message[];
  candidateInitials: string;
}

function TypingDots() {
  return (
    <div style={{ display: 'flex', gap: 4, alignItems: 'center', padding: '2px 0' }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: 6, height: 6,
          borderRadius: '50%',
          background: 'var(--text-muted)',
          animation: `bounce 1.2s ${i * 0.2}s infinite ease-in-out`,
        }} />
      ))}
    </div>
  );
}

function AIAvatar() {
  return (
    <div style={{
      width: 34, height: 34,
      borderRadius: '50%',
      background: 'var(--gold-dim)',
      border: '1px solid var(--border-gold)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 15,
      flexShrink: 0,
    }}>
      🤖
    </div>
  );
}

function UserAvatar({ initials }: { initials: string }) {
  return (
    <div style={{
      width: 34, height: 34,
      borderRadius: '50%',
      background: 'var(--surface4)',
      border: '1px solid var(--border)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'var(--font-display)',
      fontSize: 12,
      fontWeight: 700,
      color: 'var(--text-muted)',
      flexShrink: 0,
    }}>
      {initials}
    </div>
  );
}

export default function ChatWindow({ messages, candidateInitials }: ChatWindowProps) {
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div
      ref={listRef}
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '20px',
        height: 420,
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
      }}
    >
      {messages.length === 0 ? (
        <div style={{
          flex: 1,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexDirection: 'column', gap: 10, textAlign: 'center',
        }}>
          <div style={{ fontSize: 36 }}>👋</div>
          <div style={{ fontSize: 14, color: 'var(--text-dim)' }}>
            Your interview will begin shortly…
          </div>
        </div>
      ) : (
        messages.map(m => (
          <div
            key={m.id}
            style={{
              display: 'flex',
              alignItems: 'flex-end',
              gap: 10,
              maxWidth: '85%',
              alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
              flexDirection: m.sender === 'user' ? 'row-reverse' : 'row',
              animation: 'slideIn 0.3s ease both',
            }}
          >
            {m.sender === 'ai'
              ? <AIAvatar />
              : <UserAvatar initials={candidateInitials} />
            }

            <div>
              {/* Bubble */}
              <div style={{
                padding: '12px 16px',
                borderRadius: 16,
                borderBottomLeftRadius:  m.sender === 'ai'   ? 4 : 16,
                borderBottomRightRadius: m.sender === 'user' ? 4 : 16,
                background: m.sender === 'ai' ? 'var(--surface2)' : 'var(--gold)',
                border: m.sender === 'ai' ? '1px solid var(--border)' : 'none',
                color: m.sender === 'ai' ? 'var(--text)' : '#0E0E10',
                fontSize: 14,
                lineHeight: 1.65,
                whiteSpace: 'pre-wrap',
              }}>
                {m.isLoading ? <TypingDots /> : m.text}
              </div>

              {/* Meta */}
              {m.meta && (
                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 10,
                  color: 'var(--text-dim)',
                  marginTop: 5,
                  paddingLeft: m.sender === 'ai' ? 4 : 0,
                  paddingRight: m.sender === 'user' ? 4 : 0,
                  textAlign: m.sender === 'user' ? 'right' : 'left',
                  letterSpacing: '0.04em',
                }}>
                  {m.meta}
                </div>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
