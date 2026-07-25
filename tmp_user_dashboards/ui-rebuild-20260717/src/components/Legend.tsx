export default function Legend() {
  return (
    <div className="legend" aria-label="Graph legend">
      <span className="chip chip-concept">concept</span>
      <span className="chip chip-code">code</span>
      <span className="chip chip-impl">implements</span>
      <span className="chip chip-prereq">prereq / builds-on</span>
    </div>
  );
}
