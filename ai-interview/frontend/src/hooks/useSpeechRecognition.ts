import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

type SpeechRecognitionConstructor = new () => SpeechRecognition;

interface SpeechRecognitionEventResult {
  readonly isFinal: boolean;
  readonly 0: { readonly transcript: string };
}

interface SpeechRecognitionEventLike extends Event {
  readonly resultIndex: number;
  readonly results: ArrayLike<SpeechRecognitionEventResult>;
}

interface SpeechRecognitionErrorEventLike extends Event {
  readonly error: string;
}

interface SpeechRecognition extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEventLike) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
}

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

export function useSpeechRecognition(onText: (text: string) => void) {
  const Recognition = typeof window !== 'undefined' ? window.SpeechRecognition || window.webkitSpeechRecognition : undefined;
  const supported = Boolean(Recognition);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const finalTextRef = useRef('');
  const [listening, setListening] = useState(false);
  const [interimText, setInterimText] = useState('');
  const [error, setError] = useState<string | null>(null);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    setListening(false);
  }, []);

  const start = useCallback(() => {
    if (!Recognition) {
      setError('当前浏览器不支持语音识别，请使用 Chrome 或 Edge。');
      return;
    }
    setError(null);
    setInterimText('');
    finalTextRef.current = '';
    const recognition = new Recognition();
    recognition.lang = 'zh-CN';
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = (event) => {
      let interim = '';
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        const text = result[0].transcript;
        if (result.isFinal) {
          finalTextRef.current += text;
          onText(finalTextRef.current.trim());
        } else {
          interim += text;
        }
      }
      setInterimText(interim);
    };
    recognition.onerror = (event) => {
      setError(`语音识别失败：${event.error}`);
      setListening(false);
    };
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
  }, [Recognition, onText]);

  const reset = useCallback(() => {
    finalTextRef.current = '';
    setInterimText('');
    setError(null);
  }, []);

  useEffect(() => () => recognitionRef.current?.abort(), []);

  return useMemo(
    () => ({ supported, listening, interimText, error, start, stop, reset }),
    [error, interimText, listening, reset, start, stop, supported]
  );
}
