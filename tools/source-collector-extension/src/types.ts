export type Status = 'queued' | 'fetching' | 'model' | 'transcribing' | 'success' | 'error' | 'cancelled';
export interface Cue { start: number; end: number; text: string }
export interface Video {
  bvid: string; cid: number; aid: number; page: number; pages: number;
  title: string; author: string; duration: number; url: string;
}
export interface Job {
  id: string; bvid: string; page: number; status: Status; progress: number; detail: string;
  createdAt: string; collectedAt?: string; video?: Video; error?: string;
  source?: 'platform' | 'local-asr'; track?: string; model?: string; device?: string;
  cueCount?: number; subtitleStart?: number; subtitleEnd?: number; warning?: string;
}
export const MODELS = ['Xenova/whisper-small', 'Xenova/whisper-base', 'Xenova/whisper-tiny'] as const;
export interface Settings { model: typeof MODELS[number]; device: 'auto' | 'webgpu' | 'wasm' }
export interface State { jobs: Job[]; running: boolean; settings: Settings }
export const DEFAULT_STATE: State = { jobs: [], running: false, settings: { model: MODELS[0], device: 'wasm' } };
export const ACTIVE: Status[] = ['fetching', 'model', 'transcribing'];
export type Command =
  | { action: 'get' | 'start' | 'pause' | 'retry-all' | 'clear-finished' | 'clear-cache' | 'current' }
  | { action: 'add'; input: string }
  | { action: 'settings'; settings: Settings }
  | { action: 'retry' | 'cancel' | 'remove'; id: string };
export type Response = { ok: true; state?: State; added?: number; invalid?: string[]; duplicates?: number; message?: string } | { ok: false; error: string };
