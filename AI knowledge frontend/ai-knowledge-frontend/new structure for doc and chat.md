src/
│
├── api/
│   ├── authApi.ts
│   ├── axios.ts
│   ├── documentApi.ts
│   └── chatApi.ts              ← NEW
│
├── components/
│   ├── auth/
│   ├── common/
│   │
│   ├── documents/
│   │   ├── DocumentCard.tsx
│   │   ├── DocumentList.tsx
│   │   ├── EmptyState.tsx
│   │   ├── UploadForm.tsx
│   │   ├── UploadZone.tsx
│   │   └── DocumentStatus.tsx  ← NEW
│   │
│   ├── chat/                   ← NEW
│   │   ├── ChatWindow.tsx
│   │   ├── ChatInput.tsx
│   │   ├── MessageBubble.tsx
│   │   └── SourceCard.tsx
│   │
│   ├── layout/
│   └── ui/
│
├── hooks/
│   ├── useAuth.ts
│   ├── useDocuments.ts
│   └── useChat.ts              ← NEW
│
├── pages/
│   ├── auth/
│   ├── DashboardPage.tsx
│   └── DocumentChatPage.tsx    ← NEW
│
├── types/
│   ├── auth.ts
│   ├── document.ts
│   └── chat.ts                 ← NEW