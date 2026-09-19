import React, { useState } from 'react';
import { Upload, FileText, AlertCircle, Send, Trash2 } from 'lucide-react';
import './resumeupload.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

const ResumeUpload = () => {
  const [file, setFile] = useState(null);
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(selectedFile.type)) {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError('Please select a PDF or DOCX resume.');
    }
  };

  const uploadResume = async (e) => {
    e.preventDefault();
    if (!file) return;
    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('resume', file);

    try {
      const response = await fetch(API_BASE + '/rag/upload/', { method: 'POST', body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Resume indexing failed.');
      setSession(data);
      setMessages([]);
    } catch (err) {
      setError(err.message);
      setSession(null);
    } finally {
      setIsUploading(false);
    }
  };

  const askQuestion = async (e) => {
    e.preventDefault();
    const text = question.trim();
    if (!text || !session || isAsking) return;

    setQuestion('');
    setIsAsking(true);
    setError(null);
    setMessages((current) => [...current, { role: 'user', content: text }]);

    try {
      const response = await fetch(API_BASE + '/rag/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: session.session_id, question: text }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Could not generate an answer.');

      setMessages((current) => [
        ...current,
        { role: 'assistant', content: data.answer, sources: data.sources || [] },
      ]);
    } catch (err) {
      setError(err.message);
      setMessages((current) => current.filter((message, index) =>
        !(index === current.length - 1 && message.role === 'user' && message.content === text)
      ));
    } finally {
      setIsAsking(false);
    }
  };

  const resetSession = async () => {
    if (session && session.session_id) {
      await fetch(API_BASE + '/rag/session/' + session.session_id + '/', { method: 'DELETE' }).catch(() => {});
    }
    setSession(null);
    setMessages([]);
    setFile(null);
    setQuestion('');
    setError(null);
  };

  return (
    <div className="resume-upload-container">
      <h2 className="title">Resume RAG Chatbot</h2>

      {!session ? (
        <form onSubmit={uploadResume} className="upload-form">
          <div className="dropzone">
            <label htmlFor="dropzone-file" className="dropzone-label">
              <Upload className="upload-icon" />
              <p><span className="bold">Click to upload</span> a resume</p>
              <p className="file-types">PDF or DOCX · max 10 MB</p>
            </label>
            <input id="dropzone-file" type="file" className="file-input" onChange={handleFileChange} accept=".pdf,.docx" />
          </div>

          {file && (
            <div className="file-info">
              <FileText className="file-icon" />
              <span>{file.name}</span>
            </div>
          )}

          <button type="submit" disabled={!file || isUploading} className={'submit-button ' + ((!file || isUploading) ? 'disabled' : '')}>
            {isUploading ? 'Indexing resume...' : 'Upload & Start Chat'}
          </button>
        </form>
      ) : (
        <>
          <div className="session-header">
            <div>
              <strong>{session.filename}</strong>
              <div className="file-types">{session.chunks_indexed} chunks indexed</div>
            </div>
            <button className="reset-button" onClick={resetSession} title="Delete session">
              <Trash2 size={17} />
            </button>
          </div>

          <div className="chat-window">
            {messages.length === 0 && (
              <div className="empty-chat">
                Ask something about the candidate, e.g. “What ML experience does this candidate have?”
              </div>
            )}

            {messages.map((message, index) => (
              <div key={index} className={'message ' + message.role}>
                <strong>{message.role === 'user' ? 'You' : 'Assistant'}</strong>
                <p>{message.content}</p>
                {message.sources && message.sources.length > 0 && (
                  <details className="sources">
                    <summary>Retrieved resume chunks</summary>
                    {message.sources.map((source, sourceIndex) => (
                      <div key={sourceIndex} className="source">
                        <small>Similarity: {source.score}</small>
                        <p>{source.text}</p>
                      </div>
                    ))}
                  </details>
                )}
              </div>
            ))}
          </div>

          <form onSubmit={askQuestion} className="chat-form">
            <input value={question} onChange={(e) => setQuestion(e.target.value)}
              placeholder={isAsking ? 'Generating answer...' : 'Ask about the candidate...'} disabled={isAsking} />
            <button type="submit" disabled={!question.trim() || isAsking} className="send-button">
              <Send size={18} />
            </button>
          </form>
        </>
      )}

      {error && (
        <div className="alert error">
          <AlertCircle className="alert-icon" />
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;
