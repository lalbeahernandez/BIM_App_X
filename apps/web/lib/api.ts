export type BoqRow = { id: string; code: string; description: string; unit: string; quantity: number; rate: number; amount: number };
export type ActivityRow = { id: string; external_id: string | null; name: string; planned_start: string | null; planned_finish: string | null; percent_complete: number };
export type RevisionRow = { id: string; model_id: string; revision_no: number; file_name: string; status: string; ifc_schema?: string | null; error_message?: string | null };
export type WorkAreaData = { boq: BoqRow[]; activities: ActivityRow[]; revisions: RevisionRow[] };

const DEMO_PROJECT = '22222222-2222-2222-2222-222222222222';

export async function fetchWorkArea(): Promise<WorkAreaData> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
  try {
    const response = await fetch(`${base}/v1/projects/${DEMO_PROJECT}/work-area`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`API ${response.status}`);
    return await response.json() as WorkAreaData;
  } catch {
    return {
      boq: [
        { id: '44444444-4444-4444-4444-444444444441', code: '03.10', description: 'RCC Slab', unit: 'm3', quantity: 115.32, rate: 1250, amount: 144150 },
        { id: '44444444-4444-4444-4444-444444444442', code: '03.20', description: 'RCC Column', unit: 'm3', quantity: 24.18, rate: 1250, amount: 30225 }
      ],
      activities: [
        { id: '66666666-6666-6666-6666-666666666661', external_id: 'A100', name: 'First floor columns', planned_start: '2026-08-10', planned_finish: '2026-08-18', percent_complete: 40 },
        { id: '66666666-6666-6666-6666-666666666662', external_id: 'A110', name: 'First floor slab', planned_start: '2026-08-19', planned_finish: '2026-08-30', percent_complete: 15 }
      ],
      revisions: []
    };
  }
}
