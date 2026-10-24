import type { Cue } from './types';
const dbPromise = () => new Promise<IDBDatabase>((resolve, reject) => {
  const req = indexedDB.open('beannote-sources', 1);
  req.onupgradeneeded = () => req.result.createObjectStore('subtitles');
  req.onsuccess = () => resolve(req.result); req.onerror = () => reject(req.error);
});
async function operation<T>(mode: IDBTransactionMode, fn: (store: IDBObjectStore) => IDBRequest<T>): Promise<T> {
  const db = await dbPromise();
  try {
    return await new Promise<T>((resolve, reject) => {
      const tx = db.transaction('subtitles', mode); const req = fn(tx.objectStore('subtitles'));
      tx.oncomplete = () => resolve(req.result); tx.onerror = () => reject(tx.error); tx.onabort = () => reject(tx.error ?? new Error('本地存储事务被中断'));
    });
  } finally { db.close(); }
}
export const saveCues = (id: string, cues: Cue[]) => operation('readwrite', s => s.put(cues, id));
export const loadCues = (id: string): Promise<Cue[] | undefined> => operation('readonly', s => s.get(id));
export const deleteCues = (id: string) => operation('readwrite', s => s.delete(id));
