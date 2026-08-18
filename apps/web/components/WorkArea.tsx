'use client';

import { useEffect, useMemo, useState } from 'react';
import { ActivityRow, BoqRow, WorkAreaData, fetchWorkArea } from '../lib/api';
import { ViewerPlaceholder } from './ViewerPlaceholder';

export function WorkArea() {
  const [data, setData] = useState<WorkAreaData>({ boq: [], activities: [], revisions: [] });
  const [selectedBoq, setSelectedBoq] = useState<string | null>(null);
  const [selectedActivity, setSelectedActivity] = useState<string | null>(null);

  useEffect(() => { void fetchWorkArea().then(setData); }, []);
  const total = useMemo(() => data.boq.reduce((sum, row) => sum + row.amount, 0), [data.boq]);

  const chooseBoq = (row: BoqRow) => {
    setSelectedBoq(row.id);
    if (row.code === '03.10') setSelectedActivity('66666666-6666-6666-6666-666666666662');
    if (row.code === '03.20') setSelectedActivity('66666666-6666-6666-6666-666666666661');
  };
  const chooseActivity = (row: ActivityRow) => {
    setSelectedActivity(row.id);
    if (row.external_id === 'A100') setSelectedBoq('44444444-4444-4444-4444-444444444442');
    if (row.external_id === 'A110') setSelectedBoq('44444444-4444-4444-4444-444444444441');
  };

  return <main>
    <header className="topbar">
      <div><strong>BIM CONTROL X</strong><span className="badge">Active Project</span></div>
      <nav>Dashboard · <b>Work Area</b> · 4D · BOQ · Progress · QA/QC · IDS · GIS · Admin</nav>
    </header>
    <section className="workspace">
      <ViewerPlaceholder selectedBoq={selectedBoq} selectedActivity={selectedActivity} />
      <section className="panel boqPanel">
        <div className="panelHeader"><b>Bill of Quantities / 5D</b><span>€ {total.toLocaleString('es-ES')}</span></div>
        <table><thead><tr><th>Item</th><th>Description</th><th>Qty</th><th>Unit</th><th>Rate</th><th>Amount</th></tr></thead>
          <tbody>{data.boq.map(row => <tr key={row.id} onClick={() => chooseBoq(row)} className={selectedBoq === row.id ? 'selected' : ''}>
            <td>{row.code}</td><td>{row.description}</td><td>{row.quantity}</td><td>{row.unit}</td><td>{row.rate}</td><td>{row.amount.toLocaleString('es-ES')}</td>
          </tr>)}</tbody>
        </table>
      </section>
      <section className="panel schedulePanel">
        <div className="panelHeader"><b>4D Construction Schedule</b><span>Baseline / Data date / Scenario ready</span></div>
        <div className="ganttGrid">
          <div className="activityList">{data.activities.map(row => <button key={row.id} onClick={() => chooseActivity(row)} className={selectedActivity === row.id ? 'selected activity' : 'activity'}>
            <span>{row.external_id}</span><b>{row.name}</b><span>{row.percent_complete}%</span>
          </button>)}</div>
          <div className="timeline">{data.activities.map((row, index) => <div key={row.id} className="timelineRow"><div className="bar" style={{ marginLeft: `${index * 18 + 8}%`, width: '34%' }}>{row.name}</div></div>)}</div>
        </div>
      </section>
    </section>
  </main>;
}
