interface AdapterInfo { description?: string; architecture?: string; isFallbackAdapter?: boolean }
interface Adapter { info?: AdapterInfo; isFallbackAdapter?: boolean }
export function softwareAdapter(adapter: Adapter): boolean {
  return !!(adapter.isFallbackAdapter || adapter.info?.isFallbackAdapter || /swiftshader|llvmpipe|software/i.test(`${adapter.info?.description ?? ''} ${adapter.info?.architecture ?? ''}`));
}
export async function automaticDevice(): Promise<'webgpu' | 'wasm'> {
  const gpu = (navigator as unknown as { gpu?: { requestAdapter(options: { powerPreference: string }): Promise<Adapter | null> } }).gpu;
  if (!gpu) return 'wasm';
  try { const adapter = await gpu.requestAdapter({ powerPreference:'high-performance' }); return adapter && !softwareAdapter(adapter) ? 'webgpu' : 'wasm'; }
  catch { return 'wasm'; }
}
