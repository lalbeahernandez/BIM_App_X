export function ViewerPlaceholder({ selectedBoq, selectedActivity }: { selectedBoq: string | null; selectedActivity: string | null }) {
  return <section className="panel viewerPanel">
    <div className="panelHeader"><b>BIM Viewer</b><span>ViewerAdapter — demo geometry</span></div>
    <div className="viewerCanvas" aria-label="Demo BIM viewer placeholder">
      <div className="building">
        <div className={selectedBoq?.endsWith('442') ? 'tower highlight' : 'tower'}></div>
        <div className={selectedBoq?.endsWith('441') ? 'slab highlight' : 'slab'}></div>
        <div className="core"></div>
      </div>
      <div className="viewerLegend">Selection: {selectedBoq ?? selectedActivity ?? 'none'}<br/>TODO(PROD): conectar motor BIM real mediante `ViewerAdapter`.</div>
    </div>
  </section>;
}
